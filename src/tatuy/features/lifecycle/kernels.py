"""Replaceable lifecycle kernels for batched structural mutation."""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Protocol

from tatuy.ecs.entity.factory import EntityFactory
from tatuy.ecs.world import World
from tatuy.features.lifecycle.components import Lifetime, Respawn, SpawnOrigin
from tatuy.features.lifecycle.resources import (
    DespawnRequest,
    LifecycleQueue,
    SpawnRegistry,
    SpawnRequest,
)
from tatuy.tooling.profiler import profiler


class LifecycleCommitKernel(Protocol):
    """Apply the ready lifecycle batch for one structural commit barrier."""

    def commit(self, world: World, factory: EntityFactory) -> None:
        """Apply ready spawn and despawn requests to ``world``."""


@dataclass(frozen=True)
class SpawnResponse:
    """Timing information for one Python blueprint spawn."""

    prepare_time: float
    factory_time: float
    metadata_time: float


class PythonLifecycleCommitKernel:
    """Reference lifecycle commit implemented with Python world operations."""

    def commit(self, world: World, factory: EntityFactory) -> None:
        """Apply one ready lifecycle batch using the supplied entity factory."""
        if not world.has_resource(LifecycleQueue):
            return

        with profiler.span("lifecycle.take_batch", "lifecycle"):
            queue = world.get_resource(LifecycleQueue)
            batch = queue.take_ready_batch()

        profiler.metric("spawns", len(batch.spawns))
        profiler.metric("despawns", len(batch.despawns))

        if batch.despawns:
            with profiler.span("lifecycle.despawns", "lifecycle"):
                for despawn_request in batch.despawns:
                    self._despawn(world, queue, despawn_request)

        if not batch.spawns:
            return

        registry = world.get_resource(SpawnRegistry)
        responses: list[SpawnResponse] = []
        with profiler.span("lifecycle.spawns", "lifecycle"):
            for spawn_request in batch.spawns:
                responses.append(
                    self._spawn(world, factory, registry, spawn_request)
                )

        self._record_spawn_metrics(responses)

    def _spawn(
        self,
        world: World,
        factory: EntityFactory,
        registry: SpawnRegistry,
        request: SpawnRequest,
    ) -> SpawnResponse:
        start = perf_counter()
        definition = registry.definitions.get(request.definition)
        if definition is None:
            raise ValueError(f"Unknown spawn definition: {request.definition}")

        kwargs = dict(definition.make_kwargs())
        kwargs.update(request.kwargs)
        prepare_time = perf_counter() - start

        start = perf_counter()
        entity = factory.create(definition.blueprint, **kwargs)
        factory_time = perf_counter() - start

        start = perf_counter()
        world.add_component(entity, SpawnOrigin(definition=request.definition))
        if definition.respawn is not None:
            world.add_component(entity, definition.respawn)
        if definition.lifetime is not None:
            world.add_component(
                entity, Lifetime(remaining=definition.lifetime)
            )
        metadata_time = perf_counter() - start

        return SpawnResponse(prepare_time, factory_time, metadata_time)

    @staticmethod
    def _despawn(
        world: World,
        queue: LifecycleQueue,
        request: DespawnRequest,
    ) -> None:
        entity = request.entity
        if entity not in world.entities:
            return

        if (
            request.allow_respawn
            and world.has_component(entity, SpawnOrigin)
            and world.has_component(entity, Respawn)
        ):
            origin = world.get_component(entity, SpawnOrigin)
            policy = world.get_component(entity, Respawn)
            if request.reason in policy.reasons:
                queue.request_spawn(origin.definition, delay=policy.delay)

        world.destroy_entity(entity)

    @staticmethod
    def _record_spawn_metrics(responses: list[SpawnResponse]) -> None:
        if not responses:
            return

        count = len(responses)
        for name in ("prepare", "factory", "metadata"):
            values = [
                getattr(response, f"{name}_time") for response in responses
            ]
            total = sum(values)
            profiler.metric(f"spawn.{name}_total_ms", total * 1000)
            profiler.metric(
                f"spawn.{name}_avg_us", (total / count) * 1_000_000
            )
            profiler.metric(f"spawn.{name}_max_us", max(values) * 1_000_000)
