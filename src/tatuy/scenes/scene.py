from __future__ import annotations

from collections.abc import Generator
from typing import Any, ClassVar, Generic, Iterable, Mapping, Sequence, Type

from tatuy.ecs.entity.factory import EntityFactory
from tatuy.ecs.structural import StructuralCommandBuffer
from tatuy.ecs.system import BaseSystem, GameSystem
from tatuy.ecs.world import TWorld
from tatuy.engine.system import SystemPipeline, SystemRegistration
from tatuy.features.fx.particles import ParticleEmitter
from tatuy.graphics.camera.fx import CameraFX
from tatuy.graphics.canvas import Canvas
from tatuy.graphics.render.queue import RenderQueue
from tatuy.graphics.screenfx.stack import ScreenEffectStack
from tatuy.scenes.context import SceneContext, TContext, TIntent

# pylint: disable=unused-argument


class Scene(Generic[TWorld, TIntent, TContext]):

    world_type: Type[TWorld]
    intent_type: Type[TIntent]
    tick_context_type: Type[TContext]
    factory_type: Type[EntityFactory] = EntityFactory

    particles: ParticleEmitter
    screen_fx: ScreenEffectStack
    camera_fx: CameraFX

    systems: Sequence[BaseSystem[TContext]] = ()

    shared_resource_types: ClassVar[tuple[type[object], ...]] = ()

    system_pipeline: SystemPipeline[TContext]
    structural_commands: StructuralCommandBuffer[TContext]

    _world_cache: TWorld | None = None
    _intent_cache: TIntent | None = None
    _factory_cache: EntityFactory | None = None

    @property
    def world(self) -> TWorld:
        if self._world_cache:
            return self._world_cache
        self._world_cache = self.world_type()
        return self._world_cache

    @property
    def intent(self) -> TIntent:
        if self._intent_cache:
            return self._intent_cache
        self._intent_cache = self.intent_type()
        return self._intent_cache

    @property
    def factory(self) -> EntityFactory:
        if self._factory_cache:
            return self._factory_cache
        self._factory_cache = self.factory_type(self.world)
        return self._factory_cache

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

    def enter(self, ctx: SceneContext) -> None:
        self.configure(ctx)
        self.on_enter(ctx)

    def configure(self, ctx: SceneContext):
        self.screen_fx = ScreenEffectStack()
        self.camera_fx = CameraFX()

        for resource_type in self.shared_resource_types:
            resource = ctx.resources.get(resource_type)
            self.world.add_resource(resource)

        for resource in self.resources(ctx):
            self.world.add_resource(resource)

        self.structural_commands = StructuralCommandBuffer()
        self.world.add_resource(self.structural_commands)

    def resources(self, ctx: SceneContext) -> Iterable[object]:
        return ()

    def game_systems(
        self, ctx: SceneContext
    ) -> Iterable[BaseSystem | GameSystem]:
        return ()

    def builtin_overrides(
        self,
        ctx: SceneContext,
    ) -> Mapping[str, SystemRegistration[TContext] | None]:
        return {}

    def entities(self, ctx: SceneContext) -> Generator[object, None, None]:
        yield None

    def on_enter(self, ctx: SceneContext):
        raise NotImplementedError

    def on_tick(self, ctx: TContext):
        pass

    def on_present(self, ctx: TContext):
        pass

    def on_exit(self): ...

    def replay_options(self, ctx: SceneContext) -> dict[str, Any]:
        return {}
