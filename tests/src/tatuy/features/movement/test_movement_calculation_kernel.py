from types import SimpleNamespace

from tatuy.ecs.world import World
from tatuy.features.movement.components import (
    DesiredMovement,
    Movement,
    Velocity,
)
from tatuy.features.movement.kernels import PythonMovementCalculationKernel
from tatuy.features.movement.systems import MovementSystem
from tatuy.math.vec2 import Vec2


def test_python_kernel_updates_all_matching_velocities():
    world = World()
    first = world.create_entity()
    second = world.create_entity()

    first_velocity = world.add_component(first, Velocity())
    world.add_component(first, Movement(speed=10.0, acceleration=None))
    world.add_component(first, DesiredMovement(Vec2(1.0, 0.0)))

    second_velocity = world.add_component(second, Velocity())
    world.add_component(second, Movement(speed=20.0, acceleration=None))
    world.add_component(second, DesiredMovement(Vec2(0.0, -1.0)))

    PythonMovementCalculationKernel().update(world, 0.5)

    assert first_velocity.value == Vec2(10.0, 0.0)
    assert second_velocity.value == Vec2(0.0, -20.0)


def test_python_kernel_ignores_entities_missing_required_components():
    world = World()
    entity = world.create_entity()
    velocity = world.add_component(entity, Velocity(Vec2(3.0, 4.0)))
    world.add_component(entity, Movement(speed=100.0))

    PythonMovementCalculationKernel().update(world, 1.0)

    assert velocity.value == Vec2(3.0, 4.0)


def test_python_kernel_preserves_motor_injection_compatibility():
    world = World()
    entity = world.create_entity()
    movement = world.add_component(entity, Movement(speed=10.0))
    desired = world.add_component(entity, DesiredMovement(Vec2(1.0, 0.0)))
    velocity = world.add_component(entity, Velocity(Vec2(2.0, 3.0)))
    calls = []

    class RecordingMotor:
        def calculate_velocity(self, *, current, desired, movement, dt):
            calls.append((current, desired, movement, dt))
            return Vec2(7.0, 8.0)

    PythonMovementCalculationKernel(RecordingMotor()).update(world, 0.25)

    assert calls == [(Vec2(2.0, 3.0), desired.direction, movement, 0.25)]
    assert velocity.value == Vec2(7.0, 8.0)


def test_system_delegates_one_batch_call_to_injected_kernel():
    world = World()
    calls = []

    class RecordingKernel:
        def update(self, kernel_world, dt):
            calls.append((kernel_world, dt))

    system = MovementSystem(kernel=RecordingKernel())
    ctx = SimpleNamespace(world=world, dt=0.125)

    system.step(ctx)

    assert calls == [(world, 0.125)]
