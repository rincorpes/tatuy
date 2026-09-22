from __future__ import annotations

from dataclasses import dataclass
from tatuy.math.vec2 import Vec2


@dataclass
class Disk:
    center: Vec2
    radius: float
