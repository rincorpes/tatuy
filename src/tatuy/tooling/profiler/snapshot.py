from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from tatuy.tooling.profiler.event import ProfilerEvent
from tatuy.tooling.profiler.run import Run


@dataclass(slots=True)
class EventSnapshot:
    name: str
    duration: float | None
    metadata: dict[str, Any]

    @classmethod
    def from_event(cls, event: ProfilerEvent) -> EventSnapshot:
        return cls(
            name=event.name,
            duration=event.duration,
            metadata=dict(event.metadata),
        )


@dataclass(slots=True)
class RunSnapshot:
    name: str
    run_type: str

    duration: float | None
    self_duration: float | None
    work_duration: float | None

    metadata: dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, float | int] = field(default_factory=dict)

    events: list[EventSnapshot] = field(default_factory=list)
    children: list[RunSnapshot] = field(default_factory=list)

    @classmethod
    def from_run(cls, run: Run) -> RunSnapshot:
        return cls(
            name=run.name,
            run_type=run.run_type,
            duration=run.duration,
            self_duration=run.self_duration,
            work_duration=run.work_duration,
            metadata=dict(run.metadata or {}),
            metrics=dict(run.metrics or {}),
            events=[
                EventSnapshot.from_event(event) for event in run.events or ()
            ],
            children=[
                RunSnapshot.from_run(child) for child in run.children or ()
            ],
        )


@dataclass(slots=True)
class StatsSnapshot:
    path: str
    calls: int
    total: float
    peak: float

    @property
    def average(self) -> float:
        if self.calls == 0:
            return 0.0

        return self.total / self.calls


@dataclass(slots=True)
class ProfileSnapshot:
    stats: list[StatsSnapshot]
    recent_runs: list[RunSnapshot]
    slow_runs: list[RunSnapshot]
