from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Generic

from tatuy.ecs.entity.factory import EntityFactory
from tatuy.ecs.world import TWorld
from tatuy.features.lifecycle.components import Lifetime, Respawn, SpawnOrigin
from tatuy.features.lifecycle.resources import (
    DespawnRequest,
    LifecycleQueue,
    SpawnRegistry,
    SpawnRequest,
)
from tatuy.scenes.context import SceneTickContext, TContext, TIntent
from tatuy.tooling.profiler import profiler


@dataclass
class SpawnResponse:
    factory_time: float


class LifecycleCommitter(Generic[TContext]):
    def __init__(self, factory: EntityFactory) -> None:
        self._factory = factory

    def commit(self, ctx: SceneTickContext[TWorld, TIntent]) -> None:
        if not ctx.world.has_resource(LifecycleQueue):
            return

        with profiler.span("lifecycle.take_batch", "lifecycle"):
            queue = ctx.world.get_resource(LifecycleQueue)
            batch = queue.take_ready_batch()

        profiler.metric("spawns", len(batch.spawns))
        profiler.metric("despawns", len(batch.despawns))

        if batch.despawns:
            with profiler.span("lifecycle.despawns", "lifecycle"):
                for despawn_request in batch.despawns:
                    self._despawn(ctx, queue, despawn_request)

        if batch.spawns:
            registry = ctx.world.get_resource(SpawnRegistry)

            with profiler.span("lifecycle.spawns", "lifecycle"):
                for spawn_request in batch.spawns:
                    result = self._spawn(ctx, registry, spawn_request)
                    profiler.metric("factory_time", result.factory_time * 1000)

    def _spawn(
        self,
        ctx: SceneTickContext[TWorld, TIntent],
        registry: SpawnRegistry,
        request: SpawnRequest,
    ) -> SpawnResponse:
        start = perf_counter()
        factory_time = 0.0

        definition = registry.definitions.get(request.definition)

        if definition is None:
            raise ValueError(
                f"Unknown spawn definition: " f"{request.definition}"
            )

        kwargs = dict(definition.make_kwargs())
        kwargs.update(request.kwargs)

        entity = self._factory.create(
            definition.blueprint,
            **kwargs,
        )
        factory_time += perf_counter() - start

        ctx.world.add_component(
            entity,
            SpawnOrigin(definition=request.definition),
        )

        if definition.respawn is not None:
            ctx.world.add_component(
                entity,
                definition.respawn,
            )

        if definition.lifetime is not None:
            ctx.world.add_component(
                entity,
                Lifetime(remaining=definition.lifetime),
            )

        return SpawnResponse(factory_time)

    def _despawn(
        self,
        ctx: SceneTickContext[TWorld, TIntent],
        queue: LifecycleQueue,
        request: DespawnRequest,
    ) -> None:
        world = ctx.world
        entity = request.entity

        if entity not in world.entities:
            return

        if (
            request.allow_respawn
            and world.has_component(entity, SpawnOrigin)
            and world.has_component(entity, Respawn)
        ):
            origin = world.get_component(
                entity,
                SpawnOrigin,
            )
            policy = world.get_component(
                entity,
                Respawn,
            )

            if request.reason in policy.reasons:
                queue.request_spawn(
                    origin.definition,
                    delay=policy.delay,
                )

        world.destroy_entity(entity)
