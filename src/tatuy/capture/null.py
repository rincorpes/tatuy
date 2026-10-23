"""Disabled capture capability used when capture is configured off."""

from __future__ import annotations

from tatuy.capture.replay_frame import ReplayFrame
from tatuy.capture.replay_header import ReplayHeader
from tatuy.capture.settings import CaptureSettings
from tatuy.input.frame import InputFrame


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
    def replay_recording(self) -> bool:
        """Report that replay recording is inactive."""
        return False

    @property
    def replay_playing(self) -> bool:
        """Report that replay playback is inactive."""
        return False

    @property
    def replay_header(self) -> ReplayHeader | None:
        """Return no replay header because playback is unavailable."""
        return None

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

    def start_replay_record(
        self,
        *,
        filename: str,
        header: ReplayHeader,
    ) -> None:
        """Reject direct replay-record requests while capture is disabled."""
        del filename, header
        raise RuntimeError("Capture is disabled")

    def stop_replay_record(self) -> None:
        """Ignore replay-record stop requests."""

    def record_input(self, frame: InputFrame, dt: float) -> None:
        """Ignore input frames because replay recording is disabled."""
        del frame, dt

    def start_replay_play(self, filename: str) -> ReplayHeader:
        """Reject direct replay-play requests while capture is disabled."""
        del filename
        raise RuntimeError("Capture is disabled")

    def next_replay_frame(self) -> ReplayFrame | None:
        """Return no replay frame because playback is disabled."""
        return None

    def stop_replay_play(self) -> None:
        """Ignore replay-play stop requests."""

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
