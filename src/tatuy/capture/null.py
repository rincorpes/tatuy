"""Disabled capture capability used when capture is configured off."""

from __future__ import annotations

from tatuy.capture.settings import CaptureSettings


class NullCaptureService:
    """No-op capture implementation that preserves the runtime contract."""

    def __init__(self) -> None:
        self._settings = CaptureSettings(hotkeys_enabled=False)

    @property
    def enabled(self) -> bool:
        """Report that capture functionality is unavailable."""
        return False

    @property
    def settings(self) -> CaptureSettings:
        """Return inert settings with capture hotkeys disabled."""
        return self._settings

    @property
    def video_recording(self) -> bool:
        """Report that video recording is inactive."""
        return False

    @property
    def video_busy(self) -> bool:
        """Report that no video capture work is pending."""
        return False

    def request_screenshot(self, label: str | None = None) -> str:
        """Reject direct screenshot requests while capture is disabled."""
        del label
        raise RuntimeError("Capture is disabled")

    def after_render(self) -> None:
        """Perform no post-render capture work."""

    def start_video_record(self, label: str = "capture") -> None:
        """Reject direct video-record requests while capture is disabled."""
        del label
        raise RuntimeError("Capture is disabled")

    def stop_video_record(self) -> None:
        """Ignore video-record stop requests."""

    def poll(self) -> None:
        """Perform no asynchronous capture polling."""

    def close(self) -> None:
        """Release no resources because none were acquired."""
