from __future__ import annotations

from dataclasses import dataclass, field
from typing import (
    Generic,
    Iterable,
)

from tatuy.ecs.system import BaseSystem, SystemPhase
from tatuy.scenes.context import TContext


@dataclass
class SystemPipeline(Generic[TContext]):

    systems: list[BaseSystem[TContext]] = field(default_factory=list)

    def __post_init__(self):
        self._sort()

    def add(self, system: BaseSystem[TContext]):
        self.systems.append(system)
        self._sort()

    def extend(
        self,
        systems: Iterable[BaseSystem[TContext]],
    ):
        """
        Extend the pipeline with multiple systems.

        :param systems: An iterable of systems to add.
        :type systems: Iterable[BaseSystem[TContext]]
        """
        self.systems.extend(systems)
        self._sort()

    def step(
        self,
        systems: Iterable[BaseSystem[TContext]],
        ctx: TContext,
        *,
        phases: Iterable[SystemPhase] | None = None,
    ):
        """
        Execute a step for each system in the pipeline.
        """
        allowed = set(phases) if phases is not None else None

        for system in systems:
            if allowed is not None and system.phase not in allowed:
                continue

            if not system.enabled(ctx):
                continue

            system.step(ctx)

    def _sort(self) -> None:
        self.systems.sort(
            key=lambda system: (
                system.phase,
                system.order,
                system.name,
            )
        )
