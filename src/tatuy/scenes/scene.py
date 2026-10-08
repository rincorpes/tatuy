from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, ClassVar, Generic, Iterable, Mapping, Sequence, Type

from tatuy.ecs.entity.factory import EntityFactory
from tatuy.ecs.structural import StructuralCommandBuffer
from tatuy.ecs.system import BaseSystem, GameSystem
from tatuy.ecs.world import TWorld
from tatuy.engine.system import SystemPipeline, SystemRegistration
from tatuy.features.bounds.resources import (
    BoundsFrame,
    WorldBounds,
    WorldBoundsBorder,
)
from tatuy.features.fx.particles import ParticleEmitter
from tatuy.features.lifecycle.resources import (
    LifecycleQueue,
    SpawnDefinition,
    SpawnRegistry,
)
from tatuy.geometry.bounds import Bounds
from tatuy.graphics.camera.fx import CameraFX
from tatuy.graphics.canvas import Canvas
from tatuy.graphics.render.queue import RenderQueue
from tatuy.graphics.screenfx.stack import ScreenEffectStack
from tatuy.scenes.context import SceneContext, TContext, TIntent

# pylint: disable=unused-argument


@dataclass(frozen=True)
class EntitySpawn:
    definition: str
    kwargs: Mapping[str, Any] = field(default_factory=dict)
    delay: float = 0.0


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

        if not self.world.has_resource(LifecycleQueue):
            self.world.add_resource(LifecycleQueue())

        if not self.world.has_resource(SpawnRegistry):
            self.world.add_resource(SpawnRegistry())

        registry = self.world.get_resource(SpawnRegistry)
        queue = self.world.get_resource(LifecycleQueue)

        definitions = dict(self.spawn_definitions(ctx))

        duplicates = registry.definitions.keys() & definitions.keys()
        if duplicates:
            raise ValueError(
                f"Duplicate spawn definitions: {sorted(duplicates)}"
            )

        registry.definitions.update(definitions)

        placements = tuple(self.entities(ctx))

        # Validate the complete population before queueing it.
        for placement in placements:
            if placement.definition not in registry.definitions:
                raise ValueError(
                    f"Unknown spawn definition: " f"{placement.definition}"
                )

        for placement in placements:
            queue.request_spawn(
                placement.definition,
                delay=placement.delay,
                kwargs=placement.kwargs,
            )

        # pylint: disable=assignment-from-none
        bounds = self.bounds(ctx)
        if bounds is not None:
            self.world.add_resource(WorldBounds(bounds))
            self.world.add_resource(BoundsFrame())

        bounds_border = self.bounds_border(ctx)
        if bounds_border is not None:
            self.world.add_resource(bounds_border)

    def bounds(self, ctx: SceneContext) -> Bounds | None:
        return None

    def bounds_border(self, ctx: SceneContext) -> WorldBoundsBorder | None:
        return None

    def resources(self, ctx: SceneContext) -> Iterable[object]:
        return ()

    def spawn_definitions(
        self,
        ctx: SceneContext,
    ) -> Mapping[str, SpawnDefinition]:
        return {}

    def entities(
        self,
        ctx: SceneContext,
    ) -> Iterable[EntitySpawn]:
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

    def on_enter(self, ctx: SceneContext):
        raise NotImplementedError

    def on_tick(self, ctx: TContext):
        pass

    def on_present(self, ctx: TContext):
        pass

    def on_exit(self): ...

    def replay_options(self, ctx: SceneContext) -> dict[str, Any]:
        return {}
