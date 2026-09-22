from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Literal, TypeVar

from tatuy.geometry.bounds import BoundsSide
from tatuy.geometry.size import Size
from tatuy.graphics.color import Color
from tatuy.graphics.render.queue import Layer
from tatuy.input.keys import Key
from tatuy.math.vec2 import Vec2

TComponent = TypeVar("TComponent")


@dataclass
class Transform:
    position: Vec2  # Center position of an entity, used for rendering and physics calculations.
    scale: float = 1.0


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


@dataclass
class Rect:
    size: Size
    color: Color
    layer: Layer = "world"
    z: int = 0
    visible: bool = True


@dataclass
class Text:
    color: Color
    content: str = ""
    font_size: int = 16
    align: Literal["left", "center", "right"] = "left"
    valign: Literal["top", "middle", "bottom"] = "top"
    z: int = 0
    layer: Layer = "ui"
    visible: bool = True


@dataclass
class Circle:
    radius: float
    color: Color
    layer: Layer = "world"
    z: int = 0
    visible: bool = True


class BoundsBehavior(Enum):
    NONE = auto()
    CLAMP = auto()
    BOUNCE = auto()
    WRAP = auto()
    DESPAWN = auto()


@dataclass
class BoundsConstraint:
    behavior: BoundsBehavior
    sides: BoundsSide = BoundsSide.ALL


@dataclass(frozen=True)
class SpawnOrigin:
    definition: str


class DespawnReason(Enum):
    OUT_OF_BOUNDS = auto()
    LIFETIME_EXPIRED = auto()
    DEFEATED = auto()
    SCRIPTED = auto()


@dataclass(frozen=True)
class Respawn:
    delay: float = 2.0
    reasons: frozenset[DespawnReason] = frozenset(
        {
            DespawnReason.OUT_OF_BOUNDS,
            DespawnReason.DEFEATED,
        }
    )


@dataclass
class Lifetime:
    remaining: float


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


@dataclass
class PaddleMotionSample:
    start_position: Vec2 | None = None


@dataclass
class Paddle:
    face: BoundsSide
    max_angle_degrees: float = 65.0
    motion_influence: float = 0.25
