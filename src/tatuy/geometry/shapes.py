from __future__ import annotations

from abc import ABC, abstractmethod

from tatuy.math.vec2 import Vec2


class ShapeGeometry(ABC):
    @abstractmethod
    def support(self, direction: Vec2) -> Vec2:
        """Return a farthest world-space point in a nonzero direction."""


class CircleGeometry(ShapeGeometry):
    def __init__(self, center: Vec2, radius: float) -> None:
        if radius <= 0:
            raise ValueError("Circle radius must be positive")

        self._center = center
        self._radius = radius

    def support(self, direction: Vec2) -> Vec2:
        if direction.length_squared() == 0:
            raise ValueError("Direction cannot be zero")

        return self._center + direction.normalized() * self._radius


class RectangleGeometry(ShapeGeometry):
    def __init__(
        self,
        center: Vec2,
        half_width: float,
        half_height: float,
    ) -> None:
        if half_width <= 0 or half_height <= 0:
            raise ValueError("Rectangle dimensions must be positive")

        self._center = center
        self._half_width = half_width
        self._half_height = half_height

    def support(self, direction: Vec2) -> Vec2:
        return Vec2(
            self._center.x
            + (self._half_width if direction.x >= 0 else -self._half_width),
            self._center.y
            + (self._half_height if direction.y >= 0 else -self._half_height),
        )


class PolygonGeometry(ShapeGeometry):
    def __init__(self, world_vertices: tuple[Vec2, ...]) -> None:
        if len(world_vertices) < 3:
            raise ValueError("Polygon needs at least three vertices")

        self._vertices = world_vertices

    def support(self, direction: Vec2) -> Vec2:
        return max(
            self._vertices,
            key=lambda vertex: (
                vertex.x * direction.x + vertex.y * direction.y
            ),
        )
