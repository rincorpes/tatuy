"""Save the Pygame display surface or extract tightly packed BGRA pixels."""

from __future__ import annotations

# Justification: Disabling no-member checks for pygame attributes since they are
# dynamically added after initialization.
# pylint: disable=no-member
import pygame

from tatuy.backend.backend_component import BackendComponent
from tatuy.backend.pygame.config import PygameCaptureConfig

from .window import PygameWindow


class PygameCapture(BackendComponent[PygameCaptureConfig]):
    """Save or extract pixels from the concrete Pygame window surface.

    Args:
        config (PygameCaptureConfig): Settings used to configure this
            capability.
        window (PygameWindow): Concrete window providing the display
            surface.
    """

    def __init__(self, config: PygameCaptureConfig, window: PygameWindow):
        super().__init__(config)
        self._window = window

    def bmp(self, path: str | None = None) -> bool:
        """Save the display to an explicit path and return whether saving was requested.

        Omitted, None, or empty paths return false without accessing the surface.
        Pygame selects encoding from the filename; save errors propagate.

        Args:
            path (str | None): Destination image path; None or an empty string
                skips saving.

        Returns:
            bool: Whether a nonempty destination was supplied and the image was
                saved.

        Raises:
            pygame.error: A required native subsystem is unavailable or the
                platform operation fails.
            OSError: The destination image cannot be written.
        """
        if not path:
            return False
        pygame.image.save(self._window.screen, str(path))
        return True

    def bgra8888_bytes(self) -> tuple[int, int, bytes]:
        """Return display width, height, and tightly packed BGRA8888 pixel bytes.

        Returns:
            tuple[int, int, bytes]: Frame width, frame height, and tightly
                packed bytes in blue, green, red, alpha order.

        Raises:
            pygame.error: A required native subsystem is unavailable or the
                platform operation fails.
        """
        w, h = self._window.screen.get_size()
        # CaptureWorker currently decodes raw bytes as BGRA for async video frames.
        # Export BGRA here so recorded PNG frames keep correct alpha/colors.
        data = pygame.image.tostring(self._window.screen, "BGRA")
        return int(w), int(h), data
