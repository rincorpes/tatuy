from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from tatuy.graphics.color import Color
from tatuy.graphics.render.queue import Layer


@dataclass
class Text:
    color: Color
    content: str = ""
    font_size: int = 16
    align: Literal["left", "center", "right"] = "left"
    valign: Literal["top", "middle", "bottom"] = "top"
    z: int = 0
    layer: Layer = "ui"
    visible: bool = True
