"""Contract for explicit image saving and BGRA frame extraction."""

from __future__ import annotations

from typing import Protocol

from tatuy.backend.config import CaptureConfig


class Capture(Protocol):
    """Expose explicit image saving and portable raw frame extraction.

    Attributes:
        config (CaptureConfig): Settings for this capability.
    """

    config: CaptureConfig

    def bmp(self, path: str | None = None) -> bool:
        """Save to an explicit image path, returning false when no path is supplied.

        Args:
            path (str | None): Destination image path; None or an empty string
                skips saving.

        Returns:
            bool: Whether a nonempty destination was supplied and the image was
                saved.
        """

    def bgra8888_bytes(self) -> tuple[int, int, bytes]:
        """Return width, height, and tightly packed bytes in B, G, R, A channel order.

        Returns:
            tuple[int, int, bytes]: Frame width, frame height, and tightly
                packed bytes in blue, green, red, alpha order.
        """
