"""Manage the Pygame display while retaining its borrowed SDL window wrapper."""

from __future__ import annotations

# Justification: Disabling no-member checks for pygame attributes since they are
# dynamically added after initialization.
# pylint: disable=no-member
import pygame
from pygame._sdl2.video import Window  # pylint: disable=no-name-in-module

from tatuy.backend.backend_component import BackendComponent
from tatuy.backend.pygame.config import PygameWindowConfig
from tatuy.geometry.size import Size
from tatuy.math.vec2 import Vec2


class PygameWindow(BackendComponent[PygameWindowConfig]):
    """Own the display surface and retain the SDL wrapper until platform shutdown.

    Args:
        config (PygameWindowConfig): Settings used to configure this
            capability.

    Attributes:
        config (PygameWindowConfig): Settings for this capability.
        screen (pygame.Surface): Display surface, available after open().
        position (Vec2): Observed window position in screen coordinates.
        minimized (bool): Whether the window is minimized.
        maximized (bool): Whether the window is maximized.
        close_requested (bool): Whether a window close was requested.
    """

    config: PygameWindowConfig
    screen: pygame.Surface
    position: Vec2
    minimized: bool = False
    maximized: bool = False
    close_requested: bool = False

    _sdl_window: Window

    _title: str
    _flags: int
    _size: Size

    def __init__(self, config: PygameWindowConfig):
        super().__init__(config)
        self._title = config.title
        self._size = Size(config.width, config.height)
        self._flags = pygame.RESIZABLE if config.resizable else 0

    @property
    def size(self) -> Size:
        """Read current display-surface dimensions and refresh the cached size.

        Returns:
            Size: Current window width and height in screen pixels.
        """
        width, height = self.screen.get_size()
        self._size = Size(width, height)
        return self._size

    def open(self):
        """Create the configured display and retain its borrowed SDL window wrapper.

        Apply the caption and capture window position. Keep the wrapper alive until
        platform shutdown because native events retain a borrowed reference.

        Returns:
            None: This method does not return a value.

        Raises:
            pygame.error: A required native subsystem is unavailable or the
                platform operation fails.
        """
        flags = pygame.RESIZABLE if self.config.resizable else 0
        self.screen = pygame.display.set_mode(
            (self.config.width, self.config.height), flags
        )
        pygame.display.set_caption(self.config.title)
        # Pygame stores a borrowed pointer to this wrapper in window events.
        # Keep it alive while the display is open to avoid native crashes.
        self._sdl_window = Window.from_display_module()
        window_x, window_y = self._sdl_window.position  # type: ignore
        self.position = Vec2(float(window_x), float(window_y))

    def set_title(self, title: str):
        """Update the caption and cached title without rewriting frozen configuration.

        Args:
            title (str): Caption to display on the window.

        Returns:
            None: This method does not return a value.

        Raises:
            pygame.error: A required native subsystem is unavailable or the
                platform operation fails.
        """
        self._title = title
        pygame.display.set_caption(title)

    def sync_size(self, width: int, height: int) -> None:
        """Refresh observed size and surface state without requesting another resize.

        Args:
            width (int): Window width in screen pixels.
            height (int): Window height in screen pixels.

        Returns:
            None: This method does not return a value.
        """
        self._size = Size(width, height)
        surface = pygame.display.get_surface()
        if surface is not None:
            self.screen = surface

    def resize(self, width: int, height: int):
        """Request a display resize with the original flags and retain the returned surface.

        Args:
            width (int): Window width in screen pixels.
            height (int): Window height in screen pixels.

        Returns:
            None: This method does not return a value.

        Raises:
            pygame.error: A required native subsystem is unavailable or the
                platform operation fails.
        """
        self._size = Size(width, height)
        self.screen = pygame.display.set_mode(
            (self._size.width, self._size.height), self._flags
        )
