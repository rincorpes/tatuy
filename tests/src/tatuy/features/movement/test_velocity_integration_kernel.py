from types import SimpleNamespace

from tatuy.ecs.world import World
from tatuy.features.movement.components import Velocity
from tatuy.features.movement.kernels import PythonVelocityIntegrationKernel
from tatuy.features.movement.systems import VelocityIntegrationSystem
from tatuy.features.spatial.components import Transform
from tatuy.math.vec2 import Vec2


def test_python_kernel_integrates_all_matching_entities():
    world = World()
    first = world.create_entity()
    second = world.create_entity()
    world.add_component(first, Transform(Vec2(10.0, 20.0)))
    world.add_component(first, Velocity(Vec2(4.0, -2.0)))
    world.add_component(second, Transform(Vec2(-5.0, 3.0)))
    world.add_component(second, Velocity(Vec2(2.0, 6.0)))

    PythonVelocityIntegrationKernel().integrate(world, 0.5)

    assert world.get_component(first, Transform).position == Vec2(12.0, 19.0)
    assert world.get_component(second, Transform).position == Vec2(-4.0, 6.0)


def test_python_kernel_ignores_entities_missing_required_components():
    world = World()
    transform_only = world.create_entity()
    velocity_only = world.create_entity()
    transform = world.add_component(transform_only, Transform(Vec2(1.0, 2.0)))
    world.add_component(velocity_only, Velocity(Vec2(5.0, 5.0)))

    PythonVelocityIntegrationKernel().integrate(world, 1.0)

    assert transform.position == Vec2(1.0, 2.0)


def test_python_kernel_zero_dt_preserves_position():
    world = World()
    entity = world.create_entity()
    transform = world.add_component(entity, Transform(Vec2(3.0, 4.0)))
    world.add_component(entity, Velocity(Vec2(100.0, -50.0)))

    PythonVelocityIntegrationKernel().integrate(world, 0.0)

    assert transform.position == Vec2(3.0, 4.0)


def test_system_delegates_one_batch_call_to_injected_kernel():
    world = World()
    calls = []

    class RecordingKernel:
        def integrate(self, kernel_world, dt):
            calls.append((kernel_world, dt))

    system = VelocityIntegrationSystem(kernel=RecordingKernel())
    ctx = SimpleNamespace(world=world, dt=0.25)

    system.step(ctx)

    assert calls == [(world, 0.25)]
