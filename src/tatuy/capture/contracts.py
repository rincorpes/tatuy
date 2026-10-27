"""Capture capability contracts shared by enabled and disabled implementations."""

from __future__ import annotations

from typing import Protocol

from tatuy.capture.settings import CaptureSettings


class CaptureCapability(Protocol):
    """Runtime-facing screenshot/video capture capability used by the engine."""

    @property
    def enabled(self) -> bool:
        """Whether media capture functionality is available."""

    @property
    def settings(self) -> CaptureSettings:
        """Return capture settings used by runtime input handling."""

    @property
    def video_recording(self) -> bool:
        """Whether video recording is active."""

    @property
    def video_busy(self) -> bool:
        """Whether video capture/encoding is busy."""

    def request_screenshot(self, label: str | None = None) -> str:
        """Queue a screenshot request and return its target path."""

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
