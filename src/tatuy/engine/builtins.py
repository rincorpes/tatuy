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
    BoundsDirectionSystem,
    WorldBoundsRenderSystem,
)
from tatuy.features.collision.collider_access import ColliderAccess
from tatuy.features.collision.components import CollisionBody
from tatuy.features.collision.resources import CollisionFrame
from tatuy.features.collision.systems import (
    CollisionDetectionSystem,
    CollisionDirectionSystem,
    CollisionResponseSystem,
)
from tatuy.features.lifecycle.components import Lifetime
from tatuy.features.lifecycle.resources import LifecycleQueue
from tatuy.features.lifecycle.systems import LifetimeSystem, SpawnDelaySystem
from tatuy.features.movement.components import (
    DesiredMovement,
    MotionSample,
    Movement,
    MovementControls,
    Velocity,
)
from tatuy.features.movement.systems import (
    MotionSnapshotSystem,
    MovementControlSystem,
    MovementSystem,
    VelocityIntegrationSystem,
)
from tatuy.features.spatial.components import AttachedTo, Transform
from tatuy.features.spatial.systems import AttachmentSystem
from tatuy.features.visual.components import Circle, Polygon, Rect, Text
from tatuy.features.visual.systems import RenderSystem
from tatuy.scenes.context import SceneTickContext, TIntent
from tatuy.ui.components import UiNode
from tatuy.ui.resources import UIFrame


class MovementControlActivation:
    def matches(self, ctx: SceneTickContext[TWorld, TIntent]) -> bool:
        return any(ctx.world.query(MovementControls, DesiredMovement))


class SpawnDelayActivation:
    def matches(self, ctx: SceneTickContext[TWorld, TIntent]) -> bool:
        return ctx.world.has_resource(LifecycleQueue)


class MotionSnapshotActivation:
    def matches(self, ctx: SceneTickContext[TWorld, TIntent]) -> bool:
        return any(ctx.world.query(Transform, MotionSample))


class MovementActivation:
    def matches(self, ctx: SceneTickContext[TWorld, TIntent]) -> bool:
        return any(ctx.world.query(Movement, DesiredMovement, Velocity))


class VelocityIntegrationActivation:
    def matches(self, ctx: SceneTickContext[TWorld, TIntent]) -> bool:
        return any(ctx.world.query(Velocity, Transform))


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


class CollisionDetectionActivation:

    def __init__(self):
        self._collider_access = ColliderAccess()

    def matches(self, ctx: SceneTickContext[TWorld, TIntent]) -> bool:
        return ctx.world.has_resource(CollisionFrame)


class CollisionResponseActivation:

    def __init__(self):
        self._collider_access = ColliderAccess()

    def matches(self, ctx: SceneTickContext[TWorld, TIntent]) -> bool:
        world = ctx.world

        if not world.has_resource(CollisionFrame):
            return False

        transforms = tuple(world.query(Transform, CollisionBody, Velocity))

        if not transforms:
            return False

        for entity, _, _, _ in transforms:
            collider = self._collider_access.find(world, entity)

            if collider is None:
                return False

        return True


class AttachmentActivation:

    def matches(self, ctx: SceneTickContext[TWorld, TIntent]) -> bool:
        return any(ctx.world.query(AttachedTo))


class BoundsDirectionActivation:
    def matches(self, ctx: SceneTickContext[TWorld, TIntent]) -> bool:
        bounds_frame = ctx.world.has_resource(BoundsFrame)
        return any(ctx.world.query(Velocity)) and bounds_frame


class CollisionDirectionActivation:
    def matches(self, ctx: SceneTickContext[TWorld, TIntent]) -> bool:
        collision_frame = ctx.world.has_resource(CollisionFrame)
        return any(ctx.world.query(Velocity)) and collision_frame


class LifetimeActivation:
    def matches(self, ctx: SceneTickContext[TWorld, TIntent]) -> bool:
        lifecycle = ctx.world.has_resource(LifecycleQueue)
        return any(ctx.world.query(Lifetime)) and lifecycle


class RenderActivation:
    def matches(self, ctx: SceneTickContext[TWorld, TIntent]) -> bool:
        # Any entity with transform and a visual component.
        # NOTE: Currently supported visual components are (Rect, Circle, Text), more
        # will be added in the future.
        drawable = any(
            next(ctx.world.query(Transform, visual), None) is not None
            for visual in (Rect, Circle, Polygon, Text)
        )

        ui = next(ctx.world.query(UiNode), None) is not None

        if ui and not ctx.world.has_resource(UIFrame):
            raise ValueError("UI rendering requires UIFrame")

        return drawable or ui


class WorldBoundsRenderActivation:
    def matches(self, ctx: SceneTickContext[TWorld, TIntent]) -> bool:
        bounds = ctx.world.get_resource(WorldBounds)
        border = ctx.world.get_resource(WorldBoundsBorder)
        return bool(bounds and border)


# pylint: disable=unused-argument
class BuiltinSystemCatalog:
    def create(
        self,
        scene,
        ctx,
    ) -> dict[str, SystemRegistration]:

        return {
            # CONTROL
            "movement_control": SystemRegistration(
                system=MovementControlSystem(),
                active=MovementControlActivation().matches,
            ),
            # PRE SIMULATION
            "spawn_delay": SystemRegistration(
                system=SpawnDelaySystem(),
                active=SpawnDelayActivation().matches,
            ),
            "motion_snapshot": SystemRegistration(
                system=MotionSnapshotSystem(),
                active=MotionSnapshotActivation().matches,
                order=100,
            ),
            "movement": SystemRegistration(
                system=MovementSystem(),
                active=MovementActivation().matches,
                order=200,
            ),
            # SIMULATION
            "velocity": SystemRegistration(
                system=VelocityIntegrationSystem(),
                active=VelocityIntegrationActivation().matches,
                order=100,
            ),
            "bounds_constraints": SystemRegistration(
                system=BoundsConstraintSystem(),
                active=BoundsConstraintActivation().matches,
                order=200,
            ),
            "attachment": SystemRegistration(
                system=AttachmentSystem(),
                active=AttachmentActivation().matches,
                order=300,
            ),
            "collision_detection": SystemRegistration(
                system=CollisionDetectionSystem(),
                active=CollisionDetectionActivation().matches,
                order=400,
            ),
            "collision_response": SystemRegistration(
                system=CollisionResponseSystem(),
                active=CollisionResponseActivation().matches,
                order=500,
            ),
            # POST_SIMULATION
            "bounds_direction": SystemRegistration(
                system=BoundsDirectionSystem(),
                active=BoundsDirectionActivation().matches,
            ),
            "collision_direction": SystemRegistration(
                system=CollisionDirectionSystem(),
                active=CollisionDirectionActivation().matches,
            ),
            "lifetime": SystemRegistration(
                system=LifetimeSystem(),
                active=LifetimeActivation().matches,
            ),
            # PRESENTATION
            "render": SystemRegistration(
                system=RenderSystem(),
                active=RenderActivation().matches,
            ),
            "bounds_border": SystemRegistration(
                system=WorldBoundsRenderSystem(),
                active=WorldBoundsRenderActivation().matches,
            ),
        }
