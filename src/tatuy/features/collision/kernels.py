"""Replaceable collision kernels for performance-sensitive operations."""

from __future__ import annotations

from itertools import combinations
from typing import Protocol

from tatuy.ecs.entity import EntityId
from tatuy.ecs.world import World
from tatuy.features.collision.collider_access import ColliderAccess
from tatuy.features.collision.resources import CollisionContact, CollisionFrame
from tatuy.features.spatial.components import Transform
from tatuy.geometry.aabb import AABB
from tatuy.geometry.collision import CollisionGeometry
from tatuy.geometry.disk import Disk
from tatuy.geometry.shapes import PolygonGeometry
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
