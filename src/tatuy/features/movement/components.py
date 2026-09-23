from __future__ import annotations

from dataclasses import dataclass

from tatuy.input.keys import Key
from tatuy.math.vec2 import Vec2


@dataclass
class Velocity:
    value: Vec2  # Projected velocity, for presentation/debug compatibility.


@dataclass
class Movement:
    speed: float = 38.0
    acceleration: float = 100.0
    max_speed: float | None = None


@dataclass
class MovementControls:
    up: Key | None = None
    down: Key | None = None
    left: Key | None = None
    right: Key | None = None

    normalize: bool = True
