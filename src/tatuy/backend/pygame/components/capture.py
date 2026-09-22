from __future__ import annotations

# Justification: Disabling no-member checks for pygame attributes since they are
# dynamically added after initialization.
# pylint: disable=no-member
import pygame

from tatuy.backend.backend_component import BackendComponent
from tatuy.backend.pygame.config import PygameCaptureConfig

from .window import PygameWindow


class PygameCapture(BackendComponent[PygameCaptureConfig]):
    """
    Capture port for the tatuy pygame backend.
    """

    def __init__(self, config: PygameCaptureConfig, window: PygameWindow):
        super().__init__(config)
        self._window = window

    def bmp(self, path: str) -> bool:
        """
        Capture the current screen and save it as a BMP file.
        """
        if not path:
            return False
        pygame.image.save(self._window.screen, str(path))
        return True

    def bgra8888_bytes(self) -> tuple[int, int, bytes]:
        """
        Capture the current screen and return the pixel data in ARGB8888 format.
        """
        w, h = self._window.screen.get_size()
        # CaptureWorker currently decodes raw bytes as BGRA for async video frames.
        # Export BGRA here so recorded PNG frames keep correct alpha/colors.
        data = pygame.image.tostring(self._window.screen, "BGRA")
        return int(w), int(h), data
