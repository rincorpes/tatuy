"""
Module for Vec2 class.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass
class Vec2:
    """
    Simple 2D vector.
    """

    x: float
    y: float

    def __add__(self, other: Vec2 | float) -> Vec2:
        if isinstance(other, (int, float)):
            return Vec2(self.x + other, self.y + other)
        return Vec2(
            self.x + other.x,
            self.y + other.y,
        )

    def __sub__(self, other: Vec2 | float) -> Vec2:
        if isinstance(other, (int, float)):
            return Vec2(self.x - other, self.y - other)
        return Vec2(
            self.x - other.x,
            self.y - other.y,
        )

    def __mul__(self, scalar: float) -> Vec2:
        return Vec2(
            self.x * scalar,
            self.y * scalar,
        )

    def __rmul__(self, scalar: float) -> Vec2:
        return self * scalar

    def __truediv__(self, scalar: float) -> Vec2:
        if scalar == 0:
            raise ZeroDivisionError("Cannot divide Vec2 by zero.")

        return Vec2(
            self.x / scalar,
            self.y / scalar,
        )

    def to_tuple(self) -> tuple[float, float]:
        """
        Convert Vex2 to a tuple.
        """
        return (self.x, self.y)

    @classmethod
    def zero(cls) -> Vec2:
        return Vec2(0, 0)

    def length_squared(self) -> float:
        return self.x * self.x + self.y * self.y

    def length(self) -> float:
        return math.sqrt(self.length_squared())

    def normalized(self) -> Vec2:
        length = self.length()

        if length == 0:
            return Vec2.zero()

        return Vec2(
            self.x / length,
            self.y / length,
        )

    def move_towards(
        self,
        target: Vec2,
        max_delta: float,
    ) -> Vec2:
        delta = target - self

        if delta.length_squared() == 0:
            return target

        if delta.length() <= max_delta:
            return target

        return self + delta.normalized() * max_delta
