from __future__ import annotations

from tatuy.geometry.aabb import AABB, find_aabb_contact
from tatuy.geometry.disk import Disk
from tatuy.math.scalar import clamp
from tatuy.math.vec2 import Vec2


class CollisionGeometry:
    def find(
        self,
        first: AABB | Disk,
        second: AABB | Disk,
    ) -> tuple[Vec2, float] | None:
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
