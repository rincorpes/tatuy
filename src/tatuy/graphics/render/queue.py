from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Literal

from tatuy.backend.backend import Backend
from tatuy.geometry.size import Size
from tatuy.graphics.color import Color
from tatuy.graphics.render.commands import (
    CircleCommand,
    CustomCommand,
    DrawCommand,
    LineCommand,
    PolyCommand,
    RectCommand,
    TextCommand,
    TextureCommand,
)
from tatuy.math.vec2 import Vec2

Layer = Literal["world", "lighting", "ui", "effects", "postfx", "debug"]
OperationKind = Literal[
    "draw_rect",
    "draw_circle",
    "draw_line",
    "draw_texture",
    "draw_text",
    "draw_poly",
    "custom",
]


@dataclass
class DrawOperation:
    """
    A draw operation for rendering.
    """

    kind: OperationKind
    layer: Layer
    z: int = 0  # for sorting within layer
    seq: int = 0  # for stable sorting of ops with same layer/z
    payload: DrawCommand | None = None  # operation-specific data


_LAYER_ORDER: dict[Layer, int] = {
    "world": 0,
    "lighting": 1,
    "ui": 2,
    "effects": 3,
    "postfx": 4,
    "debug": 5,
}


@dataclass
class RenderQueue:
    """
    A queue of draw operations to be rendered this tick.
    Scenes/systems can push draw operations to this queue during the tick,
    and the engine will sort and render them after the tick.
    This is a more flexible alternative to building a full RenderPacket for simple
    scenes that just want to emit draw calls.
    """

    _ops: list[DrawOperation] = field(default_factory=list)
    _seq: int = 0

    def clear(self) -> None:
        """
        Clear all draw operations from the queue.
        """
        self._ops.clear()
        self._seq = 0

    def _push(
        self, kind: OperationKind, layer: Layer, z: int, payload: DrawCommand
    ) -> None:
        self._ops.append(
            DrawOperation(
                kind=kind, layer=layer, z=z, seq=self._seq, payload=payload
            )
        )
        self._seq += 1

    # pylint: disable=too-many-arguments
    def rect(
        self,
        *,
        center: Vec2,
        size: Size,
        color: Color,
        radius: float = 0.0,
        layer: Layer = "world",
        z: int = 0,
    ) -> None:
        """
        Push a rectangle draw operation.
        """
        self._push(
            "draw_rect", layer, z, RectCommand(center, size, color, radius)
        )

    def line(
        self,
        *,
        a: Vec2,
        b: Vec2,
        color: Color,
        thickness: float = 1.0,
        dash_length: float | None = None,
        dash_gap: float | None = None,
        layer: Layer = "world",
        z: int = 0,
    ) -> None:
        """
        Push a line draw operation, with optional dashed line parameters.
        """
        self._push(
            "draw_line",
            layer,
            z,
            LineCommand(a, b, color, thickness, dash_length, dash_gap),
        )

    def circle(
        self,
        *,
        center: Vec2,
        radius: float,
        color: Color,
        layer: Layer = "world",
        z: int = 0,
    ) -> None:
        """
        Push a circle draw operation.
        """
        self._push(
            "draw_circle", layer, z, CircleCommand(center, radius, color)
        )

    def poly(
        self,
        *,
        points: list[Vec2],
        fill: Color | None,
        stroke: Color | None,
        thickness: int = 1,
        closed: bool = True,
        layer: Layer = "world",
        z: int = 0,
    ) -> None:
        """
        Push a polygon draw operation.
        """
        self._push(
            "draw_poly",
            layer,
            z,
            PolyCommand(tuple(points), fill, stroke, thickness, closed),
        )

    def texture(
        self,
        *,
        tex_id: int,
        x: float,
        y: float,
        w: float,
        h: float,
        angle_deg: float = 0.0,
        layer: Layer = "world",
        z: int = 0,
    ) -> None:
        """
        Push a texture draw operation.
        """
        self._push(
            "draw_texture",
            layer,
            z,
            TextureCommand(tex_id, x, y, w, h, angle_deg),
        )

    def text(
        self,
        *,
        x: float,
        y: float,
        text: str,
        color: Color = (255, 255, 255, 255),
        font_size: int | None = None,
        font_name: str | None = None,
        align: Literal["left", "center", "right"] = "left",
        valign: Literal["top", "middle", "bottom"] = "top",
        layer: Layer = "ui",
        z: int = 0,
    ) -> None:
        """
        Push a text draw operation.
        """
        self._push(
            "draw_text",
            layer,
            z,
            TextCommand(
                x, y, text, color, font_size, font_name, align, valign
            ),
        )

    def custom(
        self,
        *,
        op: Callable[[Backend], None],
        layer: Layer = "debug",
        z: int = 0,
    ) -> None:
        """
        Push a custom draw operation defined by a callable that takes the backend.
        """
        self._push("custom", layer, z, CustomCommand(op))

    def iter_sorted(
        self, layers: tuple[Layer, ...] | list[Layer] | None = None
    ) -> list[DrawOperation]:
        """
        Get draw operations sorted by layer/z/seq, optionally filtered by layers.
        """
        if layers is None:
            ops = self._ops
        else:
            wanted = set(layers)
            ops = [op for op in self._ops if op.layer in wanted]
        return sorted(ops, key=lambda o: (_LAYER_ORDER[o.layer], o.z, o.seq))
