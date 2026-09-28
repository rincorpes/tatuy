from __future__ import annotations

from dataclasses import dataclass

from tatuy.ecs.entity import EntityId
from tatuy.math.vec2 import Vec2


@dataclass
class Transform:
    position: Vec2  # Center position of an entity, used for rendering and physics calculations.
    scale: float = 1.0


@dataclass
class AttachedTo:
    entity: EntityId
    offset: Vec2
