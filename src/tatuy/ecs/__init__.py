"""Public ECS authoring and extension API."""

from __future__ import annotations

from tatuy.ecs.entity import EntityId
from tatuy.ecs.entity.factory import (
    EntityBlueprint,
    EntityFactory,
    TypedEntityBlueprint,
)
from tatuy.ecs.structural import (
    AddComponent,
    RemoveComponent,
    StructuralCommandBuffer,
)
from tatuy.ecs.system import BaseSystem, GameSystem, SystemPhase
from tatuy.ecs.world import (
    IntersectionQueryStrategy,
    SmallestQueryStrategy,
    World,
)

__all__ = [
    "AddComponent",
    "BaseSystem",
    "EntityBlueprint",
    "EntityFactory",
    "EntityId",
    "GameSystem",
    "IntersectionQueryStrategy",
    "RemoveComponent",
    "SmallestQueryStrategy",
    "StructuralCommandBuffer",
    "SystemPhase",
    "TypedEntityBlueprint",
    "World",
]
