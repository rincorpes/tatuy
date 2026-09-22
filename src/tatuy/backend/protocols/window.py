from __future__ import annotations

from typing import Any, Protocol

from tatuy.backend.config import WindowConfig
from tatuy.geometry.size import Size
from tatuy.math.vec2 import Vec2


class Window(Protocol):
    """
    Represents a game window.
    """

    config: WindowConfig
    screen: Any
    position: Vec2
    minimized: bool
    maximized: bool
    close_requested: bool

    @property
    def size(self) -> Size: ...

    def open(self): ...

    def set_title(self, title: str):
        """
        Set the window title.

        :param title: New window title.
        :type title: str
        """

    def resize(self, width: int, height: int):
        """
        Resize the window.

        :param width: New width in pixels.
        :type width: int
        :param height: New height in pixels.
        :type height: int
        """
