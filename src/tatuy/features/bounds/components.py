from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

from tatuy.geometry.bounds import BoundsSide


class BoundsBehavior(Enum):
    NONE = auto()
    CLAMP = auto()
    BOUNCE = auto()
    WRAP = auto()
    DESPAWN = auto()


@dataclass
class BoundsConstraint:
    behavior: BoundsBehavior
    sides: BoundsSide = BoundsSide.ALL
