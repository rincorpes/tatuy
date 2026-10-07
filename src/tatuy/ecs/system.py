from __future__ import annotations

from enum import IntEnum
from typing import Generic, Mapping

from tatuy.scenes.context import TContext


class SystemPhase(IntEnum):
    """
    High-level execution buckets for scene systems.

    Keep values spaced to leave room for future insertions without churn.
    """

    CONTROL = 10
    PRE_SIMULATION = 20
    PRE_SIM_COMMIT = 30
    SIMULATION = 40
    POST_SIMULATION = 50
    POST_SIM_COMMIT = 60
    PRESENTATION = 70


class BaseSystem(Generic[TContext]):

    phase: SystemPhase = SystemPhase.SIMULATION
    order: int = 0

    @property
    def name(self) -> str:
        return self.__class__.__name__

    def enabled(
        self, ctx: TContext  # pylint: disable=unused-argument
    ) -> bool:
        return True

    def step(self, ctx: TContext):
        raise NotImplementedError


class GameSystem(Generic[TContext]):
    order: int = 0

    # Optional: different placement within different phases.
    phase_orders: Mapping[SystemPhase, int] = {}

    @property
    def name(self) -> str:
        return type(self).__name__

    def enabled(
        self, ctx: TContext  # pylint: disable=unused-argument
    ) -> bool:
        return True

    def on_control(self, ctx: TContext) -> None:
        pass

    def on_pre_simulation(self, ctx: TContext) -> None:
        pass

    def on_simulation(self, ctx: TContext) -> None:
        pass

    def on_post_simulation(self, ctx: TContext) -> None:
        pass

    def on_presentation(self, ctx: TContext) -> None:
        pass
