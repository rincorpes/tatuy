from __future__ import annotations

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


class LifecycleCommitter(Generic[TContext]):
    def __init__(self, factory: EntityFactory) -> None:
        self._factory = factory

    def commit(self, ctx: SceneTickContext[TWorld, TIntent]) -> None:
        if not ctx.world.has_resource(LifecycleQueue):
            return

        queue = ctx.world.get_resource(LifecycleQueue)
        batch = queue.take_ready_batch()

        for request in batch.despawns:
            self._despawn(ctx, queue, request)

        if batch.spawns:
            registry = ctx.world.get_resource(SpawnRegistry)

            for request in batch.spawns:
                self._spawn(ctx, registry, request)

    def _spawn(
        self,
        ctx: SceneTickContext[TWorld, TIntent],
        registry: SpawnRegistry,
        request: SpawnRequest,
    ) -> None:
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
