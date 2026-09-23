from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


@dataclass(frozen=True)
class SpawnOrigin:
    definition: str


class DespawnReason(Enum):
    OUT_OF_BOUNDS = auto()
    LIFETIME_EXPIRED = auto()
    DEFEATED = auto()
    SCRIPTED = auto()


@dataclass(frozen=True)
class Respawn:
    delay: float = 2.0
    reasons: frozenset[DespawnReason] = frozenset(
        {
            DespawnReason.OUT_OF_BOUNDS,
            DespawnReason.DEFEATED,
        }
    )


@dataclass
class Lifetime:
    remaining: float
