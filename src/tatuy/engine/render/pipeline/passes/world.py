"""
World render pass implementation.
"""

from __future__ import annotations

from dataclasses import dataclass

from tatuy.backend import Backend

# from tatuy.graphics.render.camera import viewport_transform_for_packet
from tatuy.engine.loop.frame_packet import FramePacket
from tatuy.engine.render.view import world_drawing_scope
from tatuy.graphics.render.context import RenderContext
from tatuy.graphics.render.packets import DrawOp, RenderPacket


@dataclass
class WorldPass:
    """
    World Render Pass.
    This pass handles rendering of world-space objects.
    """

    name: str = "WorldPass"
    layers: tuple[str, ...] = ("world",)

    def run(
        self, backend: Backend, ctx: RenderContext, packets: list[FramePacket]
    ) -> None:
        """Run the world render pass."""
        for fp in packets:
            if fp.is_overlay:
                continue
            for layer in self.layers:
                layer_ops = self._layer_ops(fp.packet, layer)
                if layer_ops is not None:
                    self._draw_ops(backend, ctx, fp.packet, layer_ops)
                elif layer == "world":
                    self._draw_packet(backend, ctx, fp.packet)

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

    def _draw_packet(
        self, backend: Backend, ctx: RenderContext, packet: RenderPacket
    ):
        if not packet or not packet.ops:
            return
        self._draw_ops(backend, ctx, packet, packet.ops)

    def _draw_ops(
        self,
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
