from __future__ import annotations

from dataclasses import dataclass
from math import floor

from tatuy.geometry.bounds import Bounds
from tatuy.geometry.size import Size
from tatuy.math.vec2 import Vec2


@dataclass(frozen=True)
class GridSpec:
    rows: int
    columns: int
    cell_height: int
    cell_width: int | None = None
    gap_x: int = 0
    gap_y: int = 0


@dataclass(frozen=True)
class GridPlacement:
    row: int
    column: int
    center: Vec2
    size: Size


class GridLayout:
    def resolve(
        self,
        area: Bounds,
        spec: GridSpec,
    ) -> tuple[GridPlacement, ...]:
        if spec.rows <= 0 or spec.columns <= 0:
            raise ValueError("Rows and columns must be positive")

        if spec.cell_height <= 0:
            raise ValueError("Cell height must be positive")

        if spec.gap_x < 0 or spec.gap_y < 0:
            raise ValueError("Gaps cannot be negative")

        if area.width <= 0 or area.height <= 0:
            raise ValueError("Grid area must have positive dimensions")

        width = spec.cell_width

        if width is None:
            width = floor(
                (area.width - (spec.columns - 1) * spec.gap_x) / spec.columns
            )

        if width <= 0:
            raise ValueError("Cells have no available width")

        used_width = spec.columns * width + (spec.columns - 1) * spec.gap_x
        used_height = (
            spec.rows * spec.cell_height + (spec.rows - 1) * spec.gap_y
        )

        if used_width > area.width or used_height > area.height:
            raise ValueError("Grid does not fit its area")

        left = area.left + (area.width - used_width) / 2

        return tuple(
            GridPlacement(
                row=row,
                column=column,
                center=Vec2(
                    left + column * (width + spec.gap_x) + width / 2,
                    area.top
                    + row * (spec.cell_height + spec.gap_y)
                    + spec.cell_height / 2,
                ),
                size=Size(width, spec.cell_height),
            )
            for row in range(spec.rows)
            for column in range(spec.columns)
        )
