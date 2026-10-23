"""Replaceable collision kernels for performance-sensitive operations."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Protocol

from tatuy.ecs.entity import EntityId
from tatuy.ecs.world import World
from tatuy.features.collision.collider_access import ColliderAccess
from tatuy.features.collision.components import CollisionBody
from tatuy.features.collision.resources import CollisionContact, CollisionFrame
from tatuy.features.collision.velocity_rule import CollisionVelocityRule
from tatuy.features.movement.components import Velocity
from tatuy.features.spatial.components import Transform
from tatuy.geometry.aabb import AABB
from tatuy.geometry.collision import CollisionGeometry
from tatuy.geometry.disk import Disk
from tatuy.geometry.shapes import PolygonGeometry
from tatuy.math.vec2 import Vec2
from tatuy.tooling.profiler import profiler

CollisionShape = AABB | Disk | PolygonGeometry
ColliderRow = tuple[EntityId, CollisionShape]


class CollisionDetectionKernel(Protocol):
    """Detect collisions for one simulation step as a batch operation."""

    def detect(self, world: World) -> None:
        """Populate the world's collision frame for the current step."""


class PythonCollisionDetectionKernel:
    """Reference collision detection implemented with Python ECS queries."""

    def __init__(self) -> None:
        self._colliders = ColliderAccess()
        self._geometry = CollisionGeometry()

    def detect(self, world: World) -> None:
        """Collect colliders, test pairs, and populate CollisionFrame."""
        frame = world.get_resource(CollisionFrame)
        frame.contacts.clear()

        colliders, entities_checked = self._collect_colliders(world)
        pair_tests, contacts = self._detect_contacts(colliders, frame)

        profiler.metric("entities_checked", entities_checked)
        profiler.metric("colliders", len(colliders))
        profiler.metric("pair_tests", pair_tests)
        profiler.metric("contacts", contacts)

    def _collect_colliders(
        self,
        world: World,
    ) -> tuple[list[ColliderRow], int]:
        colliders: list[ColliderRow] = []
        entities_checked = 0

        with profiler.span("collect_colliders", "collision"):
            for entity, transform in world.query(Transform):
                entities_checked += 1
                collider = self._colliders.find(world, entity)
                if collider is None:
                    continue

                shape = self._colliders.shape(transform.position, collider)
                colliders.append((entity, shape))

            colliders.sort(key=lambda row: row[0])

        return colliders, entities_checked

    def _detect_contacts(
        self,
        colliders: list[ColliderRow],
        frame: CollisionFrame,
    ) -> tuple[int, int]:
        pair_tests = 0
        contacts = 0

        with profiler.span("test_pairs", "collision"):
            for first, second in combinations(colliders, 2):
                pair_tests += 1
                entity_a, shape_a = first
                entity_b, shape_b = second

                result = self._geometry.find(shape_a, shape_b)
                if result is None:
                    continue

                contacts += 1
                normal, penetration = result
                frame.contacts.append(
                    CollisionContact(
                        entity_a=entity_a,
                        entity_b=entity_b,
                        normal=normal,
                        penetration=penetration,
                    )
                )

        return pair_tests, contacts


@dataclass(frozen=True)
class _ResponsePair:
    transform_a: Transform
    transform_b: Transform
    body_a: CollisionBody
    body_b: CollisionBody
    velocity_a: Velocity
    velocity_b: Velocity


class CollisionResponseKernel(Protocol):
    """Resolve detected collision contacts as one batch operation."""

    def respond(self, world: World) -> None:
        """Apply physical response for the current collision frame."""


class PythonCollisionResponseKernel:
    """Reference collision response with optional Python velocity rules."""

    def __init__(
        self,
        velocity_rules: tuple[CollisionVelocityRule, ...] = (),
    ) -> None:
        self._velocity_rules = velocity_rules
        self._colliders = ColliderAccess()

    def respond(self, world: World) -> None:
        """Resolve all eligible contacts in the current collision frame."""
        frame = world.get_resource(CollisionFrame)

        for contact in frame.contacts:
            self._respond_contact(world, contact)

    def _respond_contact(
        self,
        world: World,
        contact: CollisionContact,
    ) -> None:
        pair = self._response_pair(world, contact)
        if pair is None:
            return

        masses = self._separate_pair(pair, contact)
        if masses is None:
            return

        self._resolve_velocity(world, contact, pair, masses)

    def _separate_pair(
        self,
        pair: _ResponsePair,
        contact: CollisionContact,
    ) -> tuple[float, float, float] | None:
        inverse_mass_a = pair.body_a.inverse_mass
        inverse_mass_b = pair.body_b.inverse_mass
        total_inverse_mass = inverse_mass_a + inverse_mass_b
        if total_inverse_mass == 0:
            return None

        correction = contact.penetration / total_inverse_mass
        normal = contact.normal
        pair.transform_a.position.x -= normal.x * correction * inverse_mass_a
        pair.transform_a.position.y -= normal.y * correction * inverse_mass_a
        pair.transform_b.position.x += normal.x * correction * inverse_mass_b
        pair.transform_b.position.y += normal.y * correction * inverse_mass_b
        return inverse_mass_a, inverse_mass_b, total_inverse_mass

    def _resolve_velocity(
        self,
        world: World,
        contact: CollisionContact,
        pair: _ResponsePair,
        masses: tuple[float, float, float],
    ) -> None:
        normal_speed = self._normal_speed(pair, contact.normal)
        if normal_speed >= 0:
            return

        if self._apply_velocity_rule(world, contact, pair):
            return

        self._apply_impulse(pair, contact.normal, normal_speed, masses)

    def _normal_speed(self, pair: _ResponsePair, normal: Vec2) -> float:
        velocity_a = pair.velocity_a.value
        velocity_b = pair.velocity_b.value
        relative_x = velocity_b.x - velocity_a.x
        relative_y = velocity_b.y - velocity_a.y
        return relative_x * normal.x + relative_y * normal.y

    def _apply_velocity_rule(
        self,
        world: World,
        contact: CollisionContact,
        pair: _ResponsePair,
    ) -> bool:
        for rule in self._velocity_rules:
            replacement = rule.resolve(world, contact)
            if replacement is None:
                continue

            pair.velocity_a.value = replacement.a
            pair.velocity_b.value = replacement.b
            return True

        return False

    def _apply_impulse(
        self,
        pair: _ResponsePair,
        normal: Vec2,
        normal_speed: float,
        masses: tuple[float, float, float],
    ) -> None:
        inverse_mass_a, inverse_mass_b, total_inverse_mass = masses
        restitution = min(pair.body_a.restitution, pair.body_b.restitution)
        impulse = -(1.0 + restitution) * normal_speed / total_inverse_mass
        velocity_a = pair.velocity_a.value
        velocity_b = pair.velocity_b.value
        velocity_a.x -= normal.x * impulse * inverse_mass_a
        velocity_a.y -= normal.y * impulse * inverse_mass_a
        velocity_b.x += normal.x * impulse * inverse_mass_b
        velocity_b.y += normal.y * impulse * inverse_mass_b

    def _response_pair(
        self,
        world: World,
        contact: CollisionContact,
    ) -> _ResponsePair | None:
        entities = (contact.entity_a, contact.entity_b)
        required = (Transform, CollisionBody, Velocity)
        if not all(
            world.has_component(entity, component)
            for entity in entities
            for component in required
        ):
            return None

        collider_a = self._colliders.get(world, contact.entity_a)
        collider_b = self._colliders.get(world, contact.entity_b)
        if collider_a.is_sensor or collider_b.is_sensor:
            return None

        return _ResponsePair(
            transform_a=world.get_component(contact.entity_a, Transform),
            transform_b=world.get_component(contact.entity_b, Transform),
            body_a=world.get_component(contact.entity_a, CollisionBody),
            body_b=world.get_component(contact.entity_b, CollisionBody),
            velocity_a=world.get_component(contact.entity_a, Velocity),
            velocity_b=world.get_component(contact.entity_b, Velocity),
        )
