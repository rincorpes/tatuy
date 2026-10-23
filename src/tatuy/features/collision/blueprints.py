"""Collision-owned helpers for feature-aware entity blueprints."""

from __future__ import annotations

from dataclasses import dataclass

from tatuy.ecs.entity import EntityId
from tatuy.ecs.world import World
from tatuy.features.collision.components import CollisionBody


@dataclass(frozen=True, kw_only=True)
class CollisionBlueprintAttrs:
    """Optional collision-body settings shared by built-in blueprints."""

    with_collider: bool = False
    collision_body_inverse_mass: float = 1
    collision_body_restitution: float = 1


def add_collision_components(
    world: World,
    entity: EntityId,
    collider: object | None,
    attrs: CollisionBlueprintAttrs,
) -> None:
    """Attach a collider and default body when requested by a blueprint."""
    if collider is None:
        return

    if not world.has_component(entity, type(collider)):
        world.add_component(entity, collider)

    if not world.has_component(entity, CollisionBody):
        world.add_component(
            entity,
            CollisionBody(
                inverse_mass=attrs.collision_body_inverse_mass,
                restitution=attrs.collision_body_restitution,
            ),
        )
