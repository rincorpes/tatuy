from __future__ import annotations

from dataclasses import dataclass

from tatuy.geometry.size import Size
from tatuy.math.vec2 import Vec2


@dataclass
class AABB:
    center: Vec2
    size: Size

    def overlaps(self, other: AABB) -> bool:
        dx = self.center.x - other.center.x
        dy = self.center.y - other.center.y

        combined_half_width = (self.size.width + other.size.width) / 2

        combined_half_height = (self.size.height + other.size.height) / 2

        return abs(dx) < combined_half_width and abs(dy) < combined_half_height


def find_aabb_contact(
    first: AABB,
    second: AABB,
) -> tuple[Vec2, float] | None:
    """Return the normal from first to second and penetration depth."""
    dx = second.center.x - first.center.x
    dy = second.center.y - first.center.y

    penetration_x = (first.size.width + second.size.width) / 2 - abs(dx)
    penetration_y = (first.size.height + second.size.height) / 2 - abs(dy)

    # Touching edges alone do not count as penetration.
    if penetration_x <= 0 or penetration_y <= 0:
        return None

    # Separate along the axis requiring the least movement.
    if penetration_x < penetration_y:
        normal = Vec2(
            1.0 if dx >= 0 else -1.0,
            0.0,
        )
        return normal, penetration_x

    normal = Vec2(
        0.0,
        1.0 if dy >= 0 else -1.0,
    )
    return normal, penetration_y
