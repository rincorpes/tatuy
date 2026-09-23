from __future__ import annotations

from tatuy.ecs.entity.factory import EntityFactory
from tatuy.features.lifecycle.components import (
    DespawnReason,
    Lifetime,
    Respawn,
    SpawnOrigin,
)
from tatuy.features.lifecycle.resources import (
    LifecycleQueue,
    SpawnRegistry,
)
from tatuy.ecs.system.base import BaseSystem
from tatuy.ecs.world import TWorld
from tatuy.scenes.context import SceneTickContext, TContext, TIntent


class SpawnSystem(BaseSystem[TContext]):
    def __init__(self, factory: EntityFactory) -> None:
        self._factory = factory

    def step(
        self,
        ctx: SceneTickContext[TWorld, TIntent],
    ) -> None:
        queue = ctx.world.get_resource(LifecycleQueue)
        registry = ctx.world.get_resource(SpawnRegistry)

        # Process this batch. Any newly queued requests wait
        # until the next update.
        requests = queue.spawns
        queue.spawns = []

        for request in requests:
            request.remaining -= ctx.dt

            if request.remaining > 0:
                queue.spawns.append(request)
                continue

            definition = registry.definitions.get(request.definition)

            if definition is None:
                raise ValueError(
                    f"Unknown spawn definition: {request.definition}"
                )

            entity = self._factory.create(
                definition.blueprint,
                **definition.make_kwargs(),
            )

            ctx.world.add_component(
                entity,
                SpawnOrigin(definition=request.definition),
            )

            if definition.respawn is not None:
                # Respawn is frozen and contains immutable values,
                # so sharing this policy is safe.
                ctx.world.add_component(
                    entity,
                    definition.respawn,
                )

            if definition.lifetime is not None:
                # Each entity needs its own mutable countdown.
                ctx.world.add_component(
                    entity,
                    Lifetime(remaining=definition.lifetime),
                )


class LifetimeSystem(BaseSystem[TContext]):
    def step(
        self,
        ctx: SceneTickContext[TWorld, TIntent],
    ) -> None:
        queue = ctx.world.get_resource(LifecycleQueue)

        for entity, lifetime in ctx.world.query(Lifetime):
            lifetime.remaining -= ctx.dt

            if lifetime.remaining <= 0:
                queue.request_despawn(
                    entity,
                    DespawnReason.LIFETIME_EXPIRED,
                )


class DespawnSystem(BaseSystem[TContext]):
    def step(
        self,
        ctx: SceneTickContext[TWorld, TIntent],
    ) -> None:
        queue = ctx.world.get_resource(LifecycleQueue)

        requests = queue.despawns
        queue.despawns = {}

        for request in requests.values():
            entity = request.entity

            # Another removal may already have deleted this entity.
            if entity not in ctx.world.entities:
                continue

            can_respawn = (
                request.allow_respawn
                and ctx.world.has_component(entity, SpawnOrigin)
                and ctx.world.has_component(entity, Respawn)
            )

            if can_respawn:
                origin = ctx.world.get_component(
                    entity,
                    SpawnOrigin,
                )
                policy = ctx.world.get_component(
                    entity,
                    Respawn,
                )

                if request.reason in policy.reasons:
                    queue.request_spawn(
                        origin.definition,
                        delay=policy.delay,
                    )

            ctx.world.destroy_entity(entity)
