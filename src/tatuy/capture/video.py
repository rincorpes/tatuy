from __future__ import annotations

import json
import re
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from time import perf_counter
from typing import Literal
from uuid import uuid4

from tatuy.capture.models import CaptureJob
from tatuy.capture.settings import CaptureSettings
from tatuy.capture.video_encoder import EncodeResult, VideoEncoder, VideoFrame
from tatuy.capture.worker import CaptureWorker


@dataclass
class VideoSession:
    run_id: str
    label: str
    base_dir: Path

    state: Literal["recording", "finalizing", "done", "failed"] = "recording"

    frames: list[VideoFrame] = field(default_factory=list)
    size: tuple[int, int] | None = None
    queue_drops: int = 0
    error: str | None = None


@dataclass(frozen=True)
class FinalizeJob:
    run_id: str
    label: str
    base_dir: Path
    frames: tuple[VideoFrame, ...]
    duration: float
    queue_drops: int


class VideoRecorder:
    def __init__(
        self,
        settings: CaptureSettings,
        worker: CaptureWorker,
        *,
        recordings_dir: Path,
    ) -> None:
        self._settings = settings
        self._worker = worker
        self._encoder = VideoEncoder()

        self._executor = ThreadPoolExecutor(
            max_workers=1,
            thread_name_prefix="video-finalize",
        )

        self._future: Future[EncodeResult] | None = None
        self._started_at = 0.0
        self._next_capture_at = 0.0

        self.session: VideoSession | None = None

        self._recordings_dir = recordings_dir

    @property
    def active(self) -> bool:
        return self.session is not None and self.session.state == "recording"

    @property
    def busy(self) -> bool:
        return self.active or self._future is not None

    def start(self, label: str) -> Path:
        if self.busy:
            raise RuntimeError("Video capture is already busy")

        run_id = uuid4().hex
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        slug = re.sub(r"[^a-z0-9_-]+", "-", label.lower())
        slug = slug.strip("-") or "capture"

        base_dir = self._recordings_dir / f"{stamp}_{slug}_{run_id[:8]}"

        (base_dir / "frames").mkdir(parents=True)

        self.session = VideoSession(
            run_id=run_id,
            label=label,
            base_dir=base_dir,
        )

        self._started_at = perf_counter()
        self._next_capture_at = 0.0

        return base_dir

    def capture_due(self) -> bool:
        return (
            self.active
            and perf_counter() - self._started_at >= self._next_capture_at
        )

    def capture(
        self,
        *,
        width: int,
        height: int,
        pixels: bytes,
    ) -> None:
        if not self.capture_due():
            return

        session = self.session
        assert session is not None

        timestamp = perf_counter() - self._started_at

        self._next_capture_at = timestamp + 1.0 / self._settings.capture_fps

        index = len(session.frames)
        path = session.base_dir / "frames" / f"frame_{index:08d}.png"

        target_size = session.size or (width, height)

        queued = self._worker.enqueue(
            CaptureJob(
                job_id=f"video:{session.run_id}:{index}",
                out_path=path,
                w=width,
                h=height,
                pixels=pixels,
                fmt="BGRA",
                target_size=target_size,
            )
        )

        if not queued:
            session.queue_drops += 1
            return

        session.size = target_size
        session.frames.append(VideoFrame(path=path, timestamp=timestamp))

    def stop(self) -> Path | None:
        if not self.active:
            return None

        session = self.session
        assert session is not None

        duration = perf_counter() - self._started_at
        session.state = "finalizing"

        job = FinalizeJob(
            run_id=session.run_id,
            label=session.label,
            base_dir=session.base_dir,
            frames=tuple(session.frames),
            duration=duration,
            queue_drops=session.queue_drops,
        )

        self._future = self._executor.submit(
            self._finalize,
            job,
        )

        return session.base_dir

    def _finalize(self, job: FinalizeJob) -> EncodeResult:
        # Wait in the background until PNG saving has completed.
        self._worker.wait_until_idle()

        saved = tuple(frame for frame in job.frames if frame.path.is_file())

        manifest = {
            "run_id": job.run_id,
            "label": job.label,
            "duration": job.duration,
            "video_fps": self._settings.video_fps,
            "capture_fps": self._settings.capture_fps,
            "queue_drops": job.queue_drops,
            "frames": [
                {
                    "file": frame.path.relative_to(job.base_dir).as_posix(),
                    "timestamp": frame.timestamp,
                    "saved": frame.path.is_file(),
                }
                for frame in job.frames
            ],
        }

        (job.base_dir / "manifest.json").write_text(
            json.dumps(manifest, indent=2),
            encoding="utf-8",
        )

        result = self._encoder.encode(
            base_dir=job.base_dir,
            frames=saved,
            duration=job.duration,
            settings=self._settings,
        )

        if result.ok and not self._settings.keep_frames:
            for frame in saved:
                try:
                    frame.path.unlink(missing_ok=True)
                except OSError:
                    pass

        return result

    def poll(self) -> EncodeResult | None:
        if self._future is None or not self._future.done():
            return None

        future = self._future
        self._future = None

        session = self.session
        assert session is not None

        try:
            result = future.result()
        except Exception as exc:
            result = EncodeResult(
                ok=False,
                output_path=session.base_dir / "video.mp4",
                error=str(exc),
            )

        session.state = "done" if result.ok else "failed"
        session.error = result.error

        return result

    def close(self) -> None:
        self.stop()
        self._executor.shutdown(wait=True)
