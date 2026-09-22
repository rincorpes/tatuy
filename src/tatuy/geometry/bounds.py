from dataclasses import dataclass
from enum import Flag, auto

from tatuy.geometry.shapes import ShapeGeometry
from tatuy.geometry.size import Size
from tatuy.math.vec2 import Vec2


@dataclass(frozen=True)
class Bounds:
    left: float
    top: float
    right: float
    bottom: float

    @property
    def width(self) -> float:
        return self.right - self.left

    @property
    def height(self) -> float:
        return self.bottom - self.top

    @property
    def size(self) -> Size:
        return Size(int(self.width), int(self.height))

    @property
    def center(self) -> Vec2:
        return Vec2(
            self.left + self.width / 2,
            self.top + self.height / 2,
        )


class BoundsSide(Flag):
    NONE = 0

    LEFT = auto()
    RIGHT = auto()
    TOP = auto()
    BOTTOM = auto()

    HORIZONTAL = LEFT | RIGHT
    VERTICAL = TOP | BOTTOM
    ALL = LEFT | RIGHT | TOP | BOTTOM


class BoundsQuery:
    def __init__(self) -> None:
        self._contacts = BoundsContactQuery()

    def contains_point(
        self,
        bounds: Bounds,
        point: Vec2,
    ) -> bool:
        return (
            bounds.left <= point.x <= bounds.right
            and bounds.top <= point.y <= bounds.bottom
        )

    def contains_shape(
        self,
        bounds: Bounds,
        shape: ShapeGeometry,
    ) -> bool:
        return (
            shape.support(Vec2(-1, 0)).x >= bounds.left
            and shape.support(Vec2(1, 0)).x <= bounds.right
            and shape.support(Vec2(0, -1)).y >= bounds.top
            and shape.support(Vec2(0, 1)).y <= bounds.bottom
        )

    def touching_sides(
        self,
        bounds: Bounds,
        shape: ShapeGeometry,
        *,
        sides: BoundsSide = BoundsSide.ALL,
    ) -> BoundsSide:
        mask = BoundsSide.NONE

        for contact in self._contacts.contacts(
            bounds,
            shape,
            sides=sides,
        ):
            mask = BoundsSide(mask.value | contact.side.value)

        return mask

    def outside_sides(
        self,
        bounds: Bounds,
        shape: ShapeGeometry,
        *,
        sides: BoundsSide = BoundsSide.ALL,
    ) -> BoundsSide:
        exited = (
            (
                BoundsSide.LEFT,
                shape.support(Vec2(1, 0)).x < bounds.left,
            ),
            (
                BoundsSide.RIGHT,
                shape.support(Vec2(-1, 0)).x > bounds.right,
            ),
            (
                BoundsSide.TOP,
                shape.support(Vec2(0, 1)).y < bounds.top,
            ),
            (
                BoundsSide.BOTTOM,
                shape.support(Vec2(0, -1)).y > bounds.bottom,
            ),
        )

        mask = BoundsSide.NONE

        for side, is_outside in exited:
            if is_outside and has_any_side(sides, side):
                mask = BoundsSide(mask.value | side.value)

        return mask


def has_any_side(mask: BoundsSide, sides: BoundsSide) -> bool:
    return (mask.value & sides.value) != 0


@dataclass(frozen=True)
class BoundsContact:
    side: BoundsSide
    normal: Vec2
    penetration: float
    point: Vec2


class BoundsContactQuery:
    def contacts(
        self,
        bounds: Bounds,
        shape: ShapeGeometry,
        *,
        sides: BoundsSide = BoundsSide.ALL,
    ) -> tuple[BoundsContact, ...]:
        if bounds.width <= 0 or bounds.height <= 0:
            raise ValueError("Bounds must have positive dimensions")

        # Opposing walls require room for the shape to move.
        if (
            has_any_side(sides, BoundsSide.LEFT)
            and has_any_side(sides, BoundsSide.RIGHT)
            and (shape.support(Vec2(1, 0)).x - shape.support(Vec2(-1, 0)).x)
            >= bounds.width
        ):
            raise ValueError("Shape needs horizontal clearance")

        if (
            has_any_side(sides, BoundsSide.TOP)
            and has_any_side(sides, BoundsSide.BOTTOM)
            and (shape.support(Vec2(0, 1)).y - shape.support(Vec2(0, -1)).y)
            >= bounds.height
        ):
            raise ValueError("Shape needs vertical clearance")

        # Normals point inward into the playable area.
        walls = (
            (BoundsSide.LEFT, Vec2(1, 0), bounds.left),
            (BoundsSide.RIGHT, Vec2(-1, 0), -bounds.right),
            (BoundsSide.TOP, Vec2(0, 1), bounds.top),
            (BoundsSide.BOTTOM, Vec2(0, -1), -bounds.bottom),
        )

        result: list[BoundsContact] = []

        for side, normal, limit in walls:
            if not has_any_side(sides, side):
                continue

            point = shape.support(normal * -1)
            projection = point.x * normal.x + point.y * normal.y
            penetration = limit - projection

            if penetration >= 0:
                result.append(
                    BoundsContact(
                        side=side,
                        normal=normal,
                        penetration=penetration,
                        point=point,
                    )
                )

        return tuple(result)


class BoundsClamp:

    def __init__(self) -> None:
        self._contacts = BoundsContactQuery()

    def apply(
        self,
        bounds: Bounds,
        position: Vec2,
        shape: ShapeGeometry,
        *,
        sides: BoundsSide = BoundsSide.ALL,
    ) -> Vec2:
        result = Vec2(position.x, position.y)

        for contact in self._contacts.contacts(
            bounds,
            shape,
            sides=sides,
        ):
            result = result + contact.normal * contact.penetration

        return result


@dataclass(frozen=True)
class BoundsBounceResult:
    position: Vec2
    velocity: Vec2

    # All detected contact sides.
    sides: BoundsSide

    # Only sides that reflected approaching motion.
    bounced_sides: BoundsSide = BoundsSide.NONE


class BoundsBounce:

    def __init__(self) -> None:
        self._contacts = BoundsContactQuery()

    def apply(
        self,
        bounds: Bounds,
        position: Vec2,
        shape: ShapeGeometry,
        velocity: Vec2,
        *,
        sides: BoundsSide = BoundsSide.ALL,
    ) -> BoundsBounceResult:
        result_position = Vec2(position.x, position.y)
        result_velocity = Vec2(velocity.x, velocity.y)

        contact_mask = BoundsSide.NONE
        bounced_mask = BoundsSide.NONE

        for contact in self._contacts.contacts(
            bounds,
            shape,
            sides=sides,
        ):
            result_position = (
                result_position + contact.normal * contact.penetration
            )

            contact_mask = BoundsSide(contact_mask.value | contact.side.value)

            normal_speed = (
                result_velocity.x * contact.normal.x
                + result_velocity.y * contact.normal.y
            )

            if normal_speed < 0:
                result_velocity = result_velocity - contact.normal * (
                    2 * normal_speed
                )

                bounced_mask = BoundsSide(
                    bounced_mask.value | contact.side.value
                )

        return BoundsBounceResult(
            position=result_position,
            velocity=result_velocity,
            sides=contact_mask,
            bounced_sides=bounced_mask,
        )


@dataclass(frozen=True)
class BoundsWrapResult:
    position: Vec2
    sides: BoundsSide


class BoundsWrap:

    def __init__(self) -> None:
        self._query = BoundsQuery()

    def apply(
        self,
        bounds: Bounds,
        position: Vec2,
        shape: ShapeGeometry,
        *,
        sides: BoundsSide = BoundsSide.ALL,
    ) -> BoundsWrapResult:
        outside = self._query.outside_sides(
            bounds,
            shape,
            sides=sides,
        )

        result = Vec2(position.x, position.y)

        if has_any_side(outside, BoundsSide.LEFT):
            result.x += bounds.right - shape.support(Vec2(-1, 0)).x

        elif has_any_side(outside, BoundsSide.RIGHT):
            result.x += bounds.left - shape.support(Vec2(1, 0)).x

        if has_any_side(outside, BoundsSide.TOP):
            result.y += bounds.bottom - shape.support(Vec2(0, -1)).y

        elif has_any_side(outside, BoundsSide.BOTTOM):
            result.y += bounds.top - shape.support(Vec2(0, 1)).y

        return BoundsWrapResult(
            position=result,
            sides=outside,
        )
