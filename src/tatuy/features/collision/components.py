from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
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


@lru_cache(maxsize=256)
def _validate_polygon(
    vertices: tuple[tuple[float, float], ...],
) -> None:
    if len(vertices) < 3:
        raise ValueError("Polygon needs at least three vertices")

    if not all(isfinite(x) and isfinite(y) for x, y in vertices):
        raise ValueError("Polygon vertices must be finite")

    if len(set(vertices)) != len(vertices):
        raise ValueError("Polygon vertices must be unique")

    area = sum(
        x * vertices[(i + 1) % len(vertices)][1]
        - y * vertices[(i + 1) % len(vertices)][0]
        for i, (x, y) in enumerate(vertices)
    )

    if area == 0:
        raise ValueError("Polygon must have nonzero area")

    orientation = 1 if area > 0 else -1

    for i, (sx, sy) in enumerate(vertices):
        ex, ey = vertices[(i + 1) % len(vertices)]
        edge_x = ex - sx
        edge_y = ey - sy

        for vx, vy in vertices:
            offset_x = vx - sx
            offset_y = vy - sy

            cross = edge_x * offset_y - edge_y * offset_x

            if orientation * cross < -1e-9:
                raise ValueError(
                    "Collision polygons must be convex "
                    "and perimeter-ordered"
                )


@dataclass
class PolygonCollider:
    # Vertices relative to Transform.position.
    vertices: tuple[Vec2, ...]
    is_sensor: bool = False

    def __post_init__(self) -> None:
        _validate_polygon(
            tuple((vertex.x, vertex.y) for vertex in self.vertices)
        )


@dataclass
class CollisionBody:
    # 1 / mass. Zero means collision response cannot move the body.
    inverse_mass: float = 1.0

    # 0 = no rebound; 1 = fully elastic rebound.
    restitution: float = 1.0
