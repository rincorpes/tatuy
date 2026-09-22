from __future__ import annotations

from tatuy.geometry.bounds import Bounds, BoundsSide, has_any_side


class BoundsBorderGeometry:

    def resolve(
        self, bounds: Bounds, thickness: int, sides: BoundsSide
    ) -> tuple[Bounds, ...]:
        if thickness < 0:
            raise ValueError("Border thickness cannot be negative")

        if thickness == 0 or sides == BoundsSide.NONE:
            return ()

        if bounds.width <= 0 or bounds.height <= 0:
            raise ValueError("Bounds must have positive dimensions")

        strips: list[Bounds] = []

        if has_any_side(sides, BoundsSide.LEFT):
            strips.append(
                Bounds(
                    left=bounds.left - thickness,
                    top=bounds.top,
                    right=bounds.left,
                    bottom=bounds.bottom,
                )
            )

        if has_any_side(sides, BoundsSide.RIGHT):
            strips.append(
                Bounds(
                    left=bounds.right,
                    top=bounds.top,
                    right=bounds.right + thickness,
                    bottom=bounds.bottom,
                )
            )

        # Horizontal strips include the corners belonging to
        # enabled vertical sides.
        left = bounds.left
        right = bounds.right

        if has_any_side(sides, BoundsSide.LEFT):
            left -= thickness

        if has_any_side(sides, BoundsSide.RIGHT):
            right += thickness

        if has_any_side(sides, BoundsSide.TOP):
            strips.append(
                Bounds(
                    left=left,
                    top=bounds.top - thickness,
                    right=right,
                    bottom=bounds.top,
                )
            )

        if has_any_side(sides, BoundsSide.BOTTOM):
            strips.append(
                Bounds(
                    left=left,
                    top=bounds.bottom,
                    right=right,
                    bottom=bounds.bottom + thickness,
                )
            )

        return tuple(strips)
