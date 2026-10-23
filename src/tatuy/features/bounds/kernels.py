"""Replaceable bounds kernels for performance-sensitive operations."""

from __future__ import annotations

from typing import Protocol

from tatuy.ecs.world import World
from tatuy.features.bounds.components import BoundsBehavior, BoundsConstraint
from tatuy.features.bounds.resources import (
    BoundsBounceEvent,
    BoundsFrame,
    WorldBounds,
)
from tatuy.features.collision.collider_access import ColliderAccess
from tatuy.features.lifecycle.components import DespawnReason
from tatuy.features.lifecycle.resources import LifecycleQueue
from tatuy.features.movement.components import Velocity
from tatuy.features.spatial.components import Transform
from tatuy.geometry.bounds import (
    BoundsBounce,
    BoundsClamp,
    BoundsQuery,
    BoundsSide,
    BoundsWrap,
)


class BoundsConstraintKernel(Protocol):
    """Apply one batch of world-bounds constraints."""

    def apply(self, world: World) -> None:
        """Apply configured bounds behavior to all constrained entities."""


class PythonBoundsConstraintKernel:
    """Reference bounds processing implemented with Python ECS queries."""

    def __init__(self) -> None:
        self._colliders = ColliderAccess()
        self._query = BoundsQuery()
        self._clamp = BoundsClamp()
        self._bounce = BoundsBounce()
        self._wrap = BoundsWrap()

    def apply(self, world: World) -> None:
        """Process all bounds-constrained entities in one batch."""
        bounds = world.get_resource(WorldBounds).bounds
        bounds_frame = world.get_resource(BoundsFrame)
        bounds_frame.bounces.clear()

        for entity, constraint, transform in world.query(
            BoundsConstraint,
            Transform,
        ):
            if constraint.behavior == BoundsBehavior.NONE:
                continue

            shape = self._colliders.geometry(world, entity)

            match constraint.behavior:
                case BoundsBehavior.CLAMP:
                    transform.position = self._clamp.apply(
                        bounds,
                        transform.position,
                        shape,
                        sides=constraint.sides,
                    )

                case BoundsBehavior.BOUNCE:
                    velocity = world.get_component(entity, Velocity)
                    bounce_result = self._bounce.apply(
                        bounds,
                        transform.position,
                        shape,
                        velocity.value,
                        sides=constraint.sides,
                    )
                    transform.position = bounce_result.position
                    velocity.value = bounce_result.velocity

                    if bounce_result.bounced_sides != BoundsSide.NONE:
                        bounds_frame.bounces.append(
                            BoundsBounceEvent(
                                entity=entity,
                                sides=bounce_result.bounced_sides,
                            )
                        )

                case BoundsBehavior.WRAP:
                    wrap_result = self._wrap.apply(
                        bounds,
                        transform.position,
                        shape,
                        sides=constraint.sides,
                    )
                    transform.position = wrap_result.position

                case BoundsBehavior.DESPAWN:
                    outside = self._query.outside_sides(
                        bounds,
                        shape,
                        sides=constraint.sides,
                    )
                    if outside != BoundsSide.NONE:
                        world.get_resource(LifecycleQueue).request_despawn(
                            entity,
                            DespawnReason.OUT_OF_BOUNDS,
                        )
