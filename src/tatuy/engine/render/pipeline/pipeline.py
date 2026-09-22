from __future__ import annotations

from dataclasses import dataclass, field

from tatuy.backend import Backend
from tatuy.engine.loop.frame_packet import FramePacket
from tatuy.engine.render.pipeline.passes.base import FramePacketPass
from tatuy.engine.render.pipeline.passes.begin_frame import BeginFramePass
from tatuy.engine.render.pipeline.passes.end_frame import EndFramePass
from tatuy.engine.render.pipeline.passes.lighting import LightingPass

# from tatuy.graphics.passes.postfx import PostFXPass
from tatuy.engine.render.pipeline.passes.ui import UIPass
from tatuy.engine.render.pipeline.passes.world import WorldPass
from tatuy.graphics.render.context import RenderContext
from tatuy.graphics.render.packets import RenderPacket
from tatuy.graphics.viewport.state import ViewportState


@dataclass
class RenderPipeline:
    """
    Minimal pipeline for v1.

    Later you can expand this into passes:
        - build draw list
        - cull
        - sort
        - backend draw pass
    """

    passes: list[FramePacketPass] = field(
        default_factory=lambda: [
            BeginFramePass(),
            WorldPass(),
            LightingPass(),
            # Basic UI
            UIPass(include_overlays=False),
            # FXs
            WorldPass(name="EffectsPass", layers=("effects",)),
            WorldPass(name="PostFXPass", layers=("postfx",)),
            # Overlays
            UIPass(
                name="OverlayPass",
                layers=(),
                include_overlays=True,
            ),
            UIPass(
                name="DebugPass",
                layers=("debug",),
                include_overlays=False,
            ),
            EndFramePass(),
        ]
    )

    def render_frame(
        self, backend: Backend, ctx: RenderContext, packets: list[FramePacket]
    ):
        """
        Render a frame using the provided Backend, RenderContext, and list of FramePackets.
        """
        if not backend.initialized:
            return
        self.render_frame_content(backend, ctx, packets)
        self.present_frame(backend, ctx)

    def render_frame_content(
        self, backend: Backend, ctx: RenderContext, packets: list[FramePacket]
    ) -> None:
        """Render the frame contents without presenting them yet."""
        for p in self.passes:
            if isinstance(p, EndFramePass):
                continue
            p.run(backend, ctx, packets)

    def present_frame(self, backend: Backend, ctx: RenderContext) -> None:
        """Present the already-rendered frame to the user."""
        ended = False
        for p in self.passes:
            if not isinstance(p, EndFramePass):
                continue
            p.run(backend, ctx, [])
            ended = True

        if not ended:
            backend.renderer.end_frame()

    def render_presentation_overlays(
        self, backend: Backend, ctx: RenderContext, packets: list[FramePacket]
    ) -> None:
        """Render presentation-only overlays after capture, before present."""
        # if not packets:
        #     return

        # drew = False
        # for p in self.passes:
        #     if not isinstance(p, UIPass):
        #         continue
        #     p.run(backend, ctx, packets)
        #     drew = True
        #     if (
        #         all(packet.is_overlay for packet in packets)
        #         and p.include_overlays
        #     ):
        #         break

        # if not drew:
        #     UIPass().run(backend, ctx, packets)

    def draw_packet(
        self,
        backend: Backend,
        packet: RenderPacket,
        viewport_state: ViewportState,
    ):
        """
        Draw the given RenderPacket using the provided Backend.
        """
        # if not packet:
        #     return

        # # world_transform = viewport_transform_for_packet(viewport_state, packet)
        # backend.set_viewport_transform(
        #     viewport_state.offset_x,
        #     viewport_state.offset_y,
        #     viewport_state.scale,
        # )

        # backend.renderer.set_clip_rect(
        #     Vec2(0, 0),
        #     Size(
        #         viewport_state.virtual_w,
        #         viewport_state.virtual_h,
        #     ),
        # )

        # try:
        #     # backend.set_viewport_transform(
        #     #     world_transform.ox,
        #     #     world_transform.oy,
        #     #     world_transform.s,
        #     # )
        #     for op in packet.ops:
        #         op(backend)
        # finally:
        #     backend.renderer.clear_clip_rect()
        #     backend.clear_viewport_transform()
