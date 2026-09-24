from __future__ import annotations

from tatuy.ecs.system import BaseSystem, SystemPhase
from tatuy.ecs.world import TWorld
from tatuy.features.movement.components import (  # MovementControls,
    DesiredMovement,
    Movement,
    MovementControls,
    Velocity,
)
from tatuy.features.movement.motor import MovementMotor
from tatuy.features.spatial.components import Transform
from tatuy.math.vec2 import Vec2
from tatuy.scenes.context import SceneTickContext, TContext, TIntent


class MovementControlSystem(BaseSystem[TContext]):
    phase = SystemPhase.CONTROL

    def step(self, ctx: SceneTickContext[TWorld, TIntent]) -> None:
        for _, __, desired in ctx.world.query(
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
    phase = SystemPhase.SIMULATION

    def __init__(self, motor: MovementMotor | None = None):
        self._motor = motor or MovementMotor()

    def step(self, ctx: SceneTickContext[TWorld, TIntent]) -> None:
        for _, movement, desired, velocity in ctx.world.query(
            Movement,
            DesiredMovement,
            Velocity,
        ):
            velocity.value = self._motor.calculate_velocity(
                current=velocity.value,
                desired=desired.direction,
                movement=movement,
                dt=ctx.dt,
            )


class VelocityIntegrationSystem(BaseSystem[TContext]):
    phase = SystemPhase.SIMULATION

    def step(self, ctx: SceneTickContext[TWorld, TIntent]) -> None:
        for _, transform, velocity in ctx.world.query(
            Transform,
            Velocity,
        ):
            transform.position += velocity.value * ctx.dt
