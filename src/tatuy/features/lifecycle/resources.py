from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Mapping

from tatuy.ecs.entity import EntityId
from tatuy.features.lifecycle.components import DespawnReason, Respawn


@dataclass(frozen=True)
class SpawnDefinition:
    blueprint: str
    make_kwargs: Callable[[], dict[str, Any]] = field(default=lambda: {})
    respawn: Respawn | None = None
    lifetime: float | None = None


@dataclass
class SpawnRegistry:
    definitions: dict[str, SpawnDefinition] = field(default_factory=dict)


@dataclass
class SpawnRequest:
    definition: str
    remaining: float = 0.0
    kwargs: dict[str, Any] = field(default_factory=dict)


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
        *,
        kwargs: Mapping[str, Any] | None = None,
    ) -> None:
        self.spawns.append(
            SpawnRequest(
                definition=definition,
                remaining=max(0.0, delay),
                kwargs={} if kwargs is None else dict(kwargs),
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

    def advance_spawn_delays(self, dt: float) -> None:
        for request in self.spawns:
            request.remaining = max(
                0.0,
                request.remaining - dt,
            )

    def take_ready_batch(self) -> LifecycleBatch:
        ready: list[SpawnRequest] = []
        waiting: list[SpawnRequest] = []

        for request in self.spawns:
            if request.remaining <= 0:
                ready.append(request)
            else:
                waiting.append(request)

        batch = LifecycleBatch(
            spawns=tuple(ready),
            despawns=tuple(self.despawns.values()),
        )

        self.spawns = waiting
        self.despawns = {}

        return batch


@dataclass(frozen=True)
class LifecycleBatch:
    spawns: tuple[SpawnRequest, ...]
    despawns: tuple[DespawnRequest, ...]
