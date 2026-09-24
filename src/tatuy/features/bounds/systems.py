from __future__ import annotations

from tatuy.ecs.system import BaseSystem, SystemPhase
from tatuy.ecs.world import TWorld
from tatuy.features.bounds.components import BoundsBehavior, BoundsConstraint
from tatuy.features.bounds.resources import (
    BoundsBounceEvent,
    BoundsFrame,
    WorldBounds,
    WorldBoundsBorder,
)
from tatuy.features.lifecycle.components import DespawnReason
from tatuy.features.lifecycle.resources import LifecycleQueue
from tatuy.features.movement.components import (
    DesiredMovement,
    MovementControls,
    Velocity,
)
from tatuy.features.spatial.components import Transform
from tatuy.geometry.bounds import (
    BoundsBounce,
    BoundsClamp,
    BoundsQuery,
    BoundsSide,
    BoundsWrap,
)
from tatuy.graphics.bounds_border import BoundsBorderRenderer
from tatuy.physics.colliders import ColliderAccess
from tatuy.scenes.context import SceneTickContext, TContext, TIntent


class BoundsConstraintSystem(BaseSystem[TContext]):
    def __init__(self) -> None:
        self._colliders = ColliderAccess()
        self._query = BoundsQuery()
        self._clamp = BoundsClamp()
        self._bounce = BoundsBounce()
        self._wrap = BoundsWrap()

    def step(
        self,
        ctx: SceneTickContext[TWorld, TIntent],
    ) -> None:
        bounds = ctx.world.get_resource(WorldBounds).bounds

        bounds_frame = ctx.world.get_resource(BoundsFrame)
        bounds_frame.bounces.clear()

        for entity, constraint, transform in ctx.world.query(
            BoundsConstraint,
            Transform,
        ):
            if constraint.behavior == BoundsBehavior.NONE:
                continue

            shape = self._colliders.geometry(
                ctx.world,
                entity,
            )

            match constraint.behavior:
                case BoundsBehavior.CLAMP:
                    transform.position = self._clamp.apply(
                        bounds,
                        transform.position,
                        shape,
                        sides=constraint.sides,
                    )

                case BoundsBehavior.BOUNCE:
                    velocity = ctx.world.get_component(
                        entity,
                        Velocity,
                    )

                    result = self._bounce.apply(
                        bounds,
                        transform.position,
                        shape,
                        velocity.value,
                        sides=constraint.sides,
                    )

                    transform.position = result.position
                    velocity.value = result.velocity

                    if result.bounced_sides != BoundsSide.NONE:
                        bounds_frame.bounces.append(
                            BoundsBounceEvent(
                                entity=entity,
                                sides=result.bounced_sides,
                            )
                        )

                case BoundsBehavior.WRAP:
                    result = self._wrap.apply(
                        bounds,
                        transform.position,
                        shape,
                        sides=constraint.sides,
                    )

                    transform.position = result.position

                case BoundsBehavior.DESPAWN:
                    outside = self._query.outside_sides(
                        bounds,
                        shape,
                        sides=constraint.sides,
                    )

                    if outside != BoundsSide.NONE:
                        queue = ctx.world.get_resource(LifecycleQueue)

                        queue.request_despawn(
                            entity,
                            DespawnReason.OUT_OF_BOUNDS,
                        )


class BoundsDirectionSystem(BaseSystem[TContext]):
    phase = SystemPhase.SIMULATION

    def step(self, ctx: SceneTickContext[TWorld, TIntent]):
        frame = ctx.world.get_resource(BoundsFrame)

        for event in frame.bounces:
            entity = event.entity

            # Player input remains responsible for controlled entities.
            if ctx.world.has_component(entity, MovementControls):
                continue

            if not ctx.world.has_component(entity, DesiredMovement):
                continue

            velocity = ctx.world.get_component(entity, Velocity)
            desired = ctx.world.get_component(entity, DesiredMovement)

            if velocity.value.length_squared() > 0:
                desired.direction = velocity.value.normalized()


class WorldBoundsRenderSystem(BaseSystem[TContext]):
    phase = SystemPhase.PRESENTATION

    def __init__(self) -> None:
        self._renderer = BoundsBorderRenderer()

    def step(
        self,
        ctx: SceneTickContext[TWorld, TIntent],
    ) -> None:
        bounds = ctx.world.get_resource(WorldBounds)
        border = ctx.world.get_resource(WorldBoundsBorder)

        self._renderer.submit(
            bounds.bounds,
            border,
            ctx.render_queue,
        )
