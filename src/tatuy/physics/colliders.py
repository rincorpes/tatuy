from __future__ import annotations

from tatuy.ecs.entity import EntityId
from tatuy.ecs.world import World
from tatuy.features.collision.components import (
    BoxCollider,
    CircleCollider,
    PolygonCollider,
)
from tatuy.features.spatial.components import Transform
from tatuy.geometry.aabb import AABB
from tatuy.geometry.disk import Disk
from tatuy.geometry.shapes import (
    CircleGeometry,
    PolygonGeometry,
    RectangleGeometry,
    ShapeGeometry,
)
from tatuy.math.vec2 import Vec2

Collider = BoxCollider | CircleCollider | PolygonCollider


class ColliderAccess:

    def find(
        self,
        world: World,
        entity: EntityId,
    ) -> Collider | None:
        found: list[Collider] = []

        for collider_type in (
            BoxCollider,
            CircleCollider,
            PolygonCollider,
        ):
            if world.has_component(entity, collider_type):
                found.append(world.get_component(entity, collider_type))

        if len(found) > 1:
            raise ValueError(f"Entity {entity} has multiple collider shapes")

        return found[0] if found else None

    def get(
        self,
        world: World,
        entity: EntityId,
    ) -> Collider:
        collider = self.find(world, entity)

        if collider is None:
            raise ValueError(f"Entity {entity} has no collider")

        return collider

    def half_extents(
        self,
        collider: BoxCollider | CircleCollider,
    ) -> Vec2:
        if isinstance(collider, CircleCollider):
            if collider.radius <= 0:
                raise ValueError("Circle radius must be positive")

            return Vec2(collider.radius, collider.radius)

        if collider.size.width <= 0 or collider.size.height <= 0:
            raise ValueError("Box dimensions must be positive")

        return Vec2(
            collider.size.width / 2,
            collider.size.height / 2,
        )

    def shape(
        self,
        position: Vec2,
        collider: BoxCollider | CircleCollider,
    ) -> AABB | Disk:
        self.half_extents(collider)  # Validate dimensions.

        if isinstance(collider, CircleCollider):
            return Disk(position, collider.radius)

        return AABB(position, collider.size)

    def geometry(
        self,
        world: World,
        entity: EntityId,
    ) -> ShapeGeometry:
        collider = self.get(world, entity)
        position = world.get_component(entity, Transform).position

        if isinstance(collider, CircleCollider):
            return CircleGeometry(
                center=position,
                radius=collider.radius,
            )

        if isinstance(collider, BoxCollider):
            return RectangleGeometry(
                center=position,
                half_width=collider.size.width / 2,
                half_height=collider.size.height / 2,
            )

        if isinstance(collider, PolygonCollider):
            return PolygonGeometry(
                world_vertices=tuple(
                    position + vertex for vertex in collider.vertices
                )
            )

        raise TypeError("Unsupported collider")
