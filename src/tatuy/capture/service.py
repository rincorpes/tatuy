from __future__ import annotations

from pathlib import Path
from queue import Empty, SimpleQueue
from uuid import uuid4

from tatuy.backend.backend import Backend
from tatuy.capture import events
from tatuy.capture.models import (
    CaptureJob,
    CaptureResult,
    ScreenshotRequest,
    WorkerConfig,
)
from tatuy.capture.paths import CaptureDirectories, CapturePathBuilder
from tatuy.capture.replay import (
    ReplayPlayer,
    ReplayRecorder,
    ReplayRecorderConfig,
)
from tatuy.capture.replay_frame import ReplayFrame
from tatuy.capture.replay_header import ReplayHeader
from tatuy.capture.settings import CaptureSettings
from tatuy.capture.video import VideoRecorder
from tatuy.capture.worker import CaptureWorker
from tatuy.events.bus import event_bus
from tatuy.input.frame import InputFrame


class CaptureService:
    def __init__(
        self, backend: Backend, settings: CaptureSettings | None = None
    ):
        self._backend = backend
        self.settings = settings or CaptureSettings()
        self.directories = CaptureDirectories(self.settings)

        self._capture_results: SimpleQueue[CaptureResult] = SimpleQueue()
        self._screenshot_requests: list[ScreenshotRequest] = []

        self.screenshot_paths = CapturePathBuilder(
            directory=self.directories.screenshots,
            ext="png",
        )

        self.worker = CaptureWorker(
            WorkerConfig(
                queue_size=self.settings.worker_queue_size,
                on_done=self._capture_results.put,
                delete_temp=True,
            )
        )
        self.worker.start()

        self.video = VideoRecorder(
            self.settings,
            self.worker,
            recordings_dir=self.directories.recordings,
        )

        self.replay_recorder = ReplayRecorder()
        self.replay_player = ReplayPlayer()
        self.replay_header: ReplayHeader | None = None
        self._replay_finished = False

    def request_screenshot(self, label: str | None = None) -> str:
        label = label or "shot"
        path = self.screenshot_paths.build(label)

        self._screenshot_requests.append(
            ScreenshotRequest(
                job_id=f"screenshot:{uuid4().hex}",
                out_path=path,
                label=label,
            )
        )

        return str(path)

    @property
    def replay_recording(self) -> bool:
        return self.replay_recorder.active

    @property
    def replay_playing(self) -> bool:
        # A completed replay remains visible until explicitly stopped.
        return self.replay_player.active or self._replay_finished

    def start_replay_record(
        self,
        *,
        filename: str,
        header: ReplayHeader,
    ) -> None:
        if self.replay_recording or self.replay_playing:
            raise RuntimeError("A replay session is already active")

        path = self.directories.replays / filename

        self.replay_recorder.start(
            ReplayRecorderConfig(path=path, header=header)
        )

        self.replay_header = header

        event_bus.emit(events.REPLAY_RECORD_STARTED, path=str(path))

    def stop_replay_record(self) -> None:
        if not self.replay_recording:
            return

        path = self.replay_recorder.path
        self.replay_recorder.stop()
        self.replay_header = None

        event_bus.emit(
            events.REPLAY_RECORD_STOPPED,
            path=str(path) if path is not None else None,
        )

    def record_input(self, frame: InputFrame, dt: float) -> None:
        self.replay_recorder.record(frame, dt)

    def start_replay_play(self, filename: str) -> ReplayHeader:
        if self.replay_recording or self.replay_playing:
            raise RuntimeError("A replay session is already active")

        path = self.directories.replays / filename
        header = self.replay_player.start(path)

        self.replay_header = header
        self._replay_finished = False

        event_bus.emit(events.REPLAY_PLAY_STARTED, path=str(path))

        return header

    def next_replay_frame(self) -> ReplayFrame | None:
        if self._replay_finished:
            return None

        frame = self.replay_player.next()

        if frame is None:
            self._replay_finished = True
            event_bus.emit(events.REPLAY_PLAY_FINISHED)

        return frame

    def stop_replay_play(self) -> None:
        was_playing = self.replay_playing

        self.replay_player.stop()
        self._replay_finished = False

        if was_playing:
            self.replay_header = None
            event_bus.emit(events.REPLAY_PLAY_STOPPED)

    def after_render(self) -> None:
        requests = self._screenshot_requests
        self._screenshot_requests = []

        wants_video = self.video.capture_due()

        if not requests and not wants_video:
            return

        # Backend access remains on the engine thread.
        width, height, pixels = self._backend.capture.argb8888_bytes()

        # Immutable bytes can be shared by screenshot and video jobs.
        for request in requests:
            queued = self.worker.enqueue(
                CaptureJob(
                    job_id=request.job_id,
                    out_path=request.out_path,
                    w=width,
                    h=height,
                    pixels=pixels,
                    fmt="BGRA",
                )
            )

            event_bus.emit(
                (
                    events.SCREENSHOT_QUEUED
                    if queued
                    else events.SCREENSHOT_FAILED
                ),
                job_id=request.job_id,
                path=str(request.out_path),
                label=request.label,
                **({} if queued else {"error": "Capture queue is full"}),
            )

        if wants_video:
            self.video.capture(
                width=width,
                height=height,
                pixels=pixels,
            )

    @property
    def video_recording(self) -> bool:
        return self.video.active

    @property
    def video_busy(self) -> bool:
        return self.video.busy

    def start_video_record(self, label: str = "capture") -> None:
        if self.video_busy:
            return

        path = self.video.start(label)

        print(f"Video recording started: {path}")
        event_bus.emit(events.VIDEO_STARTED, path=str(path))

    def stop_video_record(self) -> None:
        path = self.video.stop()

        if path is None:
            return

        print(f"Video recording stopped; encoding: {path}")

        event_bus.emit(events.VIDEO_STOPPED, path=str(path))
        event_bus.emit(events.VIDEO_FINALIZING, path=str(path))

    def poll(self) -> None:
        while True:
            try:
                result = self._capture_results.get_nowait()
            except Empty:
                break

            if result.job_id.startswith("screenshot:"):
                event_bus.emit(
                    (
                        events.SCREENSHOT_DONE
                        if result.ok
                        else events.SCREENSHOT_FAILED
                    ),
                    job_id=result.job_id,
                    path=str(result.out_path),
                    error=result.error,
                )

            elif not result.ok:
                print(f"Video frame failed: {result.error}")

        encoded = self.video.poll()

        if encoded is not None:
            if encoded.ok:
                print(f"Video saved: {encoded.output_path}")
            else:
                print(f"Video encoding failed: {encoded.error}")

            event_bus.emit(
                (
                    events.VIDEO_ENCODE_DONE
                    if encoded.ok
                    else events.VIDEO_ENCODE_FAILED
                ),
                path=str(encoded.output_path),
                error=encoded.error,
            )

    def close(self) -> None:
        self.stop_replay_record()
        self.stop_replay_play()
        self.stop_video_record()

        # Finish video encoding while the image worker is still available.
        self.video.close()

        # BaseWorker.stop() does not drain its queue itself.
        self.worker.wait_until_idle()

        try:
            self.poll()
        finally:
            self.worker.stop()
