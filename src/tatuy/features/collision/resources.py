from __future__ import annotations

from dataclasses import dataclass, field

from tatuy.ecs.entity import EntityId
from tatuy.math.vec2 import Vec2


@dataclass(frozen=True)
class CollisionContact:
    entity_a: EntityId
    entity_b: EntityId

    # Unit normal pointing from A toward B.
    normal: Vec2
    penetration: float


@dataclass
class CollisionFrame:
    contacts: list[CollisionContact] = field(default_factory=list)
