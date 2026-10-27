from __future__ import annotations

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
from tatuy.capture.settings import CaptureSettings
from tatuy.capture.video import VideoRecorder
from tatuy.capture.worker import CaptureWorker
from tatuy.events.bus import event_bus


class CaptureService:
    @property
    def enabled(self) -> bool:
        """Whether capture/replay functionality is available."""
        return True

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
            ext=self.settings.screenshot_format,
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

    def after_render(self) -> None:
        requests = self._screenshot_requests
        self._screenshot_requests = []

        wants_video = self.video.capture_due()

        if not requests and not wants_video:
            return

        # Backend access remains on the engine thread.
        width, height, pixels = self._backend.capture.bgra8888_bytes()

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
                    image_format=self.settings.screenshot_format.upper(),
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
        self.stop_video_record()

        # Finish video encoding while the image worker is still available.
        self.video.close()

        # BaseWorker.stop() does not drain its queue itself.
        self.worker.wait_until_idle()

        try:
            self.poll()
        finally:
            self.worker.stop()
