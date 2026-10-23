"""Lighting render pass implementation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from tatuy.backend import Backend
from tatuy.engine.render.view import world_drawing_scope
from tatuy.graphics.render.context import RenderContext
from tatuy.graphics.render.executor import RenderExecutor
from tatuy.graphics.render.packets import FramePacket


@dataclass
class LightingPass:
    """Render lighting-layer operations using each packet's world view."""

    name: str = "LightingPass"

    def run(
        self,
        backend: Backend,
        ctx: RenderContext,
        packets: Sequence[FramePacket],
        executor: RenderExecutor,
    ) -> None:
        """Execute lighting operations for non-overlay packets."""
        for frame in packets:
            if frame.is_overlay:
                continue

            operations = frame.packet.layer_operations("lighting")
            if not operations:
                continue

            ctx.stats.packets += 1
            ctx.stats.renderables += len(operations)
            ctx.stats.draw_groups += 1

            with world_drawing_scope(
                backend,
                ctx.viewport,
                frame.packet.world_view,
            ):
                executor.execute(backend, operations)
