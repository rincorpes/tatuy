"""
Lighting render pass implementation.
"""

from __future__ import annotations

from dataclasses import dataclass

from tatuy.backend import Backend
from tatuy.engine.loop.frame_packet import FramePacket
from tatuy.geometry.size import Size
from tatuy.graphics.render.context import RenderContext
from tatuy.graphics.render.packets import DrawOp, RenderPacket
from tatuy.math.vec2 import Vec2


@dataclass
class LightingPass:
    """
    Lighting Render Pass.
    This pass handles scene lighting effects.
    """

    name: str = "LightingPass"

    def run(
        self, backend: Backend, ctx: RenderContext, packets: list[FramePacket]
    ) -> None:
        """Run the lighting render pass."""
        for fp in packets:
            if fp.is_overlay:
                continue
            ops = self._layer_ops(fp.packet, "lighting")
            if ops is None or not ops:
                continue
            self._draw_ops(backend, ctx, fp.packet, ops)

    @staticmethod
    def _layer_ops(
        packet: RenderPacket, key: str
    ) -> tuple[DrawOp, ...] | None:
        if not packet:
            return None
        raw = packet.meta.get("pass_ops")
        if not isinstance(raw, dict):
            return None
        ops = raw.get(key)
        if ops is None:
            return tuple()
        return tuple(ops)

    @staticmethod
    def _draw_ops(
        backend: Backend,
        ctx: RenderContext,
        packet: RenderPacket,
        ops: tuple[DrawOp, ...],
    ) -> None:
        ctx.stats.packets += 1
        ctx.stats.renderables += len(ops)
        ctx.stats.draw_groups += 1

        # world_transform = viewport_transform_for_packet(ctx.viewport, packet)

        backend.renderer.viewport_transform.set(
            ctx.viewport.offset_x,
            ctx.viewport.offset_y,
            ctx.viewport.scale,
        )
        backend.renderer.clip.set(
            Vec2(0, 0),
            Size(
                ctx.viewport.virtual_w,
                ctx.viewport.virtual_h,
            ),
        )
        try:
            # backend.set_viewport_transform(
            #     world_transform.ox,
            #     world_transform.oy,
            #     world_transform.s,
            # )
            for op in ops:
                op(backend)
        finally:
            backend.renderer.clip.clear()
            backend.renderer.viewport_transform.clear()
