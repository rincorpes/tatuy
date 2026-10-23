"""Scene presentation execution."""

from __future__ import annotations

from dataclasses import replace

from tatuy.engine.render.compiler import compile_queue
from tatuy.engine.scene import SceneService
from tatuy.graphics.canvas import QueuedCanvas
from tatuy.graphics.render.packets import FramePacket
from tatuy.graphics.render.queue import RenderQueue
from tatuy.scenes.context import SceneContext
from tatuy.tooling.profiler import profiler


class ScenePresenter:
    """Run scene presentation hooks and compile render packets."""

    def __init__(self, scene_service: SceneService) -> None:
        self._scenes = scene_service

    def present(
        self,
        dt: float,
        scene_context: SceneContext,
    ) -> list[FramePacket]:
        """Present visible scenes and return their compiled frame packets."""
        packets: list[FramePacket] = []
        with profiler.span("scene.present", "scene"):
            for entry in self._scenes.visible_entries():
                scene = entry.scene

                queue = RenderQueue()
                canvas = QueuedCanvas(queue)

                with profiler.span("scene.create_trick_context", "scene"):
                    ctx = scene.create_tick_context(
                        dt=dt,
                        render_queue=queue,
                        scene_context=scene_context,
                        canvas=canvas,
                    )
                with profiler.span("scene.on_present", "scene"):
                    scene.on_present(ctx)

                with profiler.span(
                    "scene.system_pipeline.present",
                    "scene",
                    metadata={
                        "query_strategy": ctx.world.query_strategy.name,  # type: ignore
                    },
                ):
                    scene.system_pipeline.present(ctx)

                with profiler.span("compile_queue", "render_queue"):
                    packet = replace(
                        compile_queue(queue),
                        screen_overlays=scene.screen_fx.snapshot(),
                        world_view=scene.camera_fx.snapshot(),
                    )

                packets.append(
                    FramePacket(
                        scene_id=entry.scene_id,
                        is_overlay=entry.is_overlay,
                        packet=packet,
                    )
                )

        return packets
