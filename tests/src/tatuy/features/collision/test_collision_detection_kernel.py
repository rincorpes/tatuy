from types import SimpleNamespace

from tatuy.ecs.world import World
from tatuy.features.collision.components import CircleCollider
from tatuy.features.collision.kernels import PythonCollisionDetectionKernel
from tatuy.features.collision.resources import CollisionFrame
from tatuy.features.collision.systems import CollisionDetectionSystem
from tatuy.features.spatial.components import Transform
from tatuy.math.vec2 import Vec2


def test_python_kernel_detects_overlapping_colliders_in_entity_order():
    world = World()
    first = world.create_entity()
    second = world.create_entity()
    world.add_resource(CollisionFrame())

    # Add components in reverse entity order to prove detection ordering is
    # based on entity identity rather than component insertion order.
    world.add_component(second, Transform(Vec2(8.0, 0.0)))
    world.add_component(second, CircleCollider(5.0))
    world.add_component(first, Transform(Vec2(0.0, 0.0)))
    world.add_component(first, CircleCollider(5.0))

    PythonCollisionDetectionKernel().detect(world)

    contacts = world.get_resource(CollisionFrame).contacts
    assert len(contacts) == 1
    assert contacts[0].entity_a == first
    assert contacts[0].entity_b == second
    assert contacts[0].normal == Vec2(1.0, 0.0)
    assert contacts[0].penetration == 2.0


def test_python_kernel_clears_previous_contacts_and_ignores_separated_pairs():
    world = World()
    first = world.create_entity()
    second = world.create_entity()
    frame = world.add_resource(CollisionFrame())
    frame.contacts.append(object())  # type: ignore[arg-type]

    world.add_component(first, Transform(Vec2(0.0, 0.0)))
    world.add_component(first, CircleCollider(2.0))
    world.add_component(second, Transform(Vec2(10.0, 0.0)))
    world.add_component(second, CircleCollider(2.0))

    PythonCollisionDetectionKernel().detect(world)

    assert frame.contacts == []


def test_python_kernel_ignores_entities_without_colliders():
    world = World()
    first = world.create_entity()
    second = world.create_entity()
    no_collider = world.create_entity()
    world.add_resource(CollisionFrame())

    world.add_component(first, Transform(Vec2(0.0, 0.0)))
    world.add_component(first, CircleCollider(5.0))
    world.add_component(second, Transform(Vec2(8.0, 0.0)))
    world.add_component(second, CircleCollider(5.0))
    world.add_component(no_collider, Transform(Vec2(4.0, 0.0)))

    PythonCollisionDetectionKernel().detect(world)

    contacts = world.get_resource(CollisionFrame).contacts
    assert len(contacts) == 1
    assert {contacts[0].entity_a, contacts[0].entity_b} == {first, second}


def test_python_kernel_detects_sensor_contacts():
    world = World()
    first = world.create_entity()
    second = world.create_entity()
    world.add_resource(CollisionFrame())

    world.add_component(first, Transform(Vec2(0.0, 0.0)))
    world.add_component(first, CircleCollider(5.0, is_sensor=True))
    world.add_component(second, Transform(Vec2(8.0, 0.0)))
    world.add_component(second, CircleCollider(5.0))

    PythonCollisionDetectionKernel().detect(world)

    assert len(world.get_resource(CollisionFrame).contacts) == 1


def test_system_delegates_one_batch_call_to_injected_kernel():
    world = World()
    calls = []

    class RecordingKernel:
        def detect(self, kernel_world):
            calls.append(kernel_world)

    system = CollisionDetectionSystem(kernel=RecordingKernel())
    ctx = SimpleNamespace(world=world)

    system.step(ctx)

    assert calls == [world]
