from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from tatuy.ecs.component import DespawnReason, Respawn
from tatuy.ecs.entity import EntityId
from tatuy.geometry.bounds import Bounds, BoundsSide
from tatuy.graphics.color import Color
from tatuy.math.vec2 import Vec2


@dataclass
class WorldBounds:
    bounds: Bounds


@dataclass
class WorldBoundsBorder:
    color: Color = (220, 220, 220)
    thickness: int = 6
    sides: BoundsSide = BoundsSide.ALL
    enabled: bool = True
    z: int = 0


@dataclass(frozen=True)
class SpawnDefinition:
    blueprint: str
    make_kwargs: Callable[[], dict[str, Any]]
    respawn: Respawn | None = None
    lifetime: float | None = None


@dataclass
class SpawnRegistry:
    definitions: dict[str, SpawnDefinition] = field(default_factory=dict)


@dataclass
class SpawnRequest:
    definition: str
    remaining: float = 0.0


@dataclass(frozen=True)
class DespawnRequest:
    entity: EntityId
    reason: DespawnReason
    allow_respawn: bool = True


@dataclass
class LifecycleQueue:
    spawns: list[SpawnRequest] = field(default_factory=list)
    despawns: dict[EntityId, DespawnRequest] = field(default_factory=dict)

    def request_spawn(
        self,
        definition: str,
        delay: float = 0.0,
    ) -> None:
        self.spawns.append(
            SpawnRequest(
                definition=definition,
                remaining=max(0.0, delay),
            )
        )

    def request_despawn(
        self,
        entity: EntityId,
        reason: DespawnReason,
        *,
        allow_respawn: bool = True,
    ) -> None:
        request = DespawnRequest(
            entity=entity,
            reason=reason,
            allow_respawn=allow_respawn,
        )

        # First request wins, but an explicit permanent removal
        # overrides an earlier request that allowed respawning.
        if entity not in self.despawns or not allow_respawn:
            self.despawns[entity] = request


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


@dataclass(frozen=True)
class BoundsBounceEvent:
    entity: EntityId
    sides: BoundsSide


@dataclass
class BoundsFrame:
    bounces: list[BoundsBounceEvent] = field(default_factory=list)
