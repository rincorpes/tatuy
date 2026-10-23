from types import SimpleNamespace

import pytest

from tatuy.ecs.world import World
from tatuy.features.bounds.components import BoundsBehavior, BoundsConstraint
from tatuy.features.bounds.kernels import PythonBoundsConstraintKernel
from tatuy.features.bounds.resources import (
    BoundsBounceEvent,
    BoundsFrame,
    WorldBounds,
)
from tatuy.features.bounds.systems import BoundsDirectionSystem
from tatuy.features.collision.components import BoxCollider
from tatuy.features.movement.components import (
    DesiredMovement,
    MovementControls,
    Velocity,
)
from tatuy.features.spatial.components import Transform
from tatuy.geometry.bounds import Bounds, BoundsSide
from tatuy.geometry.size import Size
from tatuy.math.vec2 import Vec2


def test_bounds_direction_system_synchronizes_desired_direction_after_bounce():
    world = World()
    frame = world.add_resource(BoundsFrame())
    entity = world.create_entity()
    velocity = world.add_component(entity, Velocity(Vec2(3.0, 4.0)))
    desired = world.add_component(entity, DesiredMovement(Vec2(-1.0, 0.0)))
    frame.bounces.append(
        BoundsBounceEvent(entity=entity, sides=BoundsSide.LEFT)
    )

    BoundsDirectionSystem().step(SimpleNamespace(world=world))

    assert desired.direction == velocity.value.normalized()


def test_bounds_direction_system_leaves_player_controlled_direction_alone():
    world = World()
    frame = world.add_resource(BoundsFrame())
    entity = world.create_entity()
    world.add_component(entity, Velocity(Vec2(3.0, 4.0)))
    desired = world.add_component(entity, DesiredMovement(Vec2(-1.0, 0.0)))
    world.add_component(entity, MovementControls())
    frame.bounces.append(
        BoundsBounceEvent(entity=entity, sides=BoundsSide.LEFT)
    )

    BoundsDirectionSystem().step(SimpleNamespace(world=world))

    assert desired.direction == Vec2(-1.0, 0.0)


def test_bounds_constraint_kernel_requires_world_bounds_resource():
    world = World()
    world.add_resource(BoundsFrame())

    with pytest.raises(KeyError, match="WorldBounds"):
        PythonBoundsConstraintKernel().apply(world)


def test_bounds_constraint_kernel_requires_bounds_frame_resource():
    world = World()
    world.add_resource(WorldBounds(Bounds(0.0, 0.0, 100.0, 100.0)))

    with pytest.raises(KeyError, match="BoundsFrame"):
        PythonBoundsConstraintKernel().apply(world)


def test_bounds_constraint_respects_selected_side_mask():
    world = World()
    world.add_resource(WorldBounds(Bounds(0.0, 0.0, 100.0, 100.0)))
    world.add_resource(BoundsFrame())
    entity = world.create_entity()
    transform = world.add_component(entity, Transform(Vec2(2.0, 2.0)))
    world.add_component(entity, BoxCollider(Size(10, 10)))
    world.add_component(
        entity,
        BoundsConstraint(
            behavior=BoundsBehavior.CLAMP,
            sides=BoundsSide.LEFT,
        ),
    )

    PythonBoundsConstraintKernel().apply(world)

    assert transform.position == Vec2(5.0, 2.0)
