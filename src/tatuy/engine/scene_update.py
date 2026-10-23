"""Scene update execution."""

from __future__ import annotations

from tatuy.engine.scene import SceneService
from tatuy.graphics.canvas import QueuedCanvas
from tatuy.graphics.render.queue import RenderQueue
from tatuy.input.frame import InputFrame
from tatuy.scenes.context import SceneContext
from tatuy.tooling.profiler import profiler


class SceneUpdater:
    """Run scene update hooks and system simulation for one frame."""

    def __init__(self, scene_service: SceneService) -> None:
        self._scenes = scene_service

    def update(
        self,
        dt: float,
        input_frame: InputFrame,
        scene_context: SceneContext,
    ) -> None:
        """Update every scene selected by the scene service."""
        input_entry = self._scenes.input_entry()
        if not input_entry:
            print("No input entry")

        for entry in self._scenes.update_entries():
            effective_input = (
                input_frame if entry is input_entry else InputFrame()
            )

            scene = entry.scene
            with profiler.span("screen_fx.update", "scene"):
                scene.screen_fx.update(dt)
            with profiler.span("camera_fx.update", "scene"):
                scene.camera_fx.update(dt)

            queue = RenderQueue()
            canvas = QueuedCanvas(queue)

            with profiler.span("intent.update_from_effective_input", "scene"):
                if hasattr(scene, "intent"):
                    scene.intent.update_from(effective_input)
                else:
                    print("Not intent defined in Scene.")

            ctx = scene.create_tick_context(
                dt=dt,
                render_queue=queue,
                scene_context=scene_context,
                canvas=canvas,
            )
            with profiler.span("on_tick", "scene"):
                scene.on_tick(ctx)
            with profiler.span(
                "system_pipeline.update",
                "scene",
                metadata={
                    "query_strategy": ctx.world.query_strategy.name,  # type: ignore
                },
            ):
                scene.system_pipeline.update(ctx)
