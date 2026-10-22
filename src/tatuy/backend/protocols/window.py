"""Contract for window state, explicit resizing, and native size observation."""

from __future__ import annotations

from typing import Protocol

from tatuy.backend.config import WindowConfig
from tatuy.geometry.size import Size
from tatuy.math.vec2 import Vec2


class Window(Protocol):
    """Expose portable window state and separate resize requests from observations.

    Attributes:
        config (WindowConfig): Read-only settings for this capability.
        position (Vec2): Observed window position in screen coordinates.
        minimized (bool): Whether the window is minimized.
        maximized (bool): Whether the window is maximized.
        close_requested (bool): Whether a window close was requested.
    """

    @property
    def config(self) -> WindowConfig:
        """Return the configuration without exposing reference reassignment.

        Returns:
            WindowConfig: Read-only configuration reference for this capability.
        """

    position: Vec2
    minimized: bool
    maximized: bool
    close_requested: bool

    @property
    def size(self) -> Size:
        """Return the current window surface dimensions.

        Returns:
            Size: Current window width and height in screen pixels.
        """

    def open(self):
        """Open a display using the configured initial window settings.

        Returns:
            None: This method does not return a value.
        """

    def set_title(self, title: str):
        """Update the displayed window title without changing frozen configuration.

        Args:
            title (str): Caption to display on the window.

        Returns:
            None: This method does not return a value.
        """

    def sync_size(self, width: int, height: int) -> None:
        """Observe a native resize without issuing another platform resize request.

        Args:
            width (int): Window width in screen pixels.
            height (int): Window height in screen pixels.

        Returns:
            None: This method does not return a value.
        """

    def resize(self, width: int, height: int):
        """Request a platform window resize to the supplied dimensions.

        Args:
            width (int): Window width in screen pixels.
            height (int): Window height in screen pixels.

        Returns:
            None: This method does not return a value.
        """
