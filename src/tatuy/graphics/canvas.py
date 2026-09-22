from __future__ import annotations

from typing import Protocol

from tatuy.geometry.size import Size
from tatuy.graphics.color import Color
from tatuy.math.vec2 import Vec2


class Canvas(Protocol):
    """Drawing operations available to a scene during presentation."""

    def rect(
        self,
        *,
        position: Vec2,
        size: Size,
        color: Color,
        radius: float = 0.0,
    ) -> None: ...

    def circle(
        self,
        *,
        center: Vec2,
        radius: float,
        color: Color,
    ) -> None: ...

    def text(
        self,
        *,
        position: Vec2,
        text: str,
        color: Color = (255, 255, 255),
        font_size: int | None = None,
        font_name: str | None = None,
    ) -> None: ...
