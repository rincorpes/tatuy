from __future__ import annotations

from tatuy.geometry.aabb import AABB, find_aabb_contact
from tatuy.geometry.disk import Disk
from tatuy.geometry.shapes import PolygonGeometry
from tatuy.math.scalar import clamp
from tatuy.math.vec2 import Vec2


class CollisionGeometry:
    def find(
        self,
        first: AABB | Disk | PolygonGeometry,
        second: AABB | Disk,
    ) -> tuple[Vec2, float] | None:
        if isinstance(first, PolygonGeometry) or isinstance(
            second, PolygonGeometry
        ):
            return self._sat(first, second)

        if isinstance(first, Disk):
            if isinstance(second, Disk):
                return self._circle_circle(first, second)

            return self._circle_box(first, second)

        if isinstance(second, Disk):
            result = self._circle_box(second, first)

            if result is None:
                return None

            normal, penetration = result
            return normal * -1, penetration

        # Preserve existing box–box behavior.
        return find_aabb_contact(first, second)

    def _circle_circle(
        self,
        first: Disk,
        second: Disk,
    ) -> tuple[Vec2, float] | None:
        delta = second.center - first.center
        distance = delta.length()
        radius = first.radius + second.radius

        if distance >= radius:
            return None

        normal = delta / distance if distance > 0 else Vec2(1, 0)

        return normal, radius - distance

    def _circle_box(
        self,
        circle: Disk,
        box: AABB,
    ) -> tuple[Vec2, float] | None:
        half_width = box.size.width / 2
        half_height = box.size.height / 2

        left = box.center.x - half_width
        right = box.center.x + half_width
        top = box.center.y - half_height
        bottom = box.center.y + half_height

        closest = Vec2(
            clamp(circle.center.x, left, right),
            clamp(circle.center.y, top, bottom),
        )

        # Normal points from the circle toward the box.
        delta = closest - circle.center
        distance = delta.length()

        if distance > 0:
            if distance >= circle.radius:
                return None

            return (
                delta / distance,
                circle.radius - distance,
            )

        # Circle center is inside or on the box.
        # Separate through its nearest face.
        exits = (
            (circle.center.x - left, Vec2(-1, 0)),
            (right - circle.center.x, Vec2(1, 0)),
            (circle.center.y - top, Vec2(0, -1)),
            (bottom - circle.center.y, Vec2(0, 1)),
        )

        distance_to_face, outward = min(
            exits,
            key=lambda item: item[0],
        )

        return (
            outward * -1,
            circle.radius + distance_to_face,
        )

    def _vertices(
        self,
        shape: AABB | PolygonGeometry,
    ) -> tuple[Vec2, ...]:
        if isinstance(shape, PolygonGeometry):
            return shape.vertices

        x, y = shape.center.x, shape.center.y
        hw = shape.size.width / 2
        hh = shape.size.height / 2
        return (
            Vec2(x - hw, y - hh),
            Vec2(x + hw, y - hh),
            Vec2(x + hw, y + hh),
            Vec2(x - hw, y + hh),
        )

    def _project(
        self,
        shape: AABB | Disk | PolygonGeometry,
        axis: Vec2,
    ) -> tuple[float, float]:
        if isinstance(shape, Disk):
            center = shape.center.dot(axis)
            return center - shape.radius, center + shape.radius

        values = [vertex.dot(axis) for vertex in self._vertices(shape)]
        return min(values), max(values)

    def _sat(
        self,
        first: AABB | Disk | PolygonGeometry,
        second: AABB | Disk | PolygonGeometry,
    ) -> tuple[Vec2, float] | None:
        axes: list[Vec2] = []

        for shape in (first, second):
            if isinstance(shape, Disk):
                continue

            vertices = self._vertices(shape)
            for index, start in enumerate(vertices):
                end = vertices[(index + 1) % len(vertices)]
                edge = end - start
                if edge.length_squared() > 0:
                    axes.append(Vec2(-edge.y, edge.x).normalized())

        # Edge normals alone miss circle-to-corner separation.
        for circle, other in ((first, second), (second, first)):
            if not isinstance(circle, Disk) or isinstance(other, Disk):
                continue

            nearest = min(
                self._vertices(other),
                key=lambda vertex: (vertex - circle.center).length_squared(),
            )
            axis = nearest - circle.center
            if axis.length_squared() > 0:
                axes.append(axis.normalized())

        best_normal = Vec2(1, 0)
        best_depth = float("inf")

        for axis in axes:
            min_a, max_a = self._project(first, axis)
            min_b, max_b = self._project(second, axis)

            # Moving B in either direction until the intervals separate.
            # These distances also handle one shape containing the other.
            positive = max_a - min_b
            negative = max_b - min_a

            if positive <= 0 or negative <= 0:
                return None

            if positive <= negative:
                normal, depth = axis, positive
            else:
                normal, depth = axis * -1, negative

            if depth < best_depth:
                best_normal, best_depth = normal, depth

        return best_normal, best_depth
