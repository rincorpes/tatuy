from types import SimpleNamespace

from tatuy.ecs.world import World
from tatuy.features.movement.components import (
    DesiredMovement,
    MotionSample,
    Movement,
    MovementControls,
    Velocity,
)
from tatuy.features.movement.motor import MovementMotor
from tatuy.features.movement.systems import (
    MotionSnapshotSystem,
    MovementControlSystem,
    MovementSystem,
)
from tatuy.features.spatial.components import Transform
from tatuy.math.vec2 import Vec2


def test_movement_control_system_updates_desired_direction_from_intent():
    world = World()
    entity = world.create_entity()
    desired = world.add_component(entity, DesiredMovement())
    world.add_component(entity, MovementControls())
    ctx = SimpleNamespace(
        world=world,
        intent=SimpleNamespace(
            move_up=True,
            move_down=False,
            move_left=False,
            move_right=True,
        ),
    )

    MovementControlSystem().step(ctx)

    assert desired.direction == Vec2(1.0, -1.0)


def test_movement_control_system_ignores_entities_without_controls():
    world = World()
    entity = world.create_entity()
    desired = world.add_component(entity, DesiredMovement(Vec2(0.25, 0.5)))
    ctx = SimpleNamespace(
        world=world,
        intent=SimpleNamespace(
            move_up=True,
            move_down=False,
            move_left=False,
            move_right=False,
        ),
    )

    MovementControlSystem().step(ctx)

    assert desired.direction == Vec2(0.25, 0.5)


def test_movement_system_applies_desired_movement_through_reference_motor():
    world = World()
    entity = world.create_entity()
    velocity = world.add_component(entity, Velocity())
    world.add_component(
        entity,
        Movement(speed=10.0, acceleration=None, max_speed=6.0),
    )
    world.add_component(entity, DesiredMovement(Vec2(1.0, 1.0)))

    MovementSystem().step(SimpleNamespace(world=world, dt=1.0))

    assert round(velocity.value.length(), 6) == 6.0
    assert velocity.value.x > 0
    assert velocity.value.y > 0


def test_motion_snapshot_system_copies_position_without_aliasing():
    world = World()
    entity = world.create_entity()
    transform = world.add_component(entity, Transform(Vec2(3.0, 4.0)))
    sample = world.add_component(entity, MotionSample())

    MotionSnapshotSystem().step(SimpleNamespace(world=world))
    transform.position.x = 99.0

    assert sample.start_position == Vec2(3.0, 4.0)


def test_movement_motor_uses_deceleration_when_direction_is_zero():
    velocity = MovementMotor().calculate_velocity(
        current=Vec2(10.0, 0.0),
        desired=Vec2.zero(),
        movement=Movement(
            speed=20.0,
            acceleration=100.0,
            deceleration=4.0,
        ),
        dt=0.5,
    )

    assert velocity == Vec2(8.0, 0.0)


def test_movement_motor_normalizes_input_and_clamps_max_speed():
    velocity = MovementMotor().calculate_velocity(
        current=Vec2.zero(),
        desired=Vec2(10.0, 10.0),
        movement=Movement(
            speed=20.0,
            acceleration=None,
            max_speed=5.0,
        ),
        dt=1.0,
    )

    assert round(velocity.length(), 6) == 5.0
