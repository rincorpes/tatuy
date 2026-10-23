"""Capture capability contracts shared by enabled and disabled implementations."""

from __future__ import annotations

from typing import Protocol

from tatuy.capture.replay_frame import ReplayFrame
from tatuy.capture.replay_header import ReplayHeader
from tatuy.capture.settings import CaptureSettings
from tatuy.input.frame import InputFrame


class CaptureCapability(Protocol):
    """Runtime-facing capture/replay capability used by the engine."""

    @property
    def enabled(self) -> bool:
        """Whether capture/replay functionality is available."""

    @property
    def settings(self) -> CaptureSettings:
        """Return capture settings used by runtime input handling."""

    @property
    def replay_recording(self) -> bool:
        """Whether replay recording is active."""

    @property
    def replay_playing(self) -> bool:
        """Whether replay playback is active."""

    @property
    def replay_header(self) -> ReplayHeader | None:
        """Return the active replay header when one exists."""

    @property
    def video_recording(self) -> bool:
        """Whether video recording is active."""

    @property
    def video_busy(self) -> bool:
        """Whether video capture/encoding is busy."""

    def request_screenshot(self, label: str | None = None) -> str:
        """Queue a screenshot request and return its target path."""

    def start_replay_record(
        self,
        *,
        filename: str,
        header: ReplayHeader,
    ) -> None:
        """Start recording replay input."""

    def stop_replay_record(self) -> None:
        """Stop replay recording."""

    def record_input(self, frame: InputFrame, dt: float) -> None:
        """Record one input frame when replay recording is active."""

    def start_replay_play(self, filename: str) -> ReplayHeader:
        """Start replay playback and return its header."""

    def next_replay_frame(self) -> ReplayFrame | None:
        """Return the next replay frame when playback is active."""

    def stop_replay_play(self) -> None:
        """Stop replay playback."""

    def after_render(self) -> None:
        """Process capture work after frame content is rendered."""

    def start_video_record(self, label: str = "capture") -> None:
        """Start video recording."""

    def stop_video_record(self) -> None:
        """Stop video recording."""

    def poll(self) -> None:
        """Poll asynchronous capture work."""

    def close(self) -> None:
        """Release capture resources."""
