from __future__ import annotations

from enum import IntEnum
from typing import Generic

from tatuy.math.vec2 import Vec2
from tatuy.scenes.context import TContext


class SystemPhase(IntEnum):
    """
    High-level execution buckets for scene systems.

    Keep values spaced to leave room for future insertions without churn.
    """

    CONTROL = 10
    SIMULATION = 20
    PRESENTATION = 30


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
