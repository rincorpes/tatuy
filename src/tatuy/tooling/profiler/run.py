from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID, uuid4

from tatuy.tooling.profiler.event import ProfilerEvent


@dataclass
class Run:
    name: str
    run_type: str

    id: UUID = field(default_factory=uuid4)
    parent_id: UUID | None = None

    start_time: float = 0.0
    end_time: float | None = None

    metadata: dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, float | int] = field(default_factory=dict)

    children: list[Run] = field(default_factory=list)

    events: list[ProfilerEvent] = field(default_factory=list)

    @property
    def duration(self) -> float | None:
        if self.end_time is None:
            return None

        return self.end_time - self.start_time

    @property
    def self_duration(self) -> float | None:
        duration = self.duration

        if duration is None:
            return None

        children_duration = sum(
            child.duration or 0.0 for child in self.children
        )

        return max(
            0.0,
            duration - children_duration,
        )
