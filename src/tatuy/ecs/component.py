from __future__ import annotations

from dataclasses import dataclass
from typing import TypeVar

from tatuy.geometry.bounds import BoundsSide
from tatuy.math.vec2 import Vec2

TComponent = TypeVar("TComponent")


@dataclass
class PaddleMotionSample:
    start_position: Vec2 | None = None


@dataclass
class Paddle:
    face: BoundsSide
    max_angle_degrees: float = 65.0
    motion_influence: float = 0.25
