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
