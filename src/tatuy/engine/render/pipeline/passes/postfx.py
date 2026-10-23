"""Post-processing effects render pass implementation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from tatuy.backend import Backend
from tatuy.geometry.size import Size
from tatuy.graphics.render.context import RenderContext
from tatuy.graphics.render.executor import RenderExecutor
from tatuy.graphics.render.packets import FramePacket
from tatuy.math.vec2 import Vec2


@dataclass
class PostFXPass:
    """Render post-FX operations and screen overlays."""

    name: str = "PostFXPass"

    def run(
        self,
        backend: Backend,
        ctx: RenderContext,
        packets: Sequence[FramePacket],
        executor: RenderExecutor,
    ) -> None:
        """Execute post-FX operations in logical screen coordinates."""
        renderer = backend.renderer
        viewport = ctx.viewport
        origin = Vec2(0, 0)
        size = Size(viewport.virtual_w, viewport.virtual_h)

        try:
            renderer.viewport_transform.set(
                viewport.offset_x,
                viewport.offset_y,
                viewport.scale,
            )
            renderer.clip.set(origin, size)

            for frame in packets:
                if frame.is_overlay:
                    continue

                operations = frame.packet.layer_operations("postfx")
                overlays = frame.packet.screen_overlays

                if not operations and not overlays:
                    continue

                ctx.stats.packets += 1
                ctx.stats.renderables += len(operations) + len(overlays)
                ctx.stats.draw_groups += 1

                executor.execute(backend, operations)

                for overlay in overlays:
                    renderer.shape.rect(origin, size, overlay.color)
        finally:
            renderer.clip.clear()
            renderer.viewport_transform.clear()
