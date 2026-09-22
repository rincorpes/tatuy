from __future__ import annotations

from typing import Any, Generic, Sequence, Type

from tatuy.ecs.entity_factory import EntityFactory
from tatuy.ecs.system import BaseSystem, SystemPhase
from tatuy.ecs.world import TWorld
from tatuy.graphics.canvas import Canvas
from tatuy.graphics.render.queue import RenderQueue
from tatuy.scenes.context import SceneContext, TContext, TIntent


class Scene(Generic[TWorld, TIntent, TContext]):

    world: TWorld
    intent: TIntent
    systems: Sequence[BaseSystem[TContext]] = ()

    entity_factory: EntityFactory

    tick_context_type: Type[TContext]

    UPDATE_PHASES = (
        SystemPhase.CONTROL,
        SystemPhase.SIMULATION,
    )

    PRESENTATION_PHASES = (SystemPhase.PRESENTATION,)

    def create_tick_context(
        self,
        dt: float,
        render_queue: RenderQueue,
        scene_context: SceneContext,
        canvas: Canvas,
    ) -> TContext | None:
        if not hasattr(self, "tick_context_type"):
            print("No tick content type defined")
            return None
        return self.tick_context_type(
            dt=dt,
            world=self.world,
            intent=self.intent,
            scene_context=scene_context,
            canvas=canvas,
            render_queue=render_queue,
        )

    def replay_options(self, ctx: SceneContext) -> dict[str, Any]:
        return {}

    def on_enter(self, ctx: SceneContext):
        raise NotImplementedError

    def on_tick(self, ctx: TContext):
        pass

    def on_present(self, ctx: TContext):
        pass

    def on_exit(self): ...
