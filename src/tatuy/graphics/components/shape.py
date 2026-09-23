from __future__ import annotations

from dataclasses import dataclass

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
