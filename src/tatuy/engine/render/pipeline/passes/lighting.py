"""
Lighting render pass implementation.
"""

from __future__ import annotations

from dataclasses import dataclass

from tatuy.backend import Backend
from tatuy.engine.loop.frame_packet import FramePacket
from tatuy.engine.render.view import world_drawing_scope
from tatuy.graphics.render.context import RenderContext
from tatuy.graphics.render.packets import DrawOp, RenderPacket


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
        if not ops:
            return

        ctx.stats.packets += 1
        ctx.stats.renderables += len(ops)
        ctx.stats.draw_groups += 1

        with world_drawing_scope(
            backend,
            ctx.viewport,
            packet.world_view,
        ):
            for op in ops:
                op(backend)
