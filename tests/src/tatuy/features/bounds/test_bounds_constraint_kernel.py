from types import SimpleNamespace

from tatuy.ecs.world import World
from tatuy.features.bounds.components import BoundsBehavior, BoundsConstraint
from tatuy.features.bounds.kernels import PythonBoundsConstraintKernel
from tatuy.features.bounds.resources import BoundsFrame, WorldBounds
from tatuy.features.bounds.systems import BoundsConstraintSystem
from tatuy.features.collision.components import BoxCollider
from tatuy.features.lifecycle.components import DespawnReason
from tatuy.features.lifecycle.resources import LifecycleQueue
from tatuy.features.movement.components import Velocity
from tatuy.features.spatial.components import Transform
from tatuy.geometry.bounds import Bounds, BoundsSide
from tatuy.geometry.size import Size
from tatuy.math.vec2 import Vec2


def _world() -> World:
    world = World()
    world.add_resource(WorldBounds(Bounds(0.0, 0.0, 100.0, 100.0)))
    world.add_resource(BoundsFrame())
    return world


def _box_entity(
    world: World,
    *,
    position: Vec2,
    behavior: BoundsBehavior,
):
    entity = world.create_entity()
    transform = world.add_component(entity, Transform(position))
    world.add_component(entity, BoxCollider(Size(10, 10)))
    world.add_component(entity, BoundsConstraint(behavior=behavior))
    return entity, transform


def test_python_kernel_clamps_matching_entity_inside_world_bounds():
    world = _world()
    _, transform = _box_entity(
        world,
        position=Vec2(2.0, 50.0),
        behavior=BoundsBehavior.CLAMP,
    )

    PythonBoundsConstraintKernel().apply(world)

    assert transform.position == Vec2(5.0, 50.0)


def test_python_kernel_bounces_velocity_and_records_event():
    world = _world()
    entity, transform = _box_entity(
        world,
        position=Vec2(2.0, 50.0),
        behavior=BoundsBehavior.BOUNCE,
    )
    velocity = world.add_component(entity, Velocity(Vec2(-20.0, 3.0)))

    PythonBoundsConstraintKernel().apply(world)

    assert transform.position == Vec2(5.0, 50.0)
    assert velocity.value == Vec2(20.0, 3.0)
    assert world.get_resource(BoundsFrame).bounces[0].entity == entity
    assert world.get_resource(BoundsFrame).bounces[0].sides == BoundsSide.LEFT


def test_python_kernel_requests_despawn_when_entity_fully_exits_bounds():
    world = _world()
    world.add_resource(LifecycleQueue())
    entity, _ = _box_entity(
        world,
        position=Vec2(-10.0, 50.0),
        behavior=BoundsBehavior.DESPAWN,
    )

    PythonBoundsConstraintKernel().apply(world)

    request = world.get_resource(LifecycleQueue).despawns[entity]
    assert request.reason is DespawnReason.OUT_OF_BOUNDS


def test_system_delegates_one_batch_call_to_injected_kernel():
    world = World()
    calls = []

    class RecordingKernel:
        def apply(self, kernel_world):
            calls.append(kernel_world)

    system = BoundsConstraintSystem(kernel=RecordingKernel())
    system.step(SimpleNamespace(world=world))

    assert calls == [world]
