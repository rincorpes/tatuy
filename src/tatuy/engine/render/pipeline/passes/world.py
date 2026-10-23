"""World-space render pass implementation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from tatuy.backend import Backend
from tatuy.engine.render.view import world_drawing_scope
from tatuy.graphics.render.context import RenderContext
from tatuy.graphics.render.executor import RenderExecutor
from tatuy.graphics.render.packets import FramePacket, RenderPacket
from tatuy.graphics.render.queue import RenderOperation


@dataclass
class WorldPass:
    """Render selected non-overlay layers using each packet's world view."""

    name: str = "WorldPass"
    layers: tuple[str, ...] = ("world",)

    def run(
        self,
        backend: Backend,
        ctx: RenderContext,
        packets: Sequence[FramePacket],
        executor: RenderExecutor,
    ) -> None:
        """Execute selected world-space operations for visible scene packets."""
        for frame in packets:
            if frame.is_overlay:
                continue

            for layer in self.layers:
                operations = frame.packet.layer_operations(layer)
                self._draw_operations(
                    backend,
                    ctx,
                    frame.packet,
                    operations,
                    executor,
                )

    @staticmethod
    def _draw_operations(
        backend: Backend,
        ctx: RenderContext,
        packet: RenderPacket,
        operations: Sequence[RenderOperation],
        executor: RenderExecutor,
    ) -> None:
        if not operations:
            return

        ctx.stats.packets += 1
        ctx.stats.renderables += len(operations)
        ctx.stats.draw_groups += 1

        with world_drawing_scope(
            backend,
            ctx.viewport,
            packet.world_view,
        ):
            executor.execute(backend, operations)
