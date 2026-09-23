from __future__ import annotations

from dataclasses import dataclass

from tatuy.geometry.size import Size
from tatuy.math.vec2 import Vec2


@dataclass
class BoxCollider:
    # World-space dimensions, centered on Transform.position.
    size: Size
    is_sensor: bool = False


@dataclass
class CircleCollider:
    radius: float
    is_sensor: bool = False


@dataclass
class PolygonCollider:
    # Vertices relative to Transform.position.
    vertices: tuple[Vec2, ...]
    is_sensor: bool = False


@dataclass
class CollisionBody:
    # 1 / mass. Zero means collision response cannot move the body.
    inverse_mass: float = 1.0

    # 0 = no rebound; 1 = fully elastic rebound.
    restitution: float = 1.0
