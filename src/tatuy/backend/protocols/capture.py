from __future__ import annotations

from typing import Protocol

from tatuy.backend.config import CaptureConfig


class Capture(Protocol):
    """
    Interface for frame capture operations.
    """

    config: CaptureConfig

    def bmp(self, path: str | None = None) -> bool:
        """
        Capture the current frame as a BMP file.
        """

    def bgra8888_bytes(self) -> tuple[int, int, bytes]:
        """
        Capture the current frame as raw ARGB8888 bytes.
        """
