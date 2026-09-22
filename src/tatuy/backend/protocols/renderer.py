from __future__ import annotations

from typing import Protocol

from tatuy.backend.config import RendererConfig
from tatuy.geometry.size import Size
from tatuy.graphics.color import Color
from tatuy.graphics.viewport.transform import ViewportTransform
from tatuy.math.vec2 import Vec2


class Shape(Protocol):
    def rect(
        self,
        pos: Vec2,
        size: Size,
        color: Color = (255, 255, 255),
        *,
        radius: float = 0.0,
    ): ...

    def line(
        self,
        start: Vec2,
        end: Vec2,
        color: Color = (255, 255, 255),
        thickness=5,
    ): ...

    def circle(
        self, x: int, y: int, radius: int, color: Color = (255, 255, 255)
    ): ...

    def polygon(
        self,
        points: list[tuple[int, int]],
        color: Color = (255, 255, 255),
        filled: bool = True,
    ): ...


class Text(Protocol):
    def measure(
        self,
        text: str,
        font_size: int | None = None,
        font_name: str | None = None,
    ) -> tuple[int, int]: ...

    def draw(
        self,
        x: int,
        y: int,
        text: str,
        color=(255, 255, 255),
        font_size: int | None = None,
        font_name: str | None = None,
    ): ...


class Texture(Protocol):

    def create(
        self,
        w: int,
        h: int,
        data: bytes | bytearray | memoryview,
        pitch: int = -1,
    ) -> int: ...
    def draw(
        self,
        tex: int,
        x: int,
        y: int,
        w: int,
        h: int,
        angle_deg: float = 0.0,
    ): ...

    def tiled(self, tex_id: int, x: int, y: int, w: int, h: int): ...

    def destroy(self, tex: int): ...


class Clip(Protocol):
    def set(
        self,
        pos: Vec2,
        size: Size,
    ) -> None: ...

    def clear(self) -> None: ...


class Renderer(Protocol):
    """
    Interface for rendering operations.
    """

    config: RendererConfig
    viewport_transform: ViewportTransform

    @property
    def shape(self) -> Shape: ...
    @property
    def text(self) -> Text: ...
    @property
    def texture(self) -> Texture: ...
    @property
    def clip(self) -> Clip: ...

    def set_clear_color(self, r: int, g: int, b: int):
        """
        Set the clear color for the renderer.
        """

    def begin_frame(self):
        """Begin a new rendering frame."""

    def end_frame(self):
        """End the current rendering frame."""
