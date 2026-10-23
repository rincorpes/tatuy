"""Scene drawing interfaces and queue-backed implementation."""

from __future__ import annotations

from typing import Protocol

from tatuy.geometry.size import Size
from tatuy.graphics.color import Color
from tatuy.graphics.render.queue import RenderQueue
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
    ) -> None:
        """Draw a rectangle using a top-left position."""

    def circle(
        self,
        *,
        center: Vec2,
        radius: float,
        color: Color,
    ) -> None:
        """Draw a circle."""

    def text(
        self,
        *,
        position: Vec2,
        text: str,
        color: Color = (255, 255, 255),
        font_size: int | None = None,
        font_name: str | None = None,
    ) -> None:
        """Draw text at a position."""


class QueuedCanvas:
    """Record scene drawing commands into a render queue."""

    def __init__(self, queue: RenderQueue) -> None:
        self._queue = queue

    def rect(
        self,
        *,
        position: Vec2,
        size: Size,
        color: Color,
        radius: float = 0.0,
    ) -> None:
        """Record a rectangle using the canvas top-left position contract."""
        center = Vec2(
            position.x + size.width / 2,
            position.y + size.height / 2,
        )
        self._queue.rect(
            center=center,
            size=Size(size.width, size.height),
            color=color,
            radius=radius,
        )

    def circle(
        self,
        *,
        center: Vec2,
        radius: float,
        color: Color,
    ) -> None:
        """Record a circle draw command."""
        self._queue.circle(
            center=center,
            radius=radius,
            color=color,
        )

    def text(
        self,
        *,
        position: Vec2,
        text: str,
        color: Color = (255, 255, 255),
        font_size: int | None = None,
        font_name: str | None = None,
    ) -> None:
        """Record a text draw command."""
        self._queue.text(
            x=position.x,
            y=position.y,
            text=text,
            color=color,
            font_size=font_size,
            font_name=font_name,
        )
