from math import exp
from types import SimpleNamespace

from tatuy.ecs.world import World
from tatuy.features.fx.components import Particle
from tatuy.features.fx.kernels import PythonParticleProcessingKernel
from tatuy.features.fx.systems import ParticleUpdateSystem
from tatuy.features.lifecycle.components import Lifetime
from tatuy.features.movement.components import Velocity
from tatuy.features.visual.components import Circle
from tatuy.math.vec2 import Vec2


def _add_particle(
    world: World,
    *,
    remaining: float = 1.0,
    duration: float = 2.0,
    radius: float = 10.0,
    drag: float = 4.0,
    velocity: Vec2 | None = None,
) -> int:
    entity = world.create_entity()
    world.add_component(
        entity,
        Particle(
            duration=duration,
            radius=radius,
            color=(100, 150, 200, 255),
            drag=drag,
        ),
    )
    world.add_component(entity, Lifetime(remaining=remaining))
    world.add_component(
        entity,
        Circle(radius=radius, color=(100, 150, 200, 255)),
    )
    world.add_component(
        entity,
        Velocity(velocity or Vec2(8.0, -4.0)),
    )
    return entity


def test_python_kernel_updates_particle_visuals_and_drag():
    world = World()
    entity = _add_particle(world)

    PythonParticleProcessingKernel().update(world, 0.5)

    circle = world.get_component(entity, Circle)
    velocity = world.get_component(entity, Velocity)
    expected_drag = exp(-4.0 * 0.5)

    assert circle.visible is True
    assert circle.radius == 5.0
    assert circle.color == (100, 150, 200, 110)
    assert velocity.value.x == 8.0 * expected_drag
    assert velocity.value.y == -4.0 * expected_drag


def test_python_kernel_hides_expired_particle_and_clamps_radius():
    world = World()
    entity = _add_particle(world, remaining=-0.25)

    PythonParticleProcessingKernel().update(world, 0.25)

    circle = world.get_component(entity, Circle)

    assert circle.visible is False
    assert circle.radius == 1.0
    assert circle.color == (100, 150, 200, 0)


def test_python_kernel_ignores_entities_missing_required_components():
    world = World()
    entity = world.create_entity()
    circle = world.add_component(
        entity,
        Circle(radius=7.0, color=(10, 20, 30, 255)),
    )
    world.add_component(
        entity,
        Particle(
            duration=1.0,
            radius=7.0,
            color=(10, 20, 30, 255),
        ),
    )

    PythonParticleProcessingKernel().update(world, 1.0)

    assert circle.radius == 7.0
    assert circle.visible is True


def test_system_delegates_one_batch_call_to_injected_kernel():
    world = World()
    calls = []

    class RecordingKernel:
        def update(self, kernel_world, dt):
            calls.append((kernel_world, dt))

    system = ParticleUpdateSystem(kernel=RecordingKernel())
    ctx = SimpleNamespace(world=world, dt=0.125)

    system.step(ctx)

    assert calls == [(world, 0.125)]
