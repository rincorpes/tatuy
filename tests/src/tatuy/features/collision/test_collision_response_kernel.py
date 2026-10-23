from types import SimpleNamespace

import pytest

from tatuy.ecs.world import World
from tatuy.features.collision.components import BoxCollider, CollisionBody
from tatuy.features.collision.kernels import PythonCollisionResponseKernel
from tatuy.features.collision.resources import CollisionContact, CollisionFrame
from tatuy.features.collision.systems import CollisionResponseSystem
from tatuy.features.collision.velocity_rule import (
    CollisionVelocities,
    CollisionVelocityRule,
)
from tatuy.features.movement.components import Velocity
from tatuy.features.spatial.components import Transform
from tatuy.geometry.size import Size
from tatuy.math.vec2 import Vec2


def _make_pair(*, sensor: bool = False):
    world = World()
    world.add_resource(CollisionFrame())
    first = world.create_entity()
    second = world.create_entity()

    world.add_component(first, Transform(Vec2(0.0, 0.0)))
    world.add_component(second, Transform(Vec2(1.0, 0.0)))
    world.add_component(first, BoxCollider(Size(2, 2), is_sensor=sensor))
    world.add_component(second, BoxCollider(Size(2, 2)))
    world.add_component(first, CollisionBody())
    world.add_component(second, CollisionBody())
    world.add_component(first, Velocity(Vec2(1.0, 0.0)))
    world.add_component(second, Velocity(Vec2(-1.0, 0.0)))

    world.get_resource(CollisionFrame).contacts.append(
        CollisionContact(
            entity_a=first,
            entity_b=second,
            normal=Vec2(1.0, 0.0),
            penetration=1.0,
        )
    )
    return world, first, second


def test_python_response_separates_and_applies_impulse():
    world, first, second = _make_pair()

    PythonCollisionResponseKernel().respond(world)

    assert world.get_component(first, Transform).position == Vec2(-0.5, 0.0)
    assert world.get_component(second, Transform).position == Vec2(1.5, 0.0)
    assert world.get_component(first, Velocity).value == Vec2(-1.0, 0.0)
    assert world.get_component(second, Velocity).value == Vec2(1.0, 0.0)


def test_python_response_skips_sensor_contacts():
    world, first, second = _make_pair(sensor=True)

    PythonCollisionResponseKernel().respond(world)

    assert world.get_component(first, Transform).position == Vec2(0.0, 0.0)
    assert world.get_component(second, Transform).position == Vec2(1.0, 0.0)


def test_python_response_uses_custom_velocity_rule_after_separation():
    world, first, second = _make_pair()

    class Rule(CollisionVelocityRule):
        def resolve(self, rule_world, contact):
            assert rule_world is world
            assert contact.entity_a == first
            return CollisionVelocities(Vec2(3.0, 4.0), Vec2(-3.0, -4.0))

    PythonCollisionResponseKernel((Rule(),)).respond(world)

    assert world.get_component(first, Transform).position == Vec2(-0.5, 0.0)
    assert world.get_component(second, Transform).position == Vec2(1.5, 0.0)
    assert world.get_component(first, Velocity).value == Vec2(3.0, 4.0)
    assert world.get_component(second, Velocity).value == Vec2(-3.0, -4.0)


def test_system_delegates_one_batch_call_to_injected_kernel():
    world = World()
    calls = []

    class RecordingKernel:
        def respond(self, kernel_world):
            calls.append(kernel_world)

    system = CollisionResponseSystem(kernel=RecordingKernel())
    system.step(SimpleNamespace(world=world))

    assert calls == [world]


def test_system_rejects_rules_with_custom_kernel():
    class Rule(CollisionVelocityRule):
        def resolve(self, world, contact):
            return None

    class RecordingKernel:
        def respond(self, world):
            pass

    with pytest.raises(ValueError, match="Configure velocity rules"):
        CollisionResponseSystem(
            velocity_rules=(Rule(),),
            kernel=RecordingKernel(),
        )
