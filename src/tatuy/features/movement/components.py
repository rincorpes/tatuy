from __future__ import annotations

from dataclasses import dataclass, field

from tatuy.math.vec2 import Vec2


@dataclass
class Velocity:
    value: Vec2 = field(default_factory=Vec2.zero)


@dataclass
class DesiredMovement:
    """
    Direction and intensity an entity wants to move.

    A zero vector means no desired movement.
    Magnitudes between 0 and 1 can represent analog input intensity.
    Magnitudes greater than 1 are clamped by MovementSystem.
    """

    direction: Vec2 = field(default_factory=Vec2.zero)


@dataclass
class Movement:
    speed: float = 38.0
    acceleration: float = 100.0
    deceleration: float | None = None
    max_speed: float | None = None


@dataclass
class MovementControls:
    normalize: bool = True
