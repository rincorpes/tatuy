"""Public lifecycle feature API."""

from tatuy.features.lifecycle.components import (
    DespawnReason,
    Lifetime,
    Respawn,
    SpawnOrigin,
)
from tatuy.features.lifecycle.resources import (
    LifecycleQueue,
    SpawnDefinition,
    SpawnRegistry,
)
from tatuy.features.lifecycle.systems import LifetimeSystem, SpawnDelaySystem

__all__ = [
    "DespawnReason",
    "LifecycleQueue",
    "Lifetime",
    "LifetimeSystem",
    "Respawn",
    "SpawnDefinition",
    "SpawnDelaySystem",
    "SpawnOrigin",
    "SpawnRegistry",
]
