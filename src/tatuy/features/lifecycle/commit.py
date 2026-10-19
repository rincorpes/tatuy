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
    prepare_time: float
    factory_time: float
    metadata_time: float


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

            prepare_total = 0.0
            factory_total = 0.0
            metadata_total = 0.0

            prepare_max = 0.0
            factory_max = 0.0
            metadata_max = 0.0

            with profiler.span("lifecycle.spawns", "lifecycle"):
                for spawn_request in batch.spawns:
                    result = self._spawn(
                        ctx,
                        registry,
                        spawn_request,
                    )

                    prepare_total += result.prepare_time
                    factory_total += result.factory_time
                    metadata_total += result.metadata_time

                    prepare_max = max(
                        prepare_max,
                        result.prepare_time,
                    )
                    factory_max = max(
                        factory_max,
                        result.factory_time,
                    )
                    metadata_max = max(
                        metadata_max,
                        result.metadata_time,
                    )

            count = len(batch.spawns)

            profiler.metric(
                "spawn.prepare_total_ms",
                prepare_total * 1000,
            )
            profiler.metric(
                "spawn.prepare_avg_us",
                (prepare_total / count) * 1_000_000,
            )
            profiler.metric(
                "spawn.prepare_max_us",
                prepare_max * 1_000_000,
            )

            profiler.metric(
                "spawn.factory_total_ms",
                factory_total * 1000,
            )
            profiler.metric(
                "spawn.factory_avg_us",
                (factory_total / count) * 1_000_000,
            )
            profiler.metric(
                "spawn.factory_max_us",
                factory_max * 1_000_000,
            )

            profiler.metric(
                "spawn.metadata_total_ms",
                metadata_total * 1000,
            )
            profiler.metric(
                "spawn.metadata_avg_us",
                (metadata_total / count) * 1_000_000,
            )
            profiler.metric(
                "spawn.metadata_max_us",
                metadata_max * 1_000_000,
            )

    def _spawn(
        self,
        ctx: SceneTickContext[TWorld, TIntent],
        registry: SpawnRegistry,
        request: SpawnRequest,
    ) -> SpawnResponse:
        # ---------------------------------------------------------
        # 1. PREPARE
        # Definition lookup + kwargs construction.
        # ---------------------------------------------------------

        start = perf_counter()

        definition = registry.definitions.get(request.definition)

        if definition is None:
            raise ValueError(f"Unknown spawn definition: {request.definition}")

        kwargs = dict(definition.make_kwargs())
        kwargs.update(request.kwargs)

        prepare_time = perf_counter() - start

        # ---------------------------------------------------------
        # 2. FACTORY
        # Actual entity/blueprint creation.
        # ---------------------------------------------------------

        start = perf_counter()

        entity = self._factory.create(
            definition.blueprint,
            **kwargs,
        )

        factory_time = perf_counter() - start

        # ---------------------------------------------------------
        # 3. METADATA
        # Lifecycle-specific components added after creation.
        # ---------------------------------------------------------

        start = perf_counter()

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

        metadata_time = perf_counter() - start

        return SpawnResponse(
            prepare_time=prepare_time,
            factory_time=factory_time,
            metadata_time=metadata_time,
        )

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
