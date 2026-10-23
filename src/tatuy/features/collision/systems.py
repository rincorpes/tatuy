from __future__ import annotations

from tatuy.ecs.system import BaseSystem, SystemPhase
from tatuy.ecs.world import TWorld
from tatuy.features.collision.kernels import (
    CollisionDetectionKernel,
    CollisionResponseKernel,
    PythonCollisionDetectionKernel,
    PythonCollisionResponseKernel,
)
from tatuy.features.collision.resources import CollisionFrame
from tatuy.features.collision.velocity_rule import CollisionVelocityRule
from tatuy.features.movement.components import (
    DesiredMovement,
    MovementControls,
    Velocity,
)
from tatuy.scenes.context import SceneTickContext, TContext, TIntent


class CollisionDetectionSystem(BaseSystem[TContext]):
    phase = SystemPhase.SIMULATION

    def __init__(
        self,
        kernel: CollisionDetectionKernel | None = None,
    ) -> None:
        self._kernel = kernel or PythonCollisionDetectionKernel()

    def step(
        self,
        ctx: SceneTickContext[TWorld, TIntent],
    ) -> None:
        self._kernel.detect(ctx.world)


class CollisionResponseSystem(BaseSystem[TContext]):
    def __init__(
        self,
        velocity_rules: tuple[CollisionVelocityRule, ...] = (),
        kernel: CollisionResponseKernel | None = None,
    ) -> None:
        if kernel is not None and velocity_rules:
            raise ValueError(
                "Configure velocity rules on the custom collision response kernel"
            )

        self._kernel = kernel or PythonCollisionResponseKernel(velocity_rules)

    def step(
        self,
        ctx: SceneTickContext[TWorld, TIntent],
    ) -> None:
        self._kernel.respond(ctx.world)


class CollisionDirectionSystem(BaseSystem[TContext]):
    phase = SystemPhase.POST_SIMULATION

    def step(self, ctx: SceneTickContext[TWorld, TIntent]):
        frame = ctx.world.get_resource(CollisionFrame)

        for contact in frame.contacts:
            for entity in (contact.entity_a, contact.entity_b):
                if ctx.world.has_component(entity, MovementControls):
                    continue

                if not ctx.world.has_component(entity, DesiredMovement):
                    continue

                velocity = ctx.world.get_component(entity, Velocity)
                desired = ctx.world.get_component(entity, DesiredMovement)

                if velocity.value.length_squared() > 0:
                    desired.direction = velocity.value.normalized()
