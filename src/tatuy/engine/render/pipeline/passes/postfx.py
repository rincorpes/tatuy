"""
Post-processing effects render pass implementation.
"""

from __future__ import annotations

from dataclasses import dataclass

from tatuy.backend import Backend
from tatuy.engine.loop.frame_packet import FramePacket
from tatuy.engine.render.pipeline.passes.world import WorldPass
from tatuy.geometry.size import Size
from tatuy.graphics.render.context import RenderContext
from tatuy.math.vec2 import Vec2


@dataclass
class PostFXPass:
    """
    PostFX Render Pass.
    This pass handles scene effect-layer draw ops and optional post-processing.
    """

    name: str = "PostFXPass"
    # registry: EffectRegistry | None = None

    def run(
        self, backend: Backend, ctx: RenderContext, packets: list[FramePacket]
    ) -> None:
        """Run the post-processing effects render pass."""
        renderer = backend.renderer
        viewport = ctx.viewport
        origin = Vec2(0, 0)
        size = Size(
            viewport.virtual_w,
            viewport.virtual_h,
        )

        try:
            # Logical screen coordinates, without a camera transform.
            renderer.viewport_transform.set(
                viewport.offset_x,
                viewport.offset_y,
                viewport.scale,
            )
            renderer.clip.set(origin, size)

            for frame in packets:
                if frame.is_overlay:
                    continue

                packet = frame.packet
                ops = WorldPass._layer_ops(packet, "postfx") or ()
                overlays = packet.screen_overlays

                if not ops and not overlays:
                    continue

                ctx.stats.packets += 1
                ctx.stats.renderables += len(ops) + len(overlays)
                ctx.stats.draw_groups += 1

                for op in ops:
                    op(backend)

                for overlay in overlays:
                    renderer.shape.rect(
                        origin,
                        size,
                        overlay.color,
                    )
        finally:
            renderer.clip.clear()
            renderer.viewport_transform.clear()
