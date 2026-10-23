from __future__ import annotations

from tatuy.ecs.system import BaseSystem, SystemPhase
from tatuy.ecs.world import TWorld
from tatuy.features.movement.components import (
    DesiredMovement,
    MotionSample,
    MovementControls,
)
from tatuy.features.movement.kernels import (
    MovementCalculationKernel,
    PythonMovementCalculationKernel,
    PythonVelocityIntegrationKernel,
    VelocityIntegrationKernel,
)
from tatuy.features.movement.motor import MovementMotor
from tatuy.features.spatial.components import Transform
from tatuy.math.vec2 import Vec2
from tatuy.scenes.context import SceneTickContext, TContext, TIntent


class MovementControlSystem(BaseSystem[TContext]):
    phase = SystemPhase.CONTROL

    def step(self, ctx: SceneTickContext[TWorld, TIntent]) -> None:
        for _, _, desired in ctx.world.query(
            MovementControls, DesiredMovement
        ):
            direction = Vec2.zero()

            if ctx.intent.move_up:
                direction.y -= 1

            if ctx.intent.move_down:
                direction.y += 1

            if ctx.intent.move_left:
                direction.x -= 1

            if ctx.intent.move_right:
                direction.x += 1

            desired.direction = direction


class MovementSystem(BaseSystem[TContext]):
    phase = SystemPhase.PRE_SIMULATION

    def __init__(
        self,
        motor: MovementMotor | None = None,
        *,
        kernel: MovementCalculationKernel | None = None,
    ) -> None:
        self._kernel = kernel or PythonMovementCalculationKernel(motor)

    def step(self, ctx: SceneTickContext[TWorld, TIntent]) -> None:
        self._kernel.update(ctx.world, ctx.dt)


class VelocityIntegrationSystem(BaseSystem[TContext]):
    phase = SystemPhase.SIMULATION

    def __init__(
        self,
        kernel: VelocityIntegrationKernel | None = None,
    ) -> None:
        self._kernel = kernel or PythonVelocityIntegrationKernel()

    def step(self, ctx: SceneTickContext[TWorld, TIntent]) -> None:
        self._kernel.integrate(ctx.world, ctx.dt)


class MotionSnapshotSystem(BaseSystem[TContext]):
    phase = SystemPhase.PRE_SIMULATION

    def step(self, ctx: SceneTickContext[TWorld, TIntent]):
        for _, transform, sample in ctx.world.query(
            Transform,
            MotionSample,
        ):
            sample.start_position = Vec2(
                transform.position.x,
                transform.position.y,
            )
