from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

from tatuy.geometry.size import Size
from tatuy.math.vec2 import Vec2


@dataclass
class BoxCollider:
    # World-space dimensions, centered on Transform.position.
    size: Size
    is_sensor: bool = False


@dataclass
class CircleCollider:
    radius: float
    is_sensor: bool = False


@dataclass
class PolygonCollider:
    # Vertices relative to Transform.position.
    vertices: tuple[Vec2, ...]
    is_sensor: bool = False

    def __post_init__(self) -> None:
        vertices = self.vertices
        if len(vertices) < 3:
            raise ValueError("Polygon needs at least three vertices")

        if not all(isfinite(v.x) and isfinite(v.y) for v in vertices):
            raise ValueError("Polygon vertices must be finite")

        if len({(v.x, v.y) for v in vertices}) != len(vertices):
            raise ValueError("Polygon vertices must be unique")

        area = sum(
            start.x * vertices[(i + 1) % len(vertices)].y
            - start.y * vertices[(i + 1) % len(vertices)].x
            for i, start in enumerate(vertices)
        )
        if area == 0:
            raise ValueError("Polygon must have nonzero area")

        orientation = 1 if area > 0 else -1
        for i, start in enumerate(vertices):
            edge = vertices[(i + 1) % len(vertices)] - start
            for vertex in vertices:
                offset = vertex - start
                cross = edge.x * offset.y - edge.y * offset.x
                if orientation * cross < -1e-9:
                    raise ValueError(
                        "Collision polygons must be convex "
                        "and perimeter-ordered"
                    )


@dataclass
class CollisionBody:
    # 1 / mass. Zero means collision response cannot move the body.
    inverse_mass: float = 1.0

    # 0 = no rebound; 1 = fully elastic rebound.
    restitution: float = 1.0
