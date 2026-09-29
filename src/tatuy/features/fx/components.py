from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

from tatuy.graphics.color import Color
from tatuy.math.vec2 import Vec2


@dataclass
class Particle:
    duration: float
    radius: float
    color: Color
    drag: float = 4.0

    def __post_init__(self):
        if self.duration <= 0:
            raise ValueError("Particle.duration must be positive")


@dataclass
class TrailPoint:
    position: Vec2
    radius: float
    color: Color
    age: float = 0.0


@dataclass
class Trail:
    duration: float = 0.45
    interval: float = 1 / 60

    radius: float = 4.0
    color: Color = (255, 255, 255)

    max_points: int = 64
    enabled: bool = True

    points: deque[TrailPoint] = field(default_factory=deque)
    clock: float = 0.0

    def __post_init__(self):
        if self.duration <= 0:
            raise ValueError("Trail.duration must be positive")

        if self.interval <= 0:
            raise ValueError("Trail.interval must be positive")

        if self.max_points < 1:
            raise ValueError("Trail.max_points must be at least 1")

    def clear(self):
        self.points.clear()
        self.clock = 0.0
