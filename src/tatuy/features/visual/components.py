from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from tatuy.geometry.size import Size
from tatuy.graphics.color import Color
from tatuy.graphics.render.queue import Layer


@dataclass
class Rect:
    size: Size
    color: Color
    layer: Layer = "world"
    z: int = 0
    visible: bool = True


@dataclass
class Circle:
    radius: float
    color: Color
    layer: Layer = "world"
    z: int = 0
    visible: bool = True


from tatuy.math.vec2 import Vec2


@dataclass
class Polygon:
    # Vertices relative to Transform.position, ordered around the perimeter.
    vertices: tuple[Vec2, ...]
    color: Color
    layer: Layer = "world"
    z: int = 0
    visible: bool = True

    def __post_init__(self) -> None:
        if len(self.vertices) < 3:
            raise ValueError("Polygon needs at least three vertices")


TextAlign = Literal["left", "center", "right"]
TextVAlign = Literal["top", "middle", "bottom"]


@dataclass
class Text:
    color: Color
    content: str = ""
    font_size: int = 16
    align: TextAlign = "left"
    valign: TextVAlign = "top"
    z: int = 0
    layer: Layer = "ui"
    visible: bool = True
