from types import SimpleNamespace

from tatuy.ecs.world import World
from tatuy.features.collision.components import BoxCollider, CollisionBody
from tatuy.features.collision.kernels import PythonCollisionResponseKernel
from tatuy.features.collision.resources import CollisionContact, CollisionFrame
from tatuy.features.collision.systems import CollisionDirectionSystem
from tatuy.features.collision.velocity_rule import (
    CollisionVelocities,
    CollisionVelocityRule,
)
from tatuy.features.movement.components import (
    DesiredMovement,
    MovementControls,
    Velocity,
)
from tatuy.features.spatial.components import Transform
from tatuy.geometry.size import Size
from tatuy.math.vec2 import Vec2


def _contact_world() -> tuple[World, int, int]:
    world = World()
    frame = world.add_resource(CollisionFrame())
    first = world.create_entity()
    second = world.create_entity()
    frame.contacts.append(
        CollisionContact(
            entity_a=first,
            entity_b=second,
            normal=Vec2(1.0, 0.0),
            penetration=1.0,
        )
    )
    return world, first, second


def test_collision_direction_system_synchronizes_desired_direction():
    world, first, second = _contact_world()
    first_velocity = world.add_component(first, Velocity(Vec2(-3.0, 4.0)))
    first_desired = world.add_component(first, DesiredMovement(Vec2(1.0, 0.0)))
    second_velocity = world.add_component(second, Velocity(Vec2(0.0, -2.0)))
    second_desired = world.add_component(
        second, DesiredMovement(Vec2(0.0, 1.0))
    )

    CollisionDirectionSystem().step(SimpleNamespace(world=world))

    assert first_desired.direction == first_velocity.value.normalized()
    assert second_desired.direction == second_velocity.value.normalized()


def test_collision_direction_system_skips_player_controlled_entities():
    world, first, second = _contact_world()
    world.add_component(first, Velocity(Vec2(-1.0, 0.0)))
    desired = world.add_component(first, DesiredMovement(Vec2(1.0, 0.0)))
    world.add_component(first, MovementControls())
    world.add_component(second, Velocity(Vec2(1.0, 0.0)))

    CollisionDirectionSystem().step(SimpleNamespace(world=world))

    assert desired.direction == Vec2(1.0, 0.0)


def test_collision_velocity_rules_run_in_declared_order_until_one_handles_contact():
    world, first, second = _contact_world()
    for entity, position, velocity in (
        (first, Vec2(0.0, 0.0), Vec2(1.0, 0.0)),
        (second, Vec2(1.0, 0.0), Vec2(-1.0, 0.0)),
    ):
        world.add_component(entity, Transform(position))
        world.add_component(entity, BoxCollider(Size(2, 2)))
        world.add_component(entity, CollisionBody())
        world.add_component(entity, Velocity(velocity))

    calls: list[str] = []

    class FirstRule(CollisionVelocityRule):
        def resolve(self, rule_world, contact):
            calls.append("first")
            return None

    class SecondRule(CollisionVelocityRule):
        def resolve(self, rule_world, contact):
            calls.append("second")
            return CollisionVelocities(Vec2(7.0, 0.0), Vec2(-7.0, 0.0))

    class NeverRule(CollisionVelocityRule):
        def resolve(self, rule_world, contact):
            calls.append("never")
            return CollisionVelocities(Vec2.zero(), Vec2.zero())

    PythonCollisionResponseKernel(
        (FirstRule(), SecondRule(), NeverRule())
    ).respond(world)

    assert calls == ["first", "second"]
    assert world.get_component(first, Velocity).value == Vec2(7.0, 0.0)
    assert world.get_component(second, Velocity).value == Vec2(-7.0, 0.0)
