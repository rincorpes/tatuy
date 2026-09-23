from __future__ import annotations

from tatuy.ecs.system.base import BaseSystem, SystemPhase
from tatuy.ecs.world import TWorld
from tatuy.features.movement.components import (
    Movement,
    MovementControls,
    Velocity,
)
from tatuy.features.spatial.components import Transform
from tatuy.math.vec2 import Vec2
from tatuy.scenes.context import SceneTickContext, TContext, TIntent


class VelocityIntegrationSystem(BaseSystem[TContext]):
    phase = SystemPhase.SIMULATION

    def step(self, ctx: SceneTickContext[TWorld, TIntent]) -> None:
        for _, transform, velocity in ctx.world.query(
            Transform,
            Velocity,
        ):
            transform.position.x += velocity.value.x * ctx.dt
            transform.position.y += velocity.value.y * ctx.dt


class MovementControlSystem(BaseSystem[TContext]):
    def step(self, ctx: SceneTickContext[TWorld, TIntent]):
        for _, movement, controls, velocity in ctx.world.query(
            Movement,
            MovementControls,
            Velocity,
        ):
            direction = Vec2.zero()

            if controls.up and ctx.intent.move_up:
                direction.y -= 1

            if controls.down and ctx.intent.move_down:
                direction.y += 1

            if controls.left and ctx.intent.move_left:
                direction.x -= 1

            if controls.right and ctx.intent.move_right:
                direction.x += 1

            if controls.normalize and direction.length_squared() > 0:
                direction = direction.normalized()

            velocity.value = direction * movement.speed
