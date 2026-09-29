from __future__ import annotations

from tatuy.ecs.component import TComponent
from tatuy.ecs.world import TWorld
from tatuy.features.collision.resources import CollisionContact


def match_contact(
    world: TWorld,
    contact: CollisionContact,
    first_type: type[TComponent],
    second_type: type[TComponent],
):
    a, b = contact.entity_a, contact.entity_b

    if world.has_component(a, first_type) and world.has_component(
        b, second_type
    ):
        return a, b

    if world.has_component(b, first_type) and world.has_component(
        a, second_type
    ):
        return b, a

    return None
