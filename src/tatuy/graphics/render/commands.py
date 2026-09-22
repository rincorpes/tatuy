from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Literal

from tatuy.backend import Backend
from tatuy.geometry.size import Size
from tatuy.graphics.color import Color
from tatuy.math.vec2 import Vec2


@dataclass(frozen=True)
class RectCommand:
    center: Vec2
    size: Size
    color: Color
    radius: float = 0.0


@dataclass(frozen=True)
class LineCommand:
    a: Vec2
    b: Vec2
    color: Color
    thickness: float = 1.0
    dash_length: float | None = None
    dash_gap: float | None = None


@dataclass(frozen=True)
class CircleCommand:
    center: Vec2
    radius: float
    color: Color


@dataclass(frozen=True)
class PolyCommand:
    points: tuple[Vec2, ...]
    fill: Color | None
    stroke: Color | None
    thickness: int = 1
    closed: bool = True


@dataclass(frozen=True)
class TextureCommand:
    tex_id: int
    x: float
    y: float
    w: float
    h: float
    angle_deg: float = 0.0


@dataclass(frozen=True)
class TextCommand:
    x: float
    y: float
    text: str
    color: Color
    font_size: int | None = None
    font_name: str | None = None
    align: Literal["left", "center", "right"] = "left"
    valign: Literal["top", "middle", "bottom"] = "top"


@dataclass(frozen=True)
class CustomCommand:
    op: Callable[[Backend], None]


DrawCommand = (
    RectCommand
    | LineCommand
    | CircleCommand
    | PolyCommand
    | TextureCommand
    | TextCommand
    | CustomCommand
)
