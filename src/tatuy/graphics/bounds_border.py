from __future__ import annotations

from tatuy.features.bounds.resources import WorldBoundsBorder
from tatuy.geometry.border import BoundsBorderGeometry
from tatuy.geometry.bounds import Bounds
from tatuy.geometry.size import Size
from tatuy.graphics.render.queue import RenderQueue
from tatuy.math.vec2 import Vec2


class BoundsBorderRenderer:
    def __init__(self) -> None:
        self._geometry = BoundsBorderGeometry()

    def submit(
        self,
        bounds: Bounds,
        border: WorldBoundsBorder,
        queue: RenderQueue,
    ) -> None:
        if not border.enabled:
            return

        strips = self._geometry.resolve(
            bounds,
            border.thickness,
            border.sides,
        )

        for strip in strips:
            size = Size(
                width=round(strip.width),
                height=round(strip.height),
            )

            if size.width <= 0 or size.height <= 0:
                continue

            queue.rect(
                center=Vec2(
                    strip.left + size.width / 2,
                    strip.top + size.height / 2,
                ),
                size=size,
                color=border.color,
                layer="world",
                z=border.z,
            )
