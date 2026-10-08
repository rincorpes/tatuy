from __future__ import annotations

from tatuy.ecs.world import TWorld
from tatuy.engine.system import SystemRegistration
from tatuy.features.bounds.components import BoundsConstraint
from tatuy.features.bounds.resources import (
    BoundsFrame,
    WorldBounds,
    WorldBoundsBorder,
)
from tatuy.features.bounds.systems import (
    BoundsConstraintSystem,
    WorldBoundsRenderSystem,
)
from tatuy.features.collision.collider_access import ColliderAccess
from tatuy.features.lifecycle.systems import LifetimeSystem, SpawnDelaySystem
from tatuy.features.movement.components import (
    DesiredMovement,
    Movement,
    MovementControls,
    Velocity,
)
from tatuy.features.movement.systems import (
    MovementControlSystem,
    MovementSystem,
    VelocityIntegrationSystem,
)
from tatuy.features.spatial.components import Transform
from tatuy.features.visual.components import Circle, Rect, Text
from tatuy.features.visual.systems import RenderSystem
from tatuy.scenes.context import SceneTickContext, TIntent
from tatuy.ui.components import UiNode
from tatuy.ui.resources import UIFrame


class RenderActivation:
    def matches(self, ctx: SceneTickContext[TWorld, TIntent]) -> bool:
        world = ctx.world

        ui = next(world.query(UiNode), None) is not None

        if ui and not world.has_resource(UIFrame):
            raise ValueError("UI rendering requires UIFrame")

        drawable = any(
            next(world.query(Transform, visual), None) is not None
            for visual in (Rect, Circle, Text)
        )

        return drawable or ui


class VelocityIntegrationActivation:
    def matches(self, ctx: SceneTickContext[TWorld, TIntent]) -> bool:
        return any(ctx.world.query(Velocity, Transform))


class MovementControlActivation:
    def matches(self, ctx: SceneTickContext[TWorld, TIntent]) -> bool:
        return any(ctx.world.query(MovementControls, DesiredMovement))


class MovementActivation:
    def matches(self, ctx: SceneTickContext[TWorld, TIntent]) -> bool:
        return any(ctx.world.query(Movement, DesiredMovement, Velocity))


class WorldBoundsRenderActivation:
    def matches(self, ctx: SceneTickContext[TWorld, TIntent]) -> bool:
        bounds = ctx.world.get_resource(WorldBounds)
        border = ctx.world.get_resource(WorldBoundsBorder)
        return bool(bounds and border)


class BoundsConstraintActivation:

    def __init__(self):
        self._collider_access = ColliderAccess()

    def matches(self, ctx: SceneTickContext[TWorld, TIntent]) -> bool:
        world = ctx.world

        if not world.has_resource(WorldBounds):
            return False

        if not world.has_resource(BoundsFrame):
            return False

        constraints = tuple(world.query(BoundsConstraint, Transform))

        if not constraints:
            return False

        for entity, _, _ in constraints:
            collider = self._collider_access.find(world, entity)

            if collider is None:
                return False

        return True


# pylint: disable=unused-argument
class BuiltinSystemCatalog:
    def create(
        self,
        scene,
        ctx,
    ) -> dict[str, SystemRegistration]:

        return {
            "render": SystemRegistration(
                system=RenderSystem(),
                active=RenderActivation().matches,
            ),
            "spawn_delay": SystemRegistration(
                system=SpawnDelaySystem(),
            ),
            "lifetime": SystemRegistration(
                system=LifetimeSystem(),
            ),
            "velocity": SystemRegistration(
                system=VelocityIntegrationSystem(),
                active=VelocityIntegrationActivation().matches,
                order=100,
            ),
            "movement_control": SystemRegistration(
                system=MovementControlSystem(),
                active=MovementControlActivation().matches,
            ),
            "movement": SystemRegistration(
                system=MovementSystem(),
                active=MovementActivation().matches,
            ),
            "bounds_border": SystemRegistration(
                system=WorldBoundsRenderSystem(),
            ),
            "bounds_constraints": SystemRegistration(
                system=BoundsConstraintSystem(),
                active=BoundsConstraintActivation().matches,
                order=200,
            ),
        }
