from __future__ import annotations

from itertools import combinations

from tatuy.ecs.system import BaseSystem, SystemPhase
from tatuy.ecs.world import TWorld
from tatuy.features.collision.components import (
    BoxCollider,
    CircleCollider,
    CollisionBody,
)
from tatuy.features.collision.resources import CollisionContact, CollisionFrame
from tatuy.features.movement.components import (
    DesiredMovement,
    MovementControls,
    Velocity,
)
from tatuy.features.spatial.components import Transform
from tatuy.geometry.collision import CollisionGeometry
from tatuy.physics.colliders import ColliderAccess
from tatuy.physics.response import CollisionVelocityRule
from tatuy.scenes.context import SceneTickContext, TContext, TIntent


class CollisionDetectionSystem(BaseSystem[TContext]):
    phase = SystemPhase.SIMULATION

    def __init__(self) -> None:
        self._colliders = ColliderAccess()
        self._geometry = CollisionGeometry()

    def step(
        self,
        ctx: SceneTickContext[TWorld, TIntent],
    ) -> None:
        frame = ctx.world.get_resource(CollisionFrame)
        frame.contacts.clear()

        colliders = []

        for entity, transform in ctx.world.query(Transform):
            collider = self._colliders.find(
                ctx.world,
                entity,
            )

            if collider is None:
                continue

            if not isinstance(
                collider,
                (BoxCollider, CircleCollider),
            ):
                raise NotImplementedError(
                    "Entity collisions currently support boxes and circles"
                )

            shape = self._colliders.shape(
                transform.position,
                collider,
            )

            colliders.append((entity, shape))

        colliders.sort(key=lambda row: row[0])

        for first, second in combinations(colliders, 2):
            entity_a, shape_a = first
            entity_b, shape_b = second

            result = self._geometry.find(
                shape_a,
                shape_b,
            )

            if result is None:
                continue

            normal, penetration = result

            frame.contacts.append(
                CollisionContact(
                    entity_a=entity_a,
                    entity_b=entity_b,
                    normal=normal,
                    penetration=penetration,
                )
            )


class CollisionResponseSystem(BaseSystem[TContext]):
    def __init__(
        self,
        velocity_rules: tuple[CollisionVelocityRule, ...] = (),
    ) -> None:
        self._velocity_rules = velocity_rules
        self._colliders = ColliderAccess()

    def step(
        self,
        ctx: SceneTickContext[TWorld, TIntent],
    ) -> None:
        world = ctx.world
        frame = world.get_resource(CollisionFrame)

        for contact in frame.contacts:
            entity_a = contact.entity_a
            entity_b = contact.entity_b

            # Detection also supports entities without physical bodies.
            required = (
                Transform,
                CollisionBody,
                Velocity,
            )
            if not all(
                world.has_component(entity, component)
                for entity in (entity_a, entity_b)
                for component in required
            ):
                continue

            collider_a = self._colliders.get(world, entity_a)
            collider_b = self._colliders.get(world, entity_b)

            if collider_a.is_sensor or collider_b.is_sensor:
                continue

            transform_a = world.get_component(entity_a, Transform)
            transform_b = world.get_component(entity_b, Transform)

            body_a = world.get_component(entity_a, CollisionBody)
            body_b = world.get_component(entity_b, CollisionBody)

            velocity_a = world.get_component(entity_a, Velocity).value
            velocity_b = world.get_component(entity_b, Velocity).value

            inverse_mass_a = body_a.inverse_mass
            inverse_mass_b = body_b.inverse_mass
            total_inverse_mass = inverse_mass_a + inverse_mass_b

            # Two immovable bodies cannot be separated by this solver.
            if total_inverse_mass == 0:
                continue

            normal = contact.normal

            # First remove the overlap. Lighter bodies move farther.
            correction = contact.penetration / total_inverse_mass

            transform_a.position.x -= normal.x * correction * inverse_mass_a
            transform_a.position.y -= normal.y * correction * inverse_mass_a

            transform_b.position.x += normal.x * correction * inverse_mass_b
            transform_b.position.y += normal.y * correction * inverse_mass_b

            # Relative velocity along the contact normal.
            relative_x = velocity_b.x - velocity_a.x
            relative_y = velocity_b.y - velocity_a.y
            normal_speed = relative_x * normal.x + relative_y * normal.y

            # Correct penetration, but do not bounce bodies that
            # are already moving apart.
            if normal_speed >= 0:
                continue

            replacement = None

            for rule in self._velocity_rules:
                replacement = rule.resolve(world, contact)

                if replacement is not None:
                    break

            if replacement is not None:
                world.get_component(entity_a, Velocity).value = replacement.a

                world.get_component(entity_b, Velocity).value = replacement.b

                continue

            restitution = min(
                body_a.restitution,
                body_b.restitution,
            )

            impulse = -(1.0 + restitution) * normal_speed / total_inverse_mass

            velocity_a.x -= normal.x * impulse * inverse_mass_a
            velocity_a.y -= normal.y * impulse * inverse_mass_a

            velocity_b.x += normal.x * impulse * inverse_mass_b
            velocity_b.y += normal.y * impulse * inverse_mass_b


class CollisionDirectionSystem(BaseSystem[TContext]):
    phase = SystemPhase.SIMULATION

    def step(self, ctx: SceneTickContext[TWorld, TIntent]):
        frame = ctx.world.get_resource(CollisionFrame)

        for contact in frame.contacts:
            for entity in (contact.entity_a, contact.entity_b):
                if ctx.world.has_component(entity, MovementControls):
                    continue

                if not ctx.world.has_component(entity, DesiredMovement):
                    continue

                velocity = ctx.world.get_component(entity, Velocity)
                desired = ctx.world.get_component(entity, DesiredMovement)

                if velocity.value.length_squared() > 0:
                    desired.direction = velocity.value.normalized()
