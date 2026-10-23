"""Python render-pass pipeline over prepared frame data."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

from tatuy.backend import Backend
from tatuy.engine.render.pipeline.passes.base import FramePacketPass
from tatuy.engine.render.pipeline.passes.begin_frame import BeginFramePass
from tatuy.engine.render.pipeline.passes.debug_overlay import DebugOverlayPass
from tatuy.engine.render.pipeline.passes.end_frame import EndFramePass
from tatuy.engine.render.pipeline.passes.lighting import LightingPass
from tatuy.engine.render.pipeline.passes.postfx import PostFXPass
from tatuy.engine.render.pipeline.passes.ui import UIPass
from tatuy.engine.render.pipeline.passes.world import WorldPass
from tatuy.engine.render.view import world_drawing_scope
from tatuy.graphics.render.context import RenderContext
from tatuy.graphics.render.executor import PythonRenderExecutor, RenderExecutor
from tatuy.graphics.render.packets import FramePacket, RenderPacket
from tatuy.graphics.viewport.state import ViewportState
from tatuy.tooling.profiler import profiler


@dataclass
class RenderPipeline:
    """Select render passes while delegating command execution to an executor."""

    executor: RenderExecutor = field(default_factory=PythonRenderExecutor)
    passes: list[FramePacketPass] = field(
        default_factory=lambda: [
            BeginFramePass(),
            WorldPass(),
            LightingPass(),
            UIPass(include_overlays=False),
            WorldPass(name="EffectsPass", layers=("effects",)),
            PostFXPass(),
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
            DebugOverlayPass(),
            EndFramePass(),
        ]
    )

    def render_frame(
        self,
        backend: Backend,
        ctx: RenderContext,
        packets: Sequence[FramePacket],
    ) -> None:
        """Render and present one complete frame."""
        if not backend.initialized:
            return
        self.render_frame_content(backend, ctx, packets)
        self.present_frame(backend, ctx)

    def render_frame_content(
        self,
        backend: Backend,
        ctx: RenderContext,
        packets: Sequence[FramePacket],
    ) -> None:
        """Render frame contents without presenting them yet."""
        for render_pass in self.passes:
            if isinstance(render_pass, EndFramePass):
                continue
            render_pass.run(backend, ctx, packets, self.executor)

    def present_frame(self, backend: Backend, ctx: RenderContext) -> None:
        """Present previously rendered frame contents."""
        ended = False
        for render_pass in self.passes:
            if not isinstance(render_pass, EndFramePass):
                continue

            with profiler.span("end_frame_pass", "render"):
                render_pass.run(backend, ctx, (), self.executor)
            ended = True

        if not ended:
            with profiler.span("backend.renderer.end_frame", "render"):
                backend.renderer.end_frame()

    def render_presentation_overlays(
        self,
        backend: Backend,
        ctx: RenderContext,
        packets: Sequence[FramePacket],
    ) -> None:
        """Render overlay-scene packets without presenting the frame."""
        UIPass(name="PresentationOverlayPass", layers=()).run(
            backend,
            ctx,
            tuple(packet for packet in packets if packet.is_overlay),
            self.executor,
        )

    def draw_packet(
        self,
        backend: Backend,
        packet: RenderPacket,
        viewport_state: ViewportState,
    ) -> None:
        """Execute one prepared packet using its world-view transform."""
        if not packet.operations:
            return

        with world_drawing_scope(
            backend,
            viewport_state,
            packet.world_view,
        ):
            self.executor.execute(backend, packet.operations)
