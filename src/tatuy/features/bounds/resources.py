from __future__ import annotations

from dataclasses import dataclass, field

from tatuy.ecs.entity import EntityId
from tatuy.geometry.bounds import Bounds, BoundsSide
from tatuy.graphics.color import Color


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
class BoundsBounceEvent:
    entity: EntityId
    sides: BoundsSide


@dataclass
class BoundsFrame:
    bounces: list[BoundsBounceEvent] = field(default_factory=list)
