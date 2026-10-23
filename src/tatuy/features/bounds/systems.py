from __future__ import annotations

from tatuy.ecs.system import BaseSystem, SystemPhase
from tatuy.ecs.world import TWorld
from tatuy.features.bounds.kernels import (
    BoundsConstraintKernel,
    PythonBoundsConstraintKernel,
)
from tatuy.features.bounds.render import BoundsBorderRenderer
from tatuy.features.bounds.resources import (
    BoundsFrame,
    WorldBounds,
    WorldBoundsBorder,
)
from tatuy.features.movement.components import (
    DesiredMovement,
    MovementControls,
    Velocity,
)
from tatuy.scenes.context import SceneTickContext, TContext, TIntent
from tatuy.tooling.profiler import profiler


class BoundsConstraintSystem(BaseSystem[TContext]):
    def __init__(
        self,
        kernel: BoundsConstraintKernel | None = None,
    ) -> None:
        self._kernel = kernel or PythonBoundsConstraintKernel()

    def step(
        self,
        ctx: SceneTickContext[TWorld, TIntent],
    ) -> None:
        self._kernel.apply(ctx.world)


class BoundsDirectionSystem(BaseSystem[TContext]):
    phase = SystemPhase.POST_SIMULATION

    def step(self, ctx: SceneTickContext[TWorld, TIntent]):
        frame = ctx.world.get_resource(BoundsFrame)

        for event in frame.bounces:
            entity = event.entity

            # Player input remains responsible for controlled entities.
            if ctx.world.has_component(entity, MovementControls):
                continue

            if not ctx.world.has_component(entity, DesiredMovement):
                continue

            velocity = ctx.world.get_component(entity, Velocity)
            desired = ctx.world.get_component(entity, DesiredMovement)

            if velocity.value.length_squared() > 0:
                desired.direction = velocity.value.normalized()


class WorldBoundsRenderSystem(BaseSystem[TContext]):
    phase = SystemPhase.PRESENTATION

    def __init__(self) -> None:
        self._renderer = BoundsBorderRenderer()

    def step(
        self,
        ctx: SceneTickContext[TWorld, TIntent],
    ) -> None:
        with profiler.span("bounds.render", "bounds"):
            bounds = ctx.world.get_resource(WorldBounds)
            border = ctx.world.get_resource(WorldBoundsBorder)

            self._renderer.submit(
                bounds.bounds,
                border,
                ctx.render_queue,
            )
