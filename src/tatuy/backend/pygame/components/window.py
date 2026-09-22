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
    """
    Port for window management.
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
        width, height = self.screen.get_size()
        self._size = Size(width, height)
        return self._size

    def open(self):
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
        """
        Set the window title.

        :param title: New window title.
        :type title: str
        """
        self._title = title
        pygame.display.set_caption(title)

    def resize(self, width: int, height: int):
        """
        Resize the window.
        """
        self._size = Size(width, height)
        self.screen = pygame.display.set_mode(
            (self._size.width, self._size.height), self._flags
        )
