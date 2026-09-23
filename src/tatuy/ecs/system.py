from __future__ import annotations

from enum import IntEnum
from typing import Generic

from tatuy.ecs.component import Paddle, PaddleMotionSample
from tatuy.ecs.world import TWorld
from tatuy.features.movement.components import Velocity
from tatuy.features.spatial.components import Transform
from tatuy.math.vec2 import Vec2
from tatuy.scenes.context import SceneTickContext, TContext, TIntent


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


class PaddleMotionCaptureSystem(BaseSystem[TContext]):
    phase = SystemPhase.SIMULATION

    def step(self, ctx: SceneTickContext[TWorld, TIntent]):
        for _, _, transform, sample in ctx.world.query(
            Paddle,
            Transform,
            PaddleMotionSample,
        ):
            sample.start_position = Vec2(
                transform.position.x,
                transform.position.y,
            )


class PaddleMotionMeasureSystem(BaseSystem[TContext]):
    phase = SystemPhase.SIMULATION

    def step(self, ctx: SceneTickContext[TWorld, TIntent]):
        for _, _, transform, velocity, sample in ctx.world.query(
            Paddle,
            Transform,
            Velocity,
            PaddleMotionSample,
        ):
            if sample.start_position is None or ctx.dt <= 0:
                velocity.value = Vec2.zero()
                continue

            velocity.value = (
                transform.position - sample.start_position
            ) / ctx.dt
