"""Draw screen-space layers and scene overlays."""

from __future__ import annotations

from dataclasses import dataclass

from tatuy.backend import Backend
from tatuy.engine.loop.frame_packet import FramePacket
from tatuy.engine.render.pipeline.passes.world import WorldPass
from tatuy.graphics.render.context import RenderContext


@dataclass
class UIPass:
    name: str = "UIPass"
    layers: tuple[str, ...] = ("ui",)
    include_overlays: bool = True

    def run(
        self, backend: Backend, ctx: RenderContext, packets: list[FramePacket]
    ) -> None:
        backend.renderer.viewport_transform.clear()
        backend.renderer.clip.clear()
        try:
            for fp in packets:
                if fp.is_overlay:
                    if not self.include_overlays:
                        continue
                    ops = fp.packet.ops
                else:
                    ops = tuple(
                        op
                        for layer in self.layers
                        for op in (
                            WorldPass._layer_ops(fp.packet, layer) or ()
                        )
                    )
                if not ops:
                    continue
                ctx.stats.packets += 1
                ctx.stats.renderables += len(ops)
                ctx.stats.draw_groups += 1
                for op in ops:
                    op(backend)
        finally:
            backend.renderer.clip.clear()
            backend.renderer.viewport_transform.clear()
