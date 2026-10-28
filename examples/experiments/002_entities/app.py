"""Single-file Shatterphase experiment for testing and profiling."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field, fields
from enum import Enum, auto
from html import entities
from math import atan2, ceil, cos, exp, isfinite, radians, sin, sqrt, tau
from random import Random
from typing import Any, Iterator

from tatuy import TatuyApp, TatuyConfigDict
from tatuy.configuration import merge_config
from tatuy.ecs import (
    EntityBlueprint,
    EntityFactory,
    EntityId,
    GameSystem,
    IntersectionQueryStrategy,
    SystemPhase,
    World,
)
from tatuy.engine import SystemRegistration
from tatuy.features.bounds import (
    BoundsBehavior,
    BoundsConstraint,
    BoundsFrame,
    WorldBounds,
    WorldBoundsBorder,
)
from tatuy.features.collision import (
    BoxCollider,
    CircleCollider,
    ColliderAccess,
    CollisionBody,
    CollisionContact,
    CollisionDirectionSystem,
    CollisionFrame,
    CollisionResponseSystem,
    PolygonCollider,
    match_contact,
)
from tatuy.features.fx import (
    CameraFX,
    ParticleBurst,
    ParticleEmitter,
    ParticleUpdateSystem,
    ScreenEffectStack,
    Trail,
    TrailRenderSystem,
    TrailSystem,
)
from tatuy.features.lifecycle import (
    DespawnReason,
    LifecycleQueue,
    Lifetime,
    SpawnDefinition,
    SpawnRegistry,
)
from tatuy.features.movement import (
    DesiredMovement,
    MotionSample,
    Movement,
    MovementControls,
    Velocity,
)
from tatuy.features.spatial import AttachedTo, Transform
from tatuy.features.visual import (
    Circle,
    CircleBlueprint,
    CircleBlueprintAttrs,
    Polygon,
    PolygonBlueprint,
    PolygonBlueprintAttrs,
    Rect,
    RectBlueprint,
    RectBlueprintAttrs,
    Text,
    TextBlueprint,
)
from tatuy.geometry.bounds import Bounds, BoundsSide, BoundsWrap
from tatuy.geometry.collision import CollisionGeometry
from tatuy.geometry.grid import GridLayout, GridSpec
from tatuy.geometry.size import Size
from tatuy.graphics.color import Color
from tatuy.input.keys import Key
from tatuy.math.scalar import clamp
from tatuy.math.vec2 import Vec2
from tatuy.scenes import (
    EntitySpawn,
    Intent,
    Scene,
    SceneRegistry,
    SceneTickContext,
)
from tatuy.settings import DataclassSettings, SettingsBuilder, SettingsRegistry
from tatuy.tooling.profiler import profiler

# Settings


class PowerUpKind(Enum):
    WIDE = auto()
    FAST = auto()
    SLOW = auto()
    MULTIBALL = auto()
    EXTRA_LIFE = auto()
    STICKY = auto()
    SHIELD = auto()


@dataclass(frozen=True)
class EnemyDefinition:
    kind: str
    color: Color
    hits: int = 1
    points: int = 50
    destructible: bool = True


@dataclass(frozen=True)
class EnemyFieldDefinition:
    rows: tuple[EnemyDefinition, ...]
    columns: int = 12
    enemy_radius: int = 20
    gap_x: int = 6
    gap_y: int = 8


@dataclass(frozen=True)
class EnemyColors:
    coral: Color = (255, 92, 114)
    orange: Color = (255, 151, 87)
    yellow: Color = (255, 211, 92)
    green: Color = (91, 210, 147)
    blue: Color = (88, 166, 255)
    purple: Color = (166, 113, 255)


@dataclass(frozen=True)
class TextColor:
    primary: Color = (245, 247, 255)
    secondary: Color = (164, 172, 196)
    accent: Color = (255, 211, 92)


@dataclass(frozen=True)
class ColorSettings:
    enabled: bool = True
    boundary: Color = (78, 86, 112)
    paddle: Color = (80, 220, 210)
    ball: Color = (245, 247, 255)
    bricks: EnemyColors = field(default_factory=EnemyColors)
    text: TextColor = field(default_factory=TextColor)

    def __post_init__(self):
        if not self.enabled:
            object.__setattr__(self, "boundary", (255, 255, 255))
            object.__setattr__(self, "paddle", (255, 255, 255))
            object.__setattr__(self, "ball", (255, 255, 255))

            for brick_color in fields(self.bricks):
                object.__setattr__(
                    self.bricks, brick_color.name, (255, 255, 255)
                )

            for text_color in fields(self.text):
                object.__setattr__(self.text, text_color.name, (255, 255, 255))


def _require_number(
    name: str,
    value: float,
    *,
    minimum: float = 0.0,
    maximum: float | None = None,
    positive: bool = False,
) -> None:
    if type(value) not in (int, float) or not isfinite(value):
        raise ValueError(f"{name} must be a finite number")
    if value < minimum or (positive and value == minimum):
        comparison = ">" if positive else ">="
        raise ValueError(f"{name} must be {comparison} {minimum}")
    if maximum is not None and value > maximum:
        raise ValueError(f"{name} must be <= {maximum}")


def _require_integer(name: str, value: int, minimum: int = 1) -> None:
    if type(value) is not int or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")


@dataclass(frozen=True)
class SpinSettings:
    enabled: bool = True
    curve_enabled: bool = True

    impact_strength: float = 28.0
    maximum: float = 50.0
    minimum_paddle_speed: float = 10.0

    decay: float = 0.8
    curve_strength: float = 0.10

    clear_on_bounds_bounce: bool = True
    prevent_vertical_reversal: bool = True

    @property
    def curve_active(self) -> bool:
        return self.enabled and self.curve_enabled

    def __post_init__(self) -> None:
        for name in (
            "impact_strength",
            "maximum",
            "minimum_paddle_speed",
            "decay",
            "curve_strength",
        ):
            _require_number(f"ball.spin.{name}", getattr(self, name))


@dataclass(frozen=True)
class BallSettings:
    radius: float = 7.5

    launch_speed: float = 450.0
    minimum_speed: float = 350.0
    maximum_speed: float = 550.0

    inherit_paddle_velocity: bool = True
    launch_inheritance: float = 0.35
    launch_spread_degrees: float = 15.0

    minimum_angle_enabled: bool = True
    minimum_vertical_angle: float = 18.0

    spin: SpinSettings = field(default_factory=SpinSettings)

    def __post_init__(self) -> None:
        for name in (
            "radius",
            "launch_speed",
            "minimum_speed",
            "maximum_speed",
        ):
            _require_number(f"ball.{name}", getattr(self, name), positive=True)
        if not self.minimum_speed <= self.launch_speed <= self.maximum_speed:
            raise ValueError(
                "ball speeds must satisfy minimum <= launch <= maximum"
            )
        _require_number("ball.launch_inheritance", self.launch_inheritance)
        _require_number(
            "ball.launch_spread_degrees",
            self.launch_spread_degrees,
            maximum=90.0,
        )
        _require_number(
            "ball.minimum_vertical_angle",
            self.minimum_vertical_angle,
            maximum=90.0,
        )
        if self.minimum_vertical_angle >= 90.0:
            raise ValueError("ball.minimum_vertical_angle must be < 90")


@dataclass(frozen=True)
class PlayerShieldSettings:
    width: int = 95
    height: int = 15

    speed: float = 850.0
    acceleration: float = 6000.0
    deceleration: float = 8000.0

    curved: bool = False

    friction_enabled: bool = True
    friction: float = 0.18

    def __post_init__(self) -> None:
        _require_integer("paddle.width", self.width)
        _require_integer("paddle.height", self.height)
        if self.curved and self.height > self.width / 2:
            raise ValueError("A curved paddle requires height <= width / 2")
        for name in ("speed", "acceleration", "deceleration", "friction"):
            _require_number(f"paddle.{name}", getattr(self, name))


@dataclass(frozen=True)
class PowerUpSettings:
    enabled: bool = True

    allowed: tuple[str, ...] = (
        "wide",
        "fast",
        "slow",
        "multiball",
        "extra_life",
        "sticky",
        "shield",
    )

    test_powerup: str | None = None

    drop_chance: float = 0.20
    fall_speed: float = 140.0
    pickup_lifetime: float = 12.0
    pickup_radius: float = 12.0

    wide_duration: float = 12.0
    fast_duration: float = 8.0
    slow_duration: float = 8.0
    sticky_duration: float = 10.0
    shield_duration: float = 10.0

    wide_factor: float = 1.5
    fast_speed_factor: float = 1.15
    slow_speed_factor: float = 0.75

    resize_ball: bool = True
    fast_size_factor: float = 0.8
    slow_size_factor: float = 1.5

    powered_damage: bool = True
    fast_power: int = 6
    slow_power: int = 4

    piercing: bool = True
    fast_hit_speed_retain: float = 0.90

    maximum_balls: int = 50
    split_angle_degrees: float = 15.0

    def __post_init__(self) -> None:
        known = {kind.name.lower() for kind in PowerUpKind}
        unknown = set(self.allowed) - known

        if unknown:
            raise ValueError(f"Unknown power-up names: {sorted(unknown)}")

        if len(set(self.allowed)) != len(self.allowed):
            raise ValueError("Duplicate power-up names")

        if not 0.0 <= self.drop_chance <= 1.0:
            raise ValueError("drop_chance must be in [0, 1]")

        _require_integer("powerups.maximum_balls", self.maximum_balls)
        for name in ("fast_power", "slow_power"):
            _require_integer(f"powerups.{name}", getattr(self, name))
        for name in (
            "pickup_lifetime",
            "pickup_radius",
            "wide_duration",
            "fast_duration",
            "slow_duration",
            "sticky_duration",
            "shield_duration",
            "wide_factor",
            "fast_speed_factor",
            "slow_speed_factor",
            "fast_size_factor",
            "slow_size_factor",
        ):
            _require_number(
                f"powerups.{name}", getattr(self, name), positive=True
            )
        _require_number("powerups.fall_speed", self.fall_speed)
        _require_number(
            "powerups.fast_hit_speed_retain",
            self.fast_hit_speed_retain,
            maximum=1.0,
        )
        _require_number(
            "powerups.split_angle_degrees",
            self.split_angle_degrees,
            maximum=90.0,
        )

    @property
    def kinds(self) -> tuple[PowerUpKind, ...]:
        if not self.enabled:
            return ()

        return tuple(PowerUpKind[name.upper()] for name in self.allowed)

    def duration(self, kind: PowerUpKind) -> float:
        return {
            PowerUpKind.WIDE: self.wide_duration,
            PowerUpKind.FAST: self.fast_duration,
            PowerUpKind.SLOW: self.slow_duration,
            PowerUpKind.STICKY: self.sticky_duration,
            PowerUpKind.SHIELD: self.shield_duration,
        }[kind]


@dataclass(frozen=True)
class EnemySettings:
    multi_hit_enabled: bool = True

    transformations_enabled: bool = True
    transform_chance: float = 0.15

    explosions_enabled: bool = True
    explosion_damage: int = 1

    ghosts_enabled: bool = True
    ghost_duration: float = 3.0

    def __post_init__(self) -> None:
        _require_number(
            "bricks.transform_chance", self.transform_chance, maximum=1.0
        )
        _require_integer("bricks.explosion_damage", self.explosion_damage)
        _require_number(
            "bricks.ghost_duration", self.ghost_duration, positive=True
        )


@dataclass(frozen=True)
class WrapSettings:
    enabled: bool = True

    chance: float = 0.04
    duration: float = 6.0
    cooldown: float = 20.0

    animated_border: bool = True
    dash_length: float = 12.0
    dash_gap: float = 8.0
    dash_speed: float = 45.0

    def __post_init__(self) -> None:
        _require_number("wrap.chance", self.chance, maximum=1.0)
        for name in ("duration", "dash_length"):
            _require_number(f"wrap.{name}", getattr(self, name), positive=True)
        for name in ("cooldown", "dash_gap", "dash_speed"):
            _require_number(f"wrap.{name}", getattr(self, name))


@dataclass(frozen=True)
class ParticleSettings:
    enabled: bool = True
    maximum: int = 500

    brick_burst: ParticleBurst = field(
        default_factory=ParticleBurst,
    )
    explosion_burst: ParticleBurst = field(
        default_factory=lambda: ParticleBurst(count=18),
    )
    pickup_burst: ParticleBurst = field(
        default_factory=ParticleBurst,
    )

    def __post_init__(self) -> None:
        _require_integer("fx.particles.maximum", self.maximum, minimum=0)
        for name in ("brick_burst", "explosion_burst", "pickup_burst"):
            burst = getattr(self, name)
            path = f"fx.particles.{name}"
            _require_integer(f"{path}.count", burst.count, minimum=0)
            for attribute in ("speed_min", "speed_max", "drag"):
                _require_number(
                    f"{path}.{attribute}", getattr(burst, attribute)
                )
            for attribute in (
                "lifetime_min",
                "lifetime_max",
                "radius_min",
                "radius_max",
            ):
                _require_number(
                    f"{path}.{attribute}",
                    getattr(burst, attribute),
                    positive=True,
                )
            if (
                burst.speed_min > burst.speed_max
                or burst.radius_min > burst.radius_max
            ):
                raise ValueError(f"{path}: minimum must not exceed maximum")


@dataclass(frozen=True)
class TrailSettings:
    enabled: bool = True
    duration: float = 0.45
    interval: float = 1 / 60
    maximum_points: int = 64
    powerup_colors: bool = True

    def __post_init__(self) -> None:
        _require_number("fx.trails.duration", self.duration, positive=True)
        _require_number("fx.trails.interval", self.interval, positive=True)
        _require_integer("fx.trails.maximum_points", self.maximum_points)


@dataclass(frozen=True)
class ShakeSettings:
    enabled: bool = True
    duration: float = 0.14
    hit_strength: float = 1.5
    explosion_strength: float = 4.0

    def __post_init__(self) -> None:
        _require_number("fx.shake.duration", self.duration, positive=True)
        _require_number("fx.shake.hit_strength", self.hit_strength)
        _require_number("fx.shake.explosion_strength", self.explosion_strength)


@dataclass(frozen=True)
class FlashSettings:
    enabled: bool = True
    duration: float = 0.10
    color: Color = (255, 255, 255)
    hit_alpha: int = 18
    explosion_alpha: int = 45

    def __post_init__(self) -> None:
        _require_number("fx.flash.duration", self.duration, positive=True)
        for name in ("hit_alpha", "explosion_alpha"):
            value = getattr(self, name)
            _require_integer(f"fx.flash.{name}", value, minimum=0)
            _require_number(f"fx.flash.{name}", value, maximum=255)
        if len(self.color) not in (3, 4) or any(
            type(channel) is not int or not 0 <= channel <= 255
            for channel in self.color
        ):
            raise ValueError("fx.flash.color must contain 3 or 4 bytes")


@dataclass(frozen=True)
class FXSettings:
    particles: ParticleSettings = field(
        default_factory=ParticleSettings,
    )
    trails: TrailSettings = field(
        default_factory=TrailSettings,
    )
    shake: ShakeSettings = field(
        default_factory=ShakeSettings,
    )
    flash: FlashSettings = field(
        default_factory=FlashSettings,
    )


@dataclass(frozen=True)
class ScoringSettings:
    combos_enabled: bool = True


@dataclass(frozen=True)
class HUDSettings:
    enabled: bool = True
    show_powerup_timers: bool = True


@dataclass(frozen=True)
class PlayerSettings:
    radius: float = 30.0
    speed: float = 300.0

    def __post_init__(self) -> None:
        _require_number("player.radius", self.radius, positive=True)
        _require_number("player.speed", self.speed, positive=True)


@dataclass(frozen=True)
class ShatterphaseSettings(DataclassSettings):

    color: ColorSettings = field(default_factory=ColorSettings)

    initial_lives: int = 5
    respawn_delay: float = 0.5

    ball: BallSettings = field(default_factory=BallSettings)
    player: PlayerSettings = field(default_factory=PlayerSettings)
    paddle: PlayerShieldSettings = field(default_factory=PlayerShieldSettings)
    powerups: PowerUpSettings = field(
        default_factory=PowerUpSettings,
    )
    bricks: EnemySettings = field(default_factory=EnemySettings)
    wrap: WrapSettings = field(default_factory=WrapSettings)
    fx: FXSettings = field(default_factory=FXSettings)
    scoring: ScoringSettings = field(
        default_factory=ScoringSettings,
    )
    hud: HUDSettings = field(default_factory=HUDSettings)

    persistent_balls: bool = True
    enable_aiming: bool = True
    profiling_max_enemies: bool = False

    def __post_init__(self) -> None:
        _require_integer("initial_lives", self.initial_lives)
        _require_number("respawn_delay", self.respawn_delay)
        if (
            self.paddle.curved
            and PowerUpKind.WIDE in self.powerups.kinds
            and int(self.paddle.width * self.powerups.wide_factor)
            < 2 * self.paddle.height
        ):
            raise ValueError(
                "The wide modifier would make the curved paddle too narrow"
            )


@SettingsRegistry.implementation("breakout")
class ShatterphaseSettingsBuilder(SettingsBuilder[ShatterphaseSettings]):
    def build(self, config: dict[str, Any]) -> ShatterphaseSettings:
        values = dict(config)

        return ShatterphaseSettings.from_dict(values)


# Components, intent and world resources


@dataclass
class TrailPoint:
    position: Vec2
    radius: float
    color: Color
    age: float = 0.0


@dataclass
class Player: ...


@dataclass
class PlayerShield:
    color: Color


@dataclass
class Ball:
    spin: float = 0.0
    speed_factor: float = 1.0
    combo: int = 1  # Multiplier for the next destroyed brick
    power: int = 1
    pierce_time: float = 0.0


@dataclass
class WaitingForLaunch: ...


@dataclass
class Enemy:
    row: int
    column: int
    kind: str
    hits_remaining: int
    max_hits: int
    points: int
    destructible: bool = True


@dataclass
class UIDisplay: ...


@dataclass
class ShieldPhysics:
    face: BoundsSide
    max_angle_degrees: float = 65.0
    motion_influence: float = 0.25


POWERUP_STYLE = {
    PowerUpKind.WIDE: ("W", (80, 220, 210)),
    PowerUpKind.FAST: ("F", (255, 100, 100)),
    PowerUpKind.SLOW: ("S", (100, 170, 255)),
    PowerUpKind.MULTIBALL: ("M", (195, 130, 255)),
    PowerUpKind.EXTRA_LIFE: ("+1", (120, 240, 130)),
    PowerUpKind.STICKY: ("ST", (255, 200, 100)),
    PowerUpKind.SHIELD: ("SH", (220, 230, 255)),
}


@dataclass
class PowerUp:
    kind: PowerUpKind


@dataclass
class ExplodingEnemy:
    pass


@dataclass
class GhostEnemy:
    remaining: float
    original_color: Color


class EWorld(World): ...


class EIntent(Intent):
    launch: bool = False
    aim: bool = False
    pointer_position: tuple[int, int] = (0, 0)
    pointer_inside: bool = False

    def update_from(self, input_frame):
        left = input_frame.buttons.get("mouse_1")
        right = input_frame.buttons.get("mouse_3")

        self.move_left = input_frame.is_down(Key.A)
        self.move_right = input_frame.is_down(Key.D)
        self.move_up = input_frame.is_down(Key.W)
        self.move_down = input_frame.is_down(Key.S)

        self.launch = input_frame.is_pressed(Key.SPACE) or bool(
            left and left.pressed
        )
        self.aim = bool(right and right.down)

        self.pointer_position = input_frame.mouse_pos
        self.pointer_inside = input_frame.mouse_inside


class ESceneTickContext(SceneTickContext[EWorld, EIntent]):
    @property
    def settings(self) -> ShatterphaseSettings:
        return self.world.get_resource(ShatterphaseSettings)


@dataclass
class WrapMode:
    rng: Random = field(default_factory=Random)
    remaining: float = 0.0
    cooldown: float = 0.0
    phase: float = 0.0


@dataclass
class Lives:
    count: int = 5


@dataclass
class Score:
    points: int = 0


@dataclass
class EnemyContactState:
    previous: set[tuple[EntityId, EntityId]] = field(default_factory=set)


@dataclass
class PowerUpState:
    base_paddle_size: Size
    base_ball_radius: float
    settings: PowerUpSettings
    remaining: dict[PowerUpKind, float] = field(default_factory=dict)

    def active(self, kind: PowerUpKind) -> bool:
        return (
            kind in self.settings.kinds and self.remaining.get(kind, 0.0) > 0
        )

    @property
    def speed_factor(self) -> float:
        if self.active(PowerUpKind.FAST):
            return self.settings.fast_speed_factor
        if self.active(PowerUpKind.SLOW):
            return self.settings.slow_speed_factor
        return 1.0


@dataclass
class WaveMotion:
    speed: float = 0.0

    # Preserve space between the lowest brick and the paddle.
    clearance: float = 96.0


# Aiming geometry and entity blueprints


@dataclass
class AimGuide:
    visible: bool = False

    # Reticle appearance, in world units.
    radius: float = 10.0
    thickness: int = 1
    rotation: float = 0.0  # radians(-5.0)

    # Trajectory appearance and maximum displayed distance.
    dot_spacing: float = 14.0
    dot_radius: float = 2.5
    max_distance: float = 900.0

    # One path per waiting ball.
    paths: list[list[Vec2]] = field(default_factory=list)

    # Reused by the launcher in the same simulation tick.
    launch_velocities: dict[EntityId, Vec2] = field(default_factory=dict)


def pointer_world_position(
    ctx: ESceneTickContext,
    camera_fx: CameraFX,
) -> Vec2 | None:
    if not ctx.intent.pointer_inside:
        return None

    viewport = ctx.scene_context.viewport

    if viewport.scale <= 0:
        return None

    mx, my = ctx.intent.pointer_position

    # Reject pointer positions in letterbox margins.
    vx = (mx - viewport.offset_x) / viewport.scale
    vy = (my - viewport.offset_y) / viewport.scale

    if not (0 <= vx < viewport.virtual_w and 0 <= vy < viewport.virtual_h):
        return None

    view = camera_fx.snapshot()

    # Match the translation applied by Tatuy's world renderer.
    origin_x = round(viewport.offset_x + viewport.scale * view.offset_x)
    origin_y = round(viewport.offset_y + viewport.scale * view.offset_y)

    return Vec2(
        (mx - origin_x) / viewport.scale,
        (my - origin_y) / viewport.scale,
    )


def calculate_launch_velocity(
    ctx: ESceneTickContext,
    entity: EntityId,
    index: int,
    count: int,
    target: Vec2 | None,
) -> Vec2:
    world = ctx.world
    cfg = ctx.settings.ball
    factor = world.get_resource(PowerUpState).speed_factor

    if target is not None:
        origin = world.get_component(entity, Transform).position
        offset = target - origin

        # Angle measured from straight upward.
        heading = (
            atan2(offset.x, -offset.y)
            if offset.length_squared() > 1e-9
            else 0.0
        )

        # Keep aimed launches within 65 degrees of upward.
        limit = radians(65.0)
        heading = max(-limit, min(limit, heading))

        direction = Vec2(sin(heading), -cos(heading))
        velocity = direction * (cfg.launch_speed * factor)

    else:
        attachment = world.get_component(entity, AttachedTo)
        paddle_velocity = world.get_component(
            attachment.entity,
            Velocity,
        ).value

        inheritance = (
            cfg.launch_inheritance if cfg.inherit_paddle_velocity else 0.0
        )

        velocity = (
            Vec2(
                paddle_velocity.x * inheritance,
                -cfg.launch_speed,
            )
            * factor
        )

    speed_limit = cfg.maximum_speed * factor

    if velocity.length() > speed_limit:
        velocity = velocity.normalized() * speed_limit

    # Preserve the existing spread between multiple waiting balls.
    if count > 1:
        spread = cfg.launch_spread_degrees
        angle = radians(-spread + 2 * spread * index / (count - 1))
        velocity = velocity.rotated(angle)

    return velocity


def ray_polygon_distance(
    origin: Vec2,
    direction: Vec2,
    vertices: tuple[Vec2, ...],
    radius: float,
    max_distance: float,
) -> float | None:
    """Sweep a circle along a unit ray against convex polygon edges/corners."""
    candidates = []
    inside = True
    area = sum(
        a.x * b.y - b.x * a.y
        for a, b in zip(vertices, vertices[1:] + vertices[:1])
    )
    winding = 1 if area >= 0 else -1
    for start, end in zip(vertices, vertices[1:] + vertices[:1]):
        edge = end - start
        length_squared = edge.length_squared()
        if length_squared <= 1e-9:
            continue
        normal = Vec2(edge.y, -edge.x).normalized() * winding
        relative = origin - start
        distance = relative.dot(normal)
        inside = inside and distance <= 0
        fraction = max(0.0, min(1.0, relative.dot(edge) / length_squared))
        if (origin - (start + edge * fraction)).length_squared() <= radius**2:
            return 0.0
        approach = direction.dot(normal)
        if approach < -1e-9:
            travel = (radius - distance) / approach
            along = (origin + direction * travel - start).dot(edge)
            if 0 <= travel <= max_distance and 0 <= along <= length_squared:
                candidates.append(travel)

        # The radius around each vertex gives a rounded corner.
        b = relative.dot(direction)
        c = relative.length_squared() - radius**2
        discriminant = b * b - c
        if discriminant >= 0:
            travel = -b - sqrt(discriminant)
            if 0 <= travel <= max_distance:
                candidates.append(travel)

    if inside:
        return 0.0
    return min(candidates) if candidates else None


def predict_path(
    ctx: ESceneTickContext,
    entity: EntityId,
    velocity: Vec2,
    guide: AimGuide,
) -> list[Vec2]:
    world = ctx.world
    origin = world.get_component(entity, Transform).position
    radius = world.get_component(entity, CircleCollider).radius

    if velocity.length_squared() <= 1e-9:
        return []

    direction = velocity.normalized()
    distance = guide.max_distance
    bounds = world.get_resource(WorldBounds).bounds

    # Stop at the first playfield edge.
    # The ball's center remains one radius inside the boundary.
    for position, delta, lower, upper in (
        (
            origin.x,
            direction.x,
            bounds.left + radius,
            bounds.right - radius,
        ),
        (
            origin.y,
            direction.y,
            bounds.top + radius,
            bounds.bottom - radius,
        ),
    ):
        if delta > 1e-9:
            hit = (upper - position) / delta
        elif delta < -1e-9:
            hit = (lower - position) / delta
        else:
            continue

        if hit >= 0:
            distance = min(distance, hit)

    # Stop at the first solid brick.
    for brick_entity, _, transform, collider in world.query(
        Enemy,
        Transform,
        PolygonCollider,
    ):
        if collider.is_sensor:
            continue

        if world.has_component(brick_entity, GhostEnemy):
            continue

        center = transform.position

        hit = ray_polygon_distance(
            origin,
            direction,
            tuple(center + vertex for vertex in collider.vertices),
            radius,
            distance,
        )

        if hit is not None:
            distance = min(distance, hit)

    # Leave a gap around the real ball.
    points: list[Vec2] = []
    spacing = max(1.0, guide.dot_spacing)
    travel = radius + spacing

    while travel < distance:
        points.append(origin + direction * travel)
        travel += spacing

    return points


class EEntityFactory(EntityFactory):
    def create(self, name: str, **kwargs):
        if name in {"player", "player_shield", "e_ball", "e_hex", "power_up"}:
            kwargs["settings"] = self._world.get_resource(ShatterphaseSettings)

        return super().create(name, **kwargs)


@dataclass(frozen=True, kw_only=True)
class PlayerShieldBlueprintAttrs(RectBlueprintAttrs):
    settings: ShatterphaseSettings


@dataclass(frozen=True, kw_only=True)
class PlayerBlueprintAttrs(CircleBlueprintAttrs):
    settings: ShatterphaseSettings


@EEntityFactory.blueprint("player")
class PlayerBlueprint(CircleBlueprint[EWorld]):
    identity = Player
    attrs_type = PlayerBlueprintAttrs

    def compose(self, attrs: PlayerBlueprintAttrs):
        return (
            MovementControls(),
            Movement(speed=attrs.settings.player.speed, acceleration=None),
            DesiredMovement(),
            Velocity(),
            MotionSample(),
            CircleCollider(attrs.radius),
            CollisionBody(inverse_mass=0),
            BoundsConstraint(
                behavior=BoundsBehavior.CLAMP, sides=BoundsSide.ALL
            ),
        )


@dataclass(frozen=True, kw_only=True)
class BallBlueprintAttrs(CircleBlueprintAttrs):
    settings: ShatterphaseSettings


@dataclass(frozen=True, kw_only=True)
class PowerUpBlueprintAttrs(CircleBlueprintAttrs):
    kind: PowerUpKind
    settings: ShatterphaseSettings


@EEntityFactory.blueprint("player_shield")
class PlayerShieldBlueprint(RectBlueprint[EWorld]):
    attrs_type = PlayerShieldBlueprintAttrs

    def build_attrs(self, world, entity, attrs: PlayerShieldBlueprintAttrs):
        super().build_attrs(world, entity, attrs)
        world.add_component(entity, PlayerShield(color=attrs.color))
        world.get_component(entity, Rect).visible = (
            not attrs.settings.paddle.curved
        )

    def compose(self, attrs: PlayerShieldBlueprintAttrs):
        return (
            Velocity(),
            BoxCollider(attrs.size),
            CollisionBody(inverse_mass=0),
            ShieldPhysics(face=BoundsSide.TOP),
            MotionSample(),
        )


@EEntityFactory.blueprint("e_ball")
class BallBlueprint(CircleBlueprint[EWorld]):

    identity = Ball
    attrs_type = BallBlueprintAttrs

    def compose(self, attrs: BallBlueprintAttrs):
        cfg = attrs.settings.fx.trails
        return (
            WaitingForLaunch(),
            Velocity(),
            CircleCollider(attrs.radius),
            CollisionBody(),
            BoundsConstraint(
                behavior=BoundsBehavior.BOUNCE,
                sides=BoundsSide.HORIZONTAL | BoundsSide.TOP,
            ),
            Trail(
                duration=cfg.duration,
                interval=cfg.interval,
                max_points=cfg.maximum_points,
                radius=attrs.radius,
                color=attrs.color,
                enabled=cfg.enabled,
            ),
        )


@dataclass(frozen=True, kw_only=True)
class EnemyBlueprintAttrs(PolygonBlueprintAttrs):
    settings: ShatterphaseSettings
    definition: EnemyDefinition
    row: int
    column: int


@EEntityFactory.blueprint("e_hex")
class EnemyBlueprint(PolygonBlueprint[EWorld]):
    attrs_type = EnemyBlueprintAttrs

    def get_collider(self, attrs):
        # The engine supplies polygon collision detection and response.
        return PolygonCollider(attrs.vertices)

    def compose(self, attrs: EnemyBlueprintAttrs):
        definition = attrs.definition
        hits = (
            definition.hits if attrs.settings.bricks.multi_hit_enabled else 1
        )
        return (
            Enemy(
                row=attrs.row,
                column=attrs.column,
                kind=definition.kind,
                hits_remaining=hits,
                max_hits=hits,
                points=definition.points,
                destructible=definition.destructible,
            ),
            Velocity(),
            CollisionBody(inverse_mass=0),
        )


@EEntityFactory.blueprint("ui")
class UIBlueprint(TextBlueprint[EWorld]):
    identity = UIDisplay


@EEntityFactory.blueprint("aim")
class AimBlueprint(EntityBlueprint[EWorld]):
    def build(self, world, entity, **kwargs):
        world.add_component(entity, Transform(Vec2.zero()))
        world.add_component(entity, AimGuide())


def hex_vertices(radius: float) -> tuple[Vec2, ...]:
    return tuple(
        Vec2(cos(index * tau / 6), sin(index * tau / 6)) * radius
        for index in range(6)
    )


@EEntityFactory.blueprint("power_up")
class PowerUpBlueprint(CircleBlueprint[EWorld]):
    attrs_type = PowerUpBlueprintAttrs

    def compose(self, attrs: PowerUpBlueprintAttrs):
        label, _ = POWERUP_STYLE[attrs.kind]
        cfg = attrs.settings.powerups

        return (
            PowerUp(attrs.kind),
            Velocity(Vec2(0, cfg.fall_speed)),
            CircleCollider(attrs.radius, is_sensor=True),
            Lifetime(cfg.pickup_lifetime),
            BoundsConstraint(
                behavior=BoundsBehavior.DESPAWN,
                sides=BoundsSide.BOTTOM,
            ),
            Text(
                color=(15, 18, 32),
                content=label,
                font_size=11,
                align="center",
                valign="middle",
                layer="world",
                z=1,
            ),
        )


# Shared gameplay helpers and wave data


def ball_below_floor(world: EWorld, entity: EntityId):
    position = world.get_component(entity, Transform).position
    radius = world.get_component(entity, CircleCollider).radius
    bottom = world.get_resource(WorldBounds).bounds.bottom

    # The whole ball has crossed the bottom.
    return position.y - radius > bottom


def attach_ball(world: EWorld, ball: EntityId, paddle: EntityId):
    size = world.get_component(paddle, BoxCollider).size
    radius = world.get_component(ball, CircleCollider).radius
    offset = Vec2(0, -(size.height / 2 + radius))

    world.add_component(ball, WaitingForLaunch())
    world.add_component(ball, AttachedTo(paddle, offset))

    world.get_component(ball, Velocity).value = Vec2.zero()
    world.get_component(ball, Ball).spin = 0.0
    world.get_component(ball, Transform).position = (
        world.get_component(paddle, Transform).position + offset
    )


def cap_circle(size: Size) -> tuple[Vec2, float]:
    half_width = size.width / 2
    height = size.height

    if not 0 < height <= half_width:
        raise ValueError("Use 0 < paddle height <= paddle width / 2")

    radius = (half_width * half_width + height * height) / (2 * height)

    # Coordinates relative to the paddle's Transform.position.
    return Vec2(0, radius - height / 2), radius


def cap_contact(
    ball: Vec2,
    ball_radius: float,
    size: Size,
) -> tuple[Vec2, float] | None:
    """Return a paddle-to-ball normal and penetration, in local space."""
    center, radius = cap_circle(size)
    half_width = size.width / 2
    bottom = size.height / 2
    delta = ball - center

    # Closest point on the circular arc, restricted to the cap.
    arc = center + delta.normalized() * radius

    if delta.length_squared() == 0:
        arc = Vec2(0, -bottom)

    if arc.y > bottom:
        arc = Vec2(
            half_width if ball.x >= 0 else -half_width,
            bottom,
        )

    # Closest point on the flat bottom.
    base = Vec2(clamp(ball.x, -half_width, half_width), bottom)

    closest = min(
        (arc, base),
        key=lambda point: (ball - point).length_squared(),
    )

    offset = ball - closest
    distance = offset.length()
    inside = ball.y <= bottom and delta.length_squared() <= radius * radius

    if not inside and distance >= ball_radius:
        return None

    if distance > 1e-9:
        normal = offset / distance
        if inside:
            normal = normal * -1
    else:
        # The ball's center lies directly on the boundary.
        normal = (
            Vec2(0, 1) if closest == base else (closest - center).normalized()
        )

    penetration = ball_radius + distance if inside else ball_radius - distance
    return normal, penetration


def brick_burst(world: EWorld, entity, particles: ParticleEmitter):
    settings = world.get_resource(ShatterphaseSettings)
    cfg = settings.fx.particles
    if not cfg.enabled:
        return

    position = world.get_component(entity, Transform).position
    color = world.get_component(entity, Polygon).color
    explosive = settings.bricks.explosions_enabled and world.has_component(
        entity, ExplodingEnemy
    )
    burst = cfg.explosion_burst if explosive else cfg.brick_burst
    particles.emit(position, color, burst=burst)


def maybe_start_wrap(world: EWorld):
    cfg = world.get_resource(ShatterphaseSettings).wrap
    if not cfg.enabled:
        return

    mode = world.get_resource(WrapMode)
    if mode.remaining > 0 or mode.cooldown > 0:
        return
    if mode.rng.random() >= cfg.chance:
        return

    mode.remaining = cfg.duration
    mode.cooldown = cfg.duration + cfg.cooldown
    world.get_resource(WorldBoundsBorder).sides &= ~BoundsSide.HORIZONTAL


class EnemyFieldBuilder:
    def __init__(
        self,
        queue: LifecycleQueue,
        layout: GridLayout | None = None,
    ) -> None:
        self._queue = queue
        self._layout = layout if layout is not None else GridLayout()

    def build(
        self,
        area: Bounds,
        definition: EnemyFieldDefinition,
    ) -> None:
        for row in definition.rows:
            if row.hits <= 0:
                raise ValueError("Initial brick hits must be positive")

        with profiler.span("field.resolve_layout", "wave"):
            placements = self._layout.resolve(
                area,
                GridSpec(
                    rows=len(definition.rows),
                    columns=definition.columns,
                    cell_height=ceil(sqrt(3) * definition.enemy_radius),
                    cell_width=definition.enemy_radius * 2,
                    gap_x=definition.gap_x,
                    gap_y=definition.gap_y,
                ),
            )

        profiler.metric("placements", len(placements))

        vertices = hex_vertices(definition.enemy_radius)

        with profiler.span("field.queue_spawns", "wave"):
            for placement in placements:
                self._queue.request_spawn(
                    "e_hex",
                    kwargs={
                        "position": placement.center,
                        "vertices": vertices,
                        "color": definition.rows[placement.row].color,
                        "row": placement.row,
                        "column": placement.column,
                        "definition": definition.rows[placement.row],
                    },
                )


@dataclass
class WaveDefinition:
    rows: tuple[EnemyDefinition, ...]
    columns: int
    enemy_radius: int = 20
    gap_x: int = 6
    gap_y: int = 8

    # World units per second. Zero disables descent.
    descent_speed: float = 0.0


@dataclass
class Waves:
    definitions: Iterator[WaveDefinition]
    max: int = 10
    completed: bool = False
    current: int = 0

    # The definition waiting for cleanup and ball attachment.
    pending: WaveDefinition | None = None

    # Prevent launching the replacement ball on its creation tick.
    started_this_tick: bool = False


def wave_definitions(settings: ShatterphaseSettings, brick_area: Bounds):
    colors = settings.color.bricks

    fragile_colors = (
        colors.green,
        colors.blue,
        colors.purple,
    )

    def make_wave(
        *,
        columns,
        hits,
        height,
        gap,
        descent=0.0,
    ):
        rows = []

        for index, durability in enumerate(hits):
            if durability == 1:
                kind = "fragile"
                color = fragile_colors[index % len(fragile_colors)]
            elif durability == 2:
                kind = "standard"
                color = colors.yellow
            else:
                kind = "armored"
                color = colors.coral

            rows.append(
                EnemyDefinition(
                    kind,
                    color,
                    hits=durability,
                    points=50 * durability,
                )
            )

        # Keep all rows inside the existing brick area.
        available_height = brick_area.height - (len(rows) - 1) * gap
        fitted_height = min(
            height,
            int(available_height // len(rows)),
        )

        available_width = brick_area.width - (columns - 1) * gap
        fitted_width = int(available_width // columns)

        if fitted_height < 2 or fitted_width < 2:
            raise ValueError(
                f"Wave with {len(rows)} rows and {columns} columns "
                "does not fit the brick area"
            )

        return {
            "rows": tuple(rows),
            "columns": columns,
            "enemy_radius": min(
                fitted_width // 2, int(fitted_height / sqrt(3))
            ),
            "gap_x": gap,
            "gap_y": gap,
            "descent_speed": descent,
        }

    wave_definitions = (
        # 1: 3 × 3 = 9 bricks.
        make_wave(
            columns=3,
            hits=(1, 1, 1),
            height=28,
            gap=8,
        ),
        # 2: 4 × 4 = 16 bricks.
        make_wave(
            columns=4,
            hits=(1, 1, 1, 1),
            height=27,
            gap=7,
        ),
        # 3: 5 × 5 = 25 bricks.
        make_wave(
            columns=5,
            hits=(1, 1, 1, 1, 1),
            height=26,
            gap=6,
        ),
        # 4: 6 × 6 = 36 bricks.
        make_wave(
            columns=6,
            hits=(2, 1, 1, 1, 1, 1),
            height=25,
            gap=6,
        ),
        # 5: 7 × 7 = 49 bricks.
        make_wave(
            columns=7,
            hits=(2, 2, 1, 1, 1, 1, 1),
            height=24,
            gap=5,
        ),
        # 6: 8 × 8 = 64 bricks.
        make_wave(
            columns=8,
            hits=(2, 2, 1, 1, 1, 1, 1, 1),
            height=23,
            gap=5,
        ),
        # 7: 9 × 9 = 81 bricks.
        make_wave(
            columns=9,
            hits=(2, 2, 2, 1, 1, 1, 1, 1, 1),
            height=22,
            gap=4,
        ),
        # 8: 10 × 10 = 100 bricks.
        make_wave(
            columns=10,
            hits=(2, 2, 2, 1, 1, 1, 1, 1, 1, 1),
            height=21,
            gap=4,
        ),
        # 9: 11 × 10 = 110 bricks.
        # Very slow descent begins.
        make_wave(
            columns=11,
            hits=(2, 2, 2, 2, 1, 1, 1, 1, 1, 1),
            height=20,
            gap=4,
            descent=0.5,
        ),
        # 10: 12 × 10 = 120 bricks.
        make_wave(
            columns=12,
            hits=(2, 2, 2, 2, 2, 1, 1, 1, 1, 1),
            height=19,
            gap=3,
            descent=1.0,
        ),
        # 11: 13 × 10 = 130 bricks.
        make_wave(
            columns=13,
            hits=(3, 2, 2, 2, 2, 1, 1, 1, 1, 1),
            height=18,
            gap=3,
            descent=1.5,
        ),
        # 12: 14 × 10 = 140 bricks.
        make_wave(
            columns=14,
            hits=(3, 3, 2, 2, 2, 1, 1, 1, 1, 1),
            height=17,
            gap=3,
            descent=2.0,
        ),
        # 13: 15 × 10 = 150 bricks.
        make_wave(
            columns=15,
            hits=(3, 3, 2, 2, 2, 2, 1, 1, 1, 1),
            height=16,
            gap=3,
            descent=2.5,
        ),
        # 14: 16 × 10 = 160 bricks.
        make_wave(
            columns=16,
            hits=(3, 3, 3, 2, 2, 2, 1, 1, 1, 1),
            height=16,
            gap=2,
            descent=3.0,
        ),
        # 15: 17 × 10 = 170 bricks.
        make_wave(
            columns=17,
            hits=(3, 3, 3, 2, 2, 2, 2, 1, 1, 1),
            height=15,
            gap=2,
            descent=3.5,
        ),
        # 16: 18 × 10 = 180 bricks.
        make_wave(
            columns=18,
            hits=(3, 3, 3, 3, 2, 2, 2, 1, 1, 1),
            height=15,
            gap=2,
            descent=4.0,
        ),
        # 17: 19 × 10 = 190 bricks.
        make_wave(
            columns=19,
            hits=(3, 3, 3, 3, 2, 2, 2, 2, 1, 1),
            height=14,
            gap=2,
            descent=4.5,
        ),
        # 18: 20 × 10 = 200 bricks.
        make_wave(
            columns=20,
            hits=(3, 3, 3, 3, 3, 2, 2, 2, 1, 1),
            height=14,
            gap=2,
            descent=5.0,
        ),
        # 19: 22 × 10 = 220 bricks.
        make_wave(
            columns=22,
            hits=(3, 3, 3, 3, 3, 2, 2, 2, 2, 1),
            height=13,
            gap=2,
            descent=5.5,
        ),
        # 20: 24 × 10 = 240 bricks.
        make_wave(
            columns=24,
            hits=(3, 3, 3, 3, 3, 3, 2, 2, 2, 1),
            height=12,
            gap=2,
            descent=6.0,
        ),
    )

    definitions = tuple(WaveDefinition(**item) for item in wave_definitions)
    if not settings.profiling_max_enemies:
        return definitions

    # Fill the existing grid with the smallest hexes used by normal waves.
    # Removing gaps maximizes the population without changing enemy scale.
    radius = min(definition.enemy_radius for definition in definitions)
    columns = int(brick_area.width // (2 * radius))
    rows = int(brick_area.height // ceil(sqrt(3) * radius))
    hits = max(
        row.hits for definition in definitions for row in definition.rows
    )
    enemy = EnemyDefinition(
        "armored", colors.coral, hits=hits, points=50 * hits
    )
    return (
        WaveDefinition(
            rows=(enemy,) * rows,
            columns=columns,
            enemy_radius=radius,
            gap_x=0,
            gap_y=0,
        ),
    )


# Domain game systems


class WaveSystem(GameSystem[ESceneTickContext]):
    """Advance waves and populate them after the spawn commit."""

    phase_orders = {
        SystemPhase.PRE_SIMULATION: 10,
        SystemPhase.SIMULATION: 30,
    }

    def on_pre_simulation(self, ctx):
        self._begin(ctx)

    def on_simulation(self, ctx):
        self._finish(ctx)

    def _begin(self, ctx):
        world = ctx.world
        waves = world.get_resource(Waves)
        queue = world.get_resource(LifecycleQueue)

        waves.started_this_tick = False

        if waves.completed or waves.pending is not None:
            return

        # Do not restart gameplay after the last life is lost.
        if world.get_resource(Lives).count <= 0:
            return

        # Enemies queued for destruction no longer block advancement.
        # The next structural commit removes them.
        has_bricks = any(
            entity not in queue.despawns for entity, _ in world.query(Enemy)
        )

        if has_bricks:
            return

        definition = next(waves.definitions, None)

        if definition is None:
            waves.completed = True

        waves.pending = definition

        # Remove every old ball and falling power-up.
        for component_type in (Ball, PowerUp):
            for entity, _ in world.query(component_type):
                queue.request_despawn(
                    entity,
                    DespawnReason.SCRIPTED,
                    allow_respawn=False,
                )

        # Cancel delayed ball respawns, otherwise an extra ball
        # could appear after the replacement has been created.
        registry = world.get_resource(SpawnRegistry)
        reset_definitions = {
            name
            for name, spawn in registry.definitions.items()
            if spawn.blueprint in {"e_ball", "power_up"}
        }

        if waves.current > 0:
            queue.spawns[:] = [
                request
                for request in queue.spawns
                if request.definition not in reset_definitions
            ]

        # This version starts each wave without active buffs.
        world.get_resource(PowerUpState).remaining.clear()

        wrap = world.get_resource(WrapMode)
        wrap.remaining = 0.0
        wrap.cooldown = 0.0
        wrap.phase = 0.0

        # Discard contacts belonging to the previous wave.
        world.get_resource(EnemyContactState).previous.clear()
        world.get_resource(CollisionFrame).contacts.clear()

        # Spawn exactly one replacement through the existing
        # registered "e_ball" definition.
        if not waves.completed:
            queue.request_spawn("e_ball")

    def _finish(self, ctx):
        world = ctx.world
        waves = world.get_resource(Waves)

        if waves.pending is None:
            return

        with profiler.span("wave.resolve_entities", "wave"):
            paddle = next(
                world.query(PlayerShield, Transform, BoxCollider),
                None,
            )

            balls = list(world.query(Ball, WaitingForLaunch))

        # Wait until the required entities exist.
        if paddle is None or len(balls) != 1:
            return

        paddle_entity = paddle[0]
        ball_entity = balls[0][0]

        with profiler.span("wave.attach_ball", "wave"):
            # The new ball is attached before any new bricks exist.
            attach_ball(world, ball_entity, paddle_entity)

        definition = waves.pending

        world.get_resource(WaveMotion).speed = definition.descent_speed

        brick_area = world.get_resource(Bounds)

        with profiler.span("wave.build_field", "wave"):
            EnemyFieldBuilder(world.get_resource(LifecycleQueue)).build(
                brick_area, definition
            )

        waves.pending = None
        waves.current += 1
        waves.started_this_tick = True


class PlayerSystem(GameSystem[ESceneTickContext]):
    """Move the circle and shield, then handle player contacts."""

    phase_orders = {
        SystemPhase.SIMULATION: 250,
        SystemPhase.POST_SIMULATION: 450,
        SystemPhase.PRESENTATION: 20,
    }

    def on_simulation(self, ctx):
        self._attach_shield(ctx)
        self._measure_shield_motion(ctx)

    def on_post_simulation(self, ctx):
        self._refine_contacts(ctx)
        self._reset_combos(ctx)
        self._catch_sticky_balls(ctx)
        self._apply_friction(ctx)

    def on_presentation(self, ctx):
        with profiler.span("palyer.presentation", "player_system"):
            self._render_shield(ctx)

    def _attach_shield(self, ctx):
        world = ctx.world
        player_row = next(world.query(Player, Transform, CircleCollider), None)
        shield_row = next(
            world.query(PlayerShield, Transform, BoxCollider), None
        )
        if player_row is None or shield_row is None:
            return

        player, _, transform, circle = player_row
        shield, _, shield_transform, box = shield_row
        offset = Vec2(0, -(circle.radius + box.size.height / 2))
        world.add_component(shield, AttachedTo(player, offset))

        bounds = world.get_resource(WorldBounds).bounds
        half_width = max(circle.radius, box.size.width / 2)
        transform.position.x = clamp(
            transform.position.x,
            bounds.left + half_width,
            bounds.right - half_width,
        )
        transform.position.y = clamp(
            transform.position.y,
            bounds.top + circle.radius + box.size.height,
            bounds.bottom - circle.radius,
        )
        shield_transform.position = transform.position + offset
        sample = world.get_component(player, MotionSample)
        if sample.start_position is not None and ctx.dt > 0:
            world.get_component(player, Velocity).value = (
                transform.position - sample.start_position
            ) / ctx.dt

    def _measure_shield_motion(self, ctx):
        for _, _, transform, velocity, sample in ctx.world.query(
            ShieldPhysics,
            Transform,
            Velocity,
            MotionSample,
        ):
            if sample.start_position is None or ctx.dt <= 0:
                velocity.value = Vec2.zero()
                continue

            velocity.value = (
                transform.position - sample.start_position
            ) / ctx.dt

    def _refine_contacts(self, ctx):
        if not ctx.settings.paddle.curved:
            return

        world = ctx.world
        frame = world.get_resource(CollisionFrame)
        refined = []

        for contact in frame.contacts:
            a, b = contact.entity_a, contact.entity_b

            if world.has_component(a, PlayerShield) and world.has_component(
                b, Ball
            ):
                paddle, ball = a, b
            elif world.has_component(b, PlayerShield) and world.has_component(
                a, Ball
            ):
                paddle, ball = b, a
            else:
                refined.append(contact)
                continue

            if world.has_component(ball, WaitingForLaunch):
                continue

            paddle_position = world.get_component(paddle, Transform).position
            ball_position = world.get_component(ball, Transform).position
            size = world.get_component(paddle, BoxCollider).size
            ball_radius = world.get_component(ball, CircleCollider).radius

            result = cap_contact(
                ball_position - paddle_position,
                ball_radius,
                size,
            )

            if result is None:
                continue

            normal, penetration = result

            # Tatuy requires the normal to point from entity A to B.
            if paddle != a:
                normal = normal * -1

            refined.append(
                CollisionContact(
                    entity_a=a,
                    entity_b=b,
                    normal=normal,
                    penetration=penetration,
                )
            )

        frame.contacts[:] = refined

    def _reset_combos(self, ctx):
        world = ctx.world

        for contact in world.get_resource(CollisionFrame).contacts:
            pair = match_contact(
                world, contact, Ball, PlayerShield
            ) or match_contact(world, contact, Ball, Player)

            if pair:
                world.get_component(pair[0], Ball).combo = 1

    def _catch_sticky_balls(self, ctx):
        world = ctx.world

        if not world.get_resource(PowerUpState).active(PowerUpKind.STICKY):
            return

        frame = world.get_resource(CollisionFrame)
        caught = set()

        for contact in frame.contacts:
            pair = match_contact(world, contact, Ball, PlayerShield)

            if pair is None:
                continue

            ball, paddle = pair

            if ball in caught or world.has_component(ball, WaitingForLaunch):
                continue

            # Orient the normal from paddle toward ball.
            normal = contact.normal

            if contact.entity_a == ball:
                normal = normal * -1

            relative = (
                world.get_component(ball, Velocity).value
                - world.get_component(paddle, Velocity).value
            )

            if relative.dot(normal) >= 0:
                # if dot(relative, normal) >= 0:
                continue

            attach_ball(world, ball, paddle)
            caught.add(ball)

            # Consume the pickup after one successful catch.
            world.get_resource(PowerUpState).remaining.pop(
                PowerUpKind.STICKY, None
            )

            # Prevent catching another ball during this same frame.
            break

        # A caught ball must not bounce or damage another entity.
        frame.contacts[:] = [
            contact
            for contact in frame.contacts
            if (
                contact.entity_a not in caught
                and contact.entity_b not in caught
            )
        ]

    def _apply_friction(self, ctx):
        world = ctx.world
        paddle_cfg = ctx.settings.paddle
        spin_cfg = ctx.settings.ball.spin

        for contact in world.get_resource(CollisionFrame).contacts:
            pair = match_contact(world, contact, Ball, PlayerShield)
            if pair is None:
                continue
            ball, paddle = pair
            if world.has_component(ball, WaitingForLaunch):
                continue

            normal = contact.normal
            if contact.entity_a != paddle:
                normal = normal * -1

            velocity = world.get_component(ball, Velocity)
            paddle_velocity = world.get_component(paddle, Velocity).value
            state = world.get_component(ball, Ball)
            radius = world.get_component(ball, CircleCollider).radius
            if not spin_cfg.enabled:
                state.spin = 0.0

            relative = velocity.value - paddle_velocity
            normal_speed = relative.dot(normal)
            if normal_speed >= 0:
                continue

            tangent = Vec2(-normal.y, normal.x)
            if paddle_cfg.friction_enabled:
                restitution = min(
                    world.get_component(ball, CollisionBody).restitution,
                    world.get_component(paddle, CollisionBody).restitution,
                )
                normal_change = -(1 + restitution) * normal_speed
                slip = relative.dot(tangent) - state.spin * radius
                limit = paddle_cfg.friction * normal_change
                tangent_change = clamp(-slip / 3, -limit, limit)
                velocity.value += tangent * tangent_change

            if (
                spin_cfg.enabled
                and paddle_velocity.length() > spin_cfg.minimum_paddle_speed
            ):
                impact_angle = atan2(relative.dot(tangent), -normal_speed)
                state.spin = clamp(
                    impact_angle * spin_cfg.impact_strength,
                    -spin_cfg.maximum,
                    spin_cfg.maximum,
                )
            else:
                state.spin = 0.0

    def _render_shield(self, ctx):
        for _, paddle, transform, box in ctx.world.query(
            PlayerShield, Transform, BoxCollider
        ):
            if not ctx.settings.paddle.curved:
                continue

            center, radius = cap_circle(box.size)
            half_width = box.size.width / 2
            points = []

            for i in range(25):
                x = -half_width + box.size.width * i / 24
                y = center.y - sqrt(max(0.0, radius * radius - x * x))
                points.append(transform.position + Vec2(x, y))

            ctx.render_queue.poly(
                points=points,
                fill=paddle.color,
                stroke=None,
                closed=True,
            )


class BallSystem(GameSystem[ESceneTickContext]):
    """Maintain flight, held balls, bounce angles, lives and trail style."""

    phase_orders = {
        SystemPhase.PRE_SIMULATION: 250,
        SystemPhase.SIMULATION: 280,
        SystemPhase.POST_SIMULATION: 540,
    }

    def on_pre_simulation(self, ctx):
        self._update_flight(ctx)

    def on_simulation(self, ctx):
        self._reset_bounds_spin(ctx)
        self._attach_waiting_balls(ctx)

    def on_post_simulation(self, ctx):
        self._enforce_bounce_angles(ctx)
        self._handle_lost_balls(ctx)
        self._style_trails(ctx)

    def _update_flight(self, ctx):
        cfg = ctx.settings.ball
        spin = cfg.spin
        maximum_heading = radians(90.0 - cfg.minimum_vertical_angle)

        for entity, ball, velocity in ctx.world.query(Ball, Velocity):
            if not spin.enabled:
                ball.spin = 0.0
            if ctx.world.has_component(entity, WaitingForLaunch):
                continue

            v = velocity.value
            speed = v.length()
            minimum = cfg.minimum_speed * ball.speed_factor
            maximum = cfg.maximum_speed * ball.speed_factor
            if speed <= 1e-9:
                v = Vec2(0.0, -minimum)
                speed = minimum
            speed = clamp(speed, minimum, maximum)

            # Speed maintenance remains active without spin or curve.
            if not spin.enabled:
                velocity.value = v.normalized() * speed
                continue

            decay = exp(-spin.decay * ctx.dt)
            if not spin.curve_active:
                velocity.value = v.normalized() * speed
                ball.spin *= decay
                continue

            if spin.decay > 0:
                angle = (
                    spin.curve_strength
                    * ball.spin
                    * (1.0 - decay)
                    / spin.decay
                )
            else:
                angle = spin.curve_strength * ball.spin * ctx.dt

            if spin.prevent_vertical_reversal:
                direction_y = 1.0 if v.y > 0 else -1.0
                heading = atan2(v.x, abs(v.y)) - direction_y * angle
                heading = clamp(heading, -maximum_heading, maximum_heading)
                velocity.value = Vec2(
                    speed * sin(heading),
                    direction_y * speed * cos(heading),
                )
            else:
                velocity.value = v.rotated(angle).normalized() * speed
            ball.spin *= decay

    def _reset_bounds_spin(self, ctx):
        cfg = ctx.settings.ball.spin
        if not cfg.enabled or not cfg.clear_on_bounds_bounce:
            return

        world = ctx.world
        frame = world.get_resource(BoundsFrame)

        for event in frame.bounces:
            if not world.has_component(event.entity, Ball):
                continue

            if world.has_component(event.entity, WaitingForLaunch):
                continue

            world.get_component(event.entity, Ball).spin = 0.0

    def _attach_waiting_balls(self, ctx):
        paddle = next(
            ctx.world.query(PlayerShield, Transform, BoxCollider),
            None,
        )

        if paddle is None:
            return

        paddle_entity, _, paddle_transform, paddle_collider = paddle

        for (
            ball_entity,
            _,
            _,
            ball_transform,
            ball_collider,
        ) in ctx.world.query(
            Ball, WaitingForLaunch, Transform, CircleCollider
        ):
            if ctx.world.has_component(ball_entity, AttachedTo):
                continue

            offset = Vec2(
                0,
                -(paddle_collider.size.height / 2 + ball_collider.radius),
            )

            ctx.world.add_component(
                ball_entity,
                AttachedTo(
                    entity=paddle_entity,
                    offset=offset,
                ),
            )

            # Snap it into the correct position immediately.
            ball_transform.position = paddle_transform.position + offset

    def _enforce_bounce_angles(self, ctx):
        cfg = ctx.settings.ball
        if not cfg.minimum_angle_enabled:
            return

        world = ctx.world

        candidates = {
            event.entity for event in world.get_resource(BoundsFrame).bounces
        }

        for contact in world.get_resource(CollisionFrame).contacts:
            pair = (
                match_contact(world, contact, Ball, Enemy)
                or match_contact(world, contact, Ball, PlayerShield)
                or match_contact(world, contact, Ball, Player)
            )

            if pair:
                candidates.add(pair[0])

        minimum_fraction = sin(radians(cfg.minimum_vertical_angle))

        for entity in candidates:
            if not world.has_component(entity, Ball):
                continue

            if world.has_component(entity, WaitingForLaunch):
                continue

            velocity = world.get_component(entity, Velocity)
            v = velocity.value
            speed = v.length()

            if speed <= 1e-9:
                continue

            minimum_y = speed * minimum_fraction

            # Already traveling at a sufficiently vertical angle.
            if abs(v.y) >= minimum_y:
                continue

            # Preserve upward/downward travel.
            # Exactly horizontal balls are directed upward.
            y = minimum_y if v.y > 0 else -minimum_y

            # Reduce horizontal speed to preserve total speed.
            x = sqrt(max(0.0, speed * speed - y * y))

            if v.x < 0:
                x = -x

            velocity.value = Vec2(x, y)

    def _handle_lost_balls(self, ctx):
        waves = ctx.world.get_resource(Waves)

        if (
            waves.completed
            or waves.pending is not None
            or waves.started_this_tick
        ):
            return

        world = ctx.world
        queue = world.get_resource(LifecycleQueue)

        balls = [
            entity
            for entity, _ in world.query(Ball)
            if entity not in queue.despawns
        ]

        lost = [entity for entity in balls if ball_below_floor(world, entity)]

        if not lost:
            return

        for entity in lost:
            queue.request_despawn(
                entity,
                DespawnReason.OUT_OF_BOUNDS,
                allow_respawn=False,
            )

        # A flying or held ball is still available.
        if len(lost) != len(balls):
            return

        lives = world.get_resource(Lives)
        lives.count = max(0, lives.count - 1)

        world.get_resource(PowerUpState).remaining.clear()
        world.get_resource(EnemyContactState).previous.clear()

        # Clear drops left over from the lost round.
        for entity, _ in world.query(PowerUp):
            queue.request_despawn(
                entity,
                DespawnReason.SCRIPTED,
                allow_respawn=False,
            )

        if lives.count > 0:
            queue.request_spawn("e_ball", delay=ctx.settings.respawn_delay)

    def _style_trails(self, ctx):
        world = ctx.world
        state = world.get_resource(PowerUpState)
        pending = world.get_resource(LifecycleQueue).despawns

        for entity, _, circle, trail in world.query(Ball, Circle, Trail):
            # Follow the ball's current visual size.
            trail.radius = circle.radius

            if ctx.settings.fx.trails.powerup_colors and state.active(
                PowerUpKind.FAST
            ):
                trail.color = POWERUP_STYLE[PowerUpKind.FAST][1]
            elif ctx.settings.fx.trails.powerup_colors and state.active(
                PowerUpKind.SLOW
            ):
                trail.color = POWERUP_STYLE[PowerUpKind.SLOW][1]
            else:
                trail.color = circle.color

            # Held or disappearing balls should not leave trails.
            trail.enabled = (
                ctx.settings.fx.trails.enabled
                and circle.visible
                and entity not in pending
                and not world.has_component(entity, WaitingForLaunch)
            )

            if not trail.enabled:
                trail.clear()


class AimingSystem(GameSystem[ESceneTickContext]):
    """Calculate launch trajectories, launch held balls and draw the guide."""

    phase_orders = {
        SystemPhase.SIMULATION: 360,
        SystemPhase.PRESENTATION: 30,
    }

    def on_simulation(self, ctx):
        self._update_guide(ctx)
        self._launch(ctx)

    def on_presentation(self, ctx):
        with profiler.span("aiming.presentation", "aiming_system"):
            self._render_guide(ctx)

    def __init__(self, camera_fx: CameraFX):
        self._camera_fx = camera_fx

    def _update_guide(self, ctx):
        entry = next(
            ctx.world.query(Transform, AimGuide),
            None,
        )
        if entry is None:
            return

        _, transform, guide = entry

        # Reset every tick, including when aiming ends.
        guide.visible = False
        guide.paths.clear()
        guide.launch_velocities.clear()

        ready = sorted(
            ctx.world.query(
                Ball,
                WaitingForLaunch,
                AttachedTo,
            ),
            key=lambda row: row[0],
        )

        if not ready:
            return

        target = (
            pointer_world_position(ctx, self._camera_fx)
            if ctx.intent.aim
            else None
        )

        guide.visible = target is not None

        if target is not None:
            transform.position = target

        for index, (entity, _, _, _) in enumerate(ready):
            velocity = calculate_launch_velocity(
                ctx,
                entity,
                index,
                len(ready),
                target,
            )

            guide.launch_velocities[entity] = velocity

            if guide.visible:
                guide.paths.append(predict_path(ctx, entity, velocity, guide))

    def _launch(self, ctx):
        waves = ctx.world.get_resource(Waves)

        if (
            waves.completed
            or waves.pending is not None
            or waves.started_this_tick
        ):
            return

        if not ctx.intent.launch:
            return

        world = ctx.world

        ready = sorted(
            world.query(Ball, WaitingForLaunch, AttachedTo),
            key=lambda row: row[0],
        )
        if not ready:
            return

        entry = next(world.query(AimGuide), None)
        guide = entry[1] if entry is not None else None

        factor = world.get_resource(PowerUpState).speed_factor

        for index, (entity, ball, _, _) in enumerate(ready):
            velocity = (
                guide.launch_velocities.get(entity)
                if guide is not None
                else None
            )

            if velocity is None:
                velocity = calculate_launch_velocity(
                    ctx,
                    entity,
                    index,
                    len(ready),
                    target=None,
                )

            world.get_component(entity, Velocity).value = velocity

            ball.speed_factor = factor
            ball.spin = 0.0

            world.remove_component(entity, AttachedTo)
            world.remove_component(entity, WaitingForLaunch)

        if guide is not None:
            guide.visible = False
            guide.paths.clear()
            guide.launch_velocities.clear()

    def _render_guide(self, ctx):
        queue = ctx.render_queue

        for _, transform, guide in ctx.world.query(
            Transform,
            AimGuide,
        ):
            if not guide.visible:
                continue

            # Draw trajectory dots below the reticle.
            for path in guide.paths:
                count = max(1, len(path) - 1)

                for index, point in enumerate(path):
                    progress = index / count

                    # Dots become smaller farther from the ball.
                    radius = guide.dot_radius * (1.0 - 0.55 * progress)

                    queue.circle(
                        center=point,
                        radius=radius,
                        color=(180, 210, 255),
                        layer="world",
                        z=90,
                    )

            center = transform.position
            color = (255, 255, 255)

            ring = [
                center
                + Vec2(
                    cos(tau * index / 48),
                    sin(tau * index / 48),
                )
                * guide.radius
                for index in range(48)
            ]

            queue.poly(
                points=ring,
                fill=None,
                stroke=color,
                thickness=guide.thickness,
                closed=True,
                layer="world",
                z=100,
            )

            # Two perpendicular diameters, slightly rotated.
            for axis in (Vec2(1, 0), Vec2(0, 1)):
                offset = axis.rotated(guide.rotation) * guide.radius

                queue.line(
                    a=center - offset,
                    b=center + offset,
                    color=color,
                    thickness=guide.thickness,
                    layer="world",
                    z=101,
                )


class EnemySystem(GameSystem[ESceneTickContext]):
    """Descend hex enemies and apply damage, transformations and score."""

    phase_orders = {
        SystemPhase.PRE_SIMULATION: 260,
        SystemPhase.POST_SIMULATION: 460,
    }

    def on_pre_simulation(self, ctx):
        self._descend(ctx)

    def on_post_simulation(self, ctx):
        self._hit(ctx)

    def __init__(
        self,
        particles: ParticleEmitter,
        screen_fx: ScreenEffectStack,
        camera_fx: CameraFX,
        rng: Random | None = None,
    ):
        self._rng = rng if rng is not None else Random()
        self._particles = particles
        self._screen_fx = screen_fx
        self._camera_fx = camera_fx

    def _descend(self, ctx):
        world = ctx.world
        queue = world.get_resource(LifecycleQueue)
        waves = world.get_resource(Waves)
        motion = world.get_resource(WaveMotion)

        bricks = list(
            world.query(
                Enemy,
                Transform,
                PolygonCollider,
                Velocity,
            )
        )

        # Clear last tick's velocity even when descent is paused.
        for _, _, _, _, velocity in bricks:
            velocity.value = Vec2.zero()

        active_bricks = [row for row in bricks if row[0] not in queue.despawns]

        if (
            not active_bricks
            or ctx.dt <= 0
            or motion.speed <= 0
            or waves.completed
            or waves.pending is not None
            or waves.started_this_tick
            or world.get_resource(Lives).count <= 0
        ):
            return

        has_flying_ball = any(
            entity not in queue.despawns
            and not world.has_component(entity, WaitingForLaunch)
            for entity, _ in world.query(Ball)
        )

        if not has_flying_ball:
            return

        paddle = next(
            world.query(PlayerShield, Transform, BoxCollider),
            None,
        )

        if paddle is None:
            return

        _, _, paddle_transform, paddle_collider = paddle

        paddle_top = (
            paddle_transform.position.y - paddle_collider.size.height / 2
        )
        stop_y = paddle_top - motion.clearance

        lowest_bottom = max(
            transform.position.y
            + max(vertex.y for vertex in collider.vertices)
            for _, _, transform, collider, _ in active_bricks
        )

        remaining_distance = max(
            0.0,
            stop_y - lowest_bottom,
        )

        # Clamp this tick's movement so bricks cannot overshoot.
        speed = min(
            motion.speed,
            remaining_distance / ctx.dt,
        )

        for _, _, _, _, velocity in active_bricks:
            velocity.value = Vec2(0.0, speed)

    def _hit(self, ctx):
        world = ctx.world

        if not any(world.query(Enemy)):
            return

        frame = world.get_resource(CollisionFrame)
        previous = world.get_resource(EnemyContactState)
        queue = world.get_resource(LifecycleQueue)
        score = world.get_resource(Score)
        cfg = ctx.settings
        pickups = cfg.powerups
        powered_damage = pickups.enabled and pickups.powered_damage
        transformations = []
        if cfg.bricks.explosions_enabled:
            transformations.append("explosion")
        if cfg.bricks.ghosts_enabled:
            transformations.append("ghost")

        current = set()

        for contact in frame.contacts:
            pair = match_contact(world, contact, Ball, Enemy)

            if pair:
                current.add(pair)

        # None means direct ball damage.
        # A number means explosion damage.
        damage = deque(
            (source, target, None)
            for source, target in sorted(current - previous.previous)
        )

        previous.previous = current
        ignored = set()

        while damage:
            source, entity, amount = damage.popleft()
            direct = amount is None
            brick = world.get_component(entity, Enemy)

            # Another hit may already have destroyed this brick.
            if entity in queue.despawns or brick.hits_remaining <= 0:
                if direct:
                    ignored.add((source, entity))
                continue

            if not brick.destructible:
                continue

            if cfg.bricks.ghosts_enabled and world.has_component(
                entity, GhostEnemy
            ):
                if direct:
                    ignored.add((source, entity))
                continue

            ball = world.get_component(source, Ball)

            if direct:
                amount = min(
                    ball.power if powered_damage else 1,
                    brick.hits_remaining,
                )

                powered_fast = (
                    powered_damage and ball.pierce_time > 0 and ball.power > 1
                )

                # This particular hit passes through if it kills.
                if (
                    powered_fast
                    and pickups.piercing
                    and amount == brick.hits_remaining
                ):
                    ignored.add((source, entity))

                if powered_fast:
                    velocity = world.get_component(source, Velocity)
                    velocity.value *= pickups.fast_hit_speed_retain

                # Spend actual damage, with permanent baseline 1.
                ball.power = max(1, ball.power - amount)

                if ball.power == 1:
                    ball.pierce_time = 0.0

            brick.hits_remaining = max(
                0,
                brick.hits_remaining - amount,
            )

            # Preserve surviving-brick transformations.
            if brick.hits_remaining > 0:
                if (
                    cfg.bricks.transformations_enabled
                    and transformations
                    and not world.has_component(entity, ExplodingEnemy)
                    and self._rng.random() < cfg.bricks.transform_chance
                ):
                    rect = world.get_component(entity, Polygon)

                    if self._rng.choice(transformations) == "explosion":
                        world.add_component(entity, ExplodingEnemy())
                        rect.color = (255, 110, 40)

                    else:
                        world.add_component(
                            entity,
                            GhostEnemy(
                                cfg.bricks.ghost_duration,
                                rect.color,
                            ),
                        )
                        rect.color = (65, 75, 100)

                continue

            brick_burst(world, entity, self._particles)

            explosive = cfg.bricks.explosions_enabled and world.has_component(
                entity, ExplodingEnemy
            )

            shake = cfg.fx.shake
            if shake.enabled:
                self._camera_fx.shake(
                    duration=shake.duration,
                    strength=(
                        shake.explosion_strength
                        if explosive
                        else shake.hit_strength
                    ),
                )

            flash = cfg.fx.flash
            if flash.enabled:
                self._screen_fx.flash(
                    duration=flash.duration,
                    color=flash.color,
                    peak_alpha=(
                        flash.explosion_alpha if explosive else flash.hit_alpha
                    ),
                )

            maybe_start_wrap(world)

            # Award this ball's current multiplier.
            if cfg.scoring.combos_enabled:
                score.points += brick.points * ball.combo
                ball.combo += 1
            else:
                score.points += brick.points
                ball.combo = 1

            queue.request_despawn(
                entity,
                DespawnReason.DEFEATED,
                allow_respawn=False,
            )

            # Preserve pickup drops.
            if pickups.kinds and self._rng.random() < pickups.drop_chance:
                kind = self._rng.choice(pickups.kinds)
                position = world.get_component(entity, Transform).position

                queue.request_spawn(
                    "power_up",
                    kwargs={
                        "position": Vec2(position.x, position.y),
                        "radius": pickups.pickup_radius,
                        "color": POWERUP_STYLE[kind][1],
                        "kind": kind,
                    },
                )

            # Explosions retain ownership but deal fixed damage.
            if explosive:
                for other_id, other in sorted(world.query(Enemy)):
                    if (
                        max(
                            abs(other.row - brick.row),
                            abs(other.column - brick.column),
                        )
                        == 1
                    ):
                        damage.append(
                            (source, other_id, cfg.bricks.explosion_damage)
                        )

        # These contacts already caused damage, but must not
        # cause a physical bounce.
        frame.contacts[:] = [
            contact
            for contact in frame.contacts
            if match_contact(world, contact, Ball, Enemy) not in ignored
        ]


class PowerUpSystem(GameSystem[ESceneTickContext]):
    """Maintain timed modifiers and collect or split pickups."""

    phase_orders = {
        SystemPhase.PRE_SIMULATION: 20,
        SystemPhase.POST_SIMULATION: 520,
    }

    def on_pre_simulation(self, ctx):
        self._tick(ctx)

    def on_post_simulation(self, ctx):
        self._collect(ctx)

    def __init__(self, factory: EEntityFactory, particles: ParticleEmitter):
        self._factory = factory
        self._particles = particles

    def _tick(self, ctx):
        # Keep baseline restoration active even when pickups are disabled.
        cfg = ctx.settings.powerups
        world = ctx.world
        state = world.get_resource(PowerUpState)

        state.remaining = {
            kind: seconds - ctx.dt
            for kind, seconds in state.remaining.items()
            if seconds > ctx.dt and kind in cfg.kinds
        }

        bounds = world.get_resource(WorldBounds).bounds
        width_factor = (
            cfg.wide_factor if state.active(PowerUpKind.WIDE) else 1.0
        )

        for entity, _, box in world.query(PlayerShield, BoxCollider):
            box.size = Size(
                min(
                    int(state.base_paddle_size.width * width_factor),
                    int(bounds.width),
                ),
                state.base_paddle_size.height,
            )

            visual = world.get_component(entity, Rect)
            visual.size = box.size
            visual.visible = not ctx.settings.paddle.curved

        sides = BoundsSide.ALL
        if not ctx.settings.persistent_balls:
            sides = BoundsSide.HORIZONTAL | BoundsSide.TOP

        if (
            state.active(PowerUpKind.SHIELD)
            and not ctx.settings.persistent_balls
        ):
            sides |= BoundsSide.BOTTOM

        for _, ball, velocity, constraint in world.query(
            Ball, Velocity, BoundsConstraint
        ):
            factor = state.speed_factor

            # Rescale only by the change in the active multiplier.
            velocity.value *= factor / ball.speed_factor
            ball.speed_factor = factor
            constraint.sides = sides

            if not cfg.enabled or not cfg.powered_damage:
                ball.power = 1
                ball.pierce_time = 0.0

            if ball.pierce_time > 0:
                ball.pierce_time = max(0.0, ball.pierce_time - ctx.dt)

                if ball.pierce_time == 0:
                    ball.power = 1

        if cfg.resize_ball and state.active(PowerUpKind.FAST):
            size_factor = cfg.fast_size_factor
        elif cfg.resize_ball and state.active(PowerUpKind.SLOW):
            size_factor = cfg.slow_size_factor
        else:
            size_factor = 1.0

        radius = state.base_ball_radius * size_factor

        for entity, _, circle, collider in world.query(
            Ball, Circle, CircleCollider
        ):
            circle.radius = radius
            collider.radius = radius

            # Keep held balls resting on the paddle after resizing.
            if world.has_component(entity, AttachedTo):
                attachment = world.get_component(entity, AttachedTo)
                paddle_size = world.get_component(
                    attachment.entity, BoxCollider
                ).size

                attachment.offset = Vec2(
                    0,
                    -(paddle_size.height / 2 + radius),
                )

        world.get_resource(WorldBoundsBorder).sides = sides

    def _collect(self, ctx: ESceneTickContext):
        world = ctx.world
        queue = world.get_resource(LifecycleQueue)
        state = world.get_resource(PowerUpState)
        cfg = ctx.settings.powerups
        frame = world.get_resource(CollisionFrame)

        matched_pickups = 0
        splits = 0
        particle_emit_calls = 0
        particles_requested = 0
        particles_emitted = 0
        despawns = 0

        with profiler.span("systems.powerups", "game_systems"):
            profiler.metric("contacts", len(frame.contacts))
            for contact in frame.contacts:
                pair = match_contact(world, contact, PowerUp, PlayerShield)

                if pair is None:
                    continue

                matched_pickups += 1

                pickup, paddle = pair

                # Prevent collecting the same entity twice.
                if pickup in queue.despawns:
                    continue

                local = (
                    world.get_component(pickup, Transform).position
                    - world.get_component(paddle, Transform).position
                )
                radius = world.get_component(pickup, CircleCollider).radius
                size = world.get_component(paddle, BoxCollider).size

                # Curved paddles refine the broad-phase box contact.
                if (
                    ctx.settings.paddle.curved
                    and cap_contact(local, radius, size) is None
                ):
                    continue

                kind = world.get_component(pickup, PowerUp).kind
                if kind not in cfg.kinds:
                    queue.request_despawn(
                        pickup,
                        DespawnReason.SCRIPTED,
                        allow_respawn=False,
                    )
                    despawns += 1
                    continue

                if kind == PowerUpKind.EXTRA_LIFE:
                    world.get_resource(Lives).count += 1

                elif kind == PowerUpKind.MULTIBALL:
                    splits += 1
                    with profiler.span("split_multiball", "powerups"):
                        self._split(world)

                else:
                    if kind == PowerUpKind.FAST:
                        state.remaining.pop(PowerUpKind.SLOW, None)
                    elif kind == PowerUpKind.SLOW:
                        state.remaining.pop(PowerUpKind.FAST, None)

                    # Repeated pickups refresh the duration.
                    state.remaining[kind] = cfg.duration(kind)

                    if kind in (PowerUpKind.FAST, PowerUpKind.SLOW):
                        for _, ball in world.query(Ball):
                            if not cfg.powered_damage:
                                ball.power = 1
                                ball.pierce_time = 0.0
                            elif kind == PowerUpKind.FAST:
                                ball.power = cfg.fast_power
                                # This timer also limits the powered damage lifetime.
                                ball.pierce_time = cfg.fast_duration
                            else:
                                ball.power = cfg.slow_power
                                ball.pierce_time = 0.0

                if ctx.settings.fx.particles.enabled and kind in (
                    PowerUpKind.FAST,
                    PowerUpKind.SLOW,
                    PowerUpKind.MULTIBALL,
                    PowerUpKind.STICKY,
                ):
                    with profiler.span(
                        "powerup_particles",
                        "powerups",
                    ):
                        available = self._particles.available

                        if available > 0:
                            for ball_id, _, transform in world.query(
                                Ball,
                                Transform,
                            ):
                                if available <= 0:
                                    break

                                if ball_id in queue.despawns:
                                    continue

                                burst = ctx.settings.fx.particles.pickup_burst

                                result = self._particles.emit(
                                    transform.position,
                                    POWERUP_STYLE[kind][1],
                                    burst=burst,
                                    available=available,
                                )

                                particle_emit_calls += 1
                                particles_requested += result.requested
                                particles_emitted += result.emitted

                                available -= result.emitted

                profiler.metric("matched_pickups", matched_pickups)
                profiler.metric("splits", splits)
                profiler.metric("particle_emit_calls", particle_emit_calls)
                profiler.metric("particles_requested", particles_requested)
                profiler.metric("particles_emitted", particles_emitted)
                profiler.metric("despawns", despawns)

                queue.request_despawn(
                    pickup,
                    DespawnReason.SCRIPTED,
                    allow_respawn=False,
                )

    def _split(self, world: EWorld):
        settings = world.get_resource(ShatterphaseSettings)
        cfg = settings.powerups
        if PowerUpKind.MULTIBALL not in cfg.kinds:
            return

        pending = world.get_resource(LifecycleQueue).despawns

        balls = sorted(
            entity
            for entity, _ in world.query(Ball)
            if (entity not in pending and not ball_below_floor(world, entity))
        )

        if not balls or len(balls) >= cfg.maximum_balls:
            return

        # Prefer a flying ball; otherwise duplicate a held ball.
        source = next(
            (
                entity
                for entity in balls
                if not world.has_component(entity, WaitingForLaunch)
            ),
            balls[0],
        )

        position = world.get_component(source, Transform).position
        visual = world.get_component(source, Circle)
        source_ball = world.get_component(source, Ball)
        source_velocity = world.get_component(source, Velocity).value

        count = min(2, cfg.maximum_balls - len(balls))

        spread = cfg.split_angle_degrees
        for angle in (-spread, spread)[:count]:
            clone = self._factory.create(
                "e_ball",
                position=Vec2(position.x, position.y),
                radius=visual.radius,
                color=visual.color,
            )

            clone_ball = world.get_component(clone, Ball)
            clone_ball.speed_factor = source_ball.speed_factor
            clone_ball.spin = (
                source_ball.spin if settings.ball.spin.enabled else 0.0
            )
            clone_ball.combo = source_ball.combo
            # NOTE: Test
            clone_ball.power = source_ball.power
            clone_ball.pierce_time = source_ball.pierce_time

            if world.has_component(source, AttachedTo):
                parent = world.get_component(source, AttachedTo).entity
                attach_ball(world, clone, parent)

            elif world.has_component(source, WaitingForLaunch):
                # BallSystem attaches it next tick.
                continue

            else:
                world.remove_component(clone, WaitingForLaunch)
                world.get_component(clone, Velocity).value = (
                    source_velocity.rotated(radians(angle))
                )


class WrapSystem(GameSystem[ESceneTickContext]):
    """Manage temporary side wrapping and its animated borders."""

    phase_orders = {
        SystemPhase.PRE_SIMULATION: 30,
        SystemPhase.SIMULATION: 220,
        SystemPhase.PRESENTATION: 10,
    }

    def on_pre_simulation(self, ctx):
        self._tick(ctx)

    def on_simulation(self, ctx):
        self._wrap_balls(ctx)

    def on_presentation(self, ctx):
        with profiler.span("wrap.presentation", "wrap_system"):
            self._render_border(ctx)

    def __init__(self):
        self._wrap = BoundsWrap()
        self._colliders = ColliderAccess()

    def _tick(self, ctx):
        cfg = ctx.settings.wrap
        if not cfg.enabled:
            return

        world = ctx.world
        mode = world.get_resource(WrapMode)

        mode.remaining = max(0.0, mode.remaining - ctx.dt)
        mode.cooldown = max(0.0, mode.cooldown - ctx.dt)

        period = cfg.dash_length + cfg.dash_gap

        mode.phase = (mode.phase + cfg.dash_speed * ctx.dt) % period

        # PowerUpTickSystem restores normal bounds first.
        if mode.remaining > 0:
            for _, _, constraint in world.query(Ball, BoundsConstraint):
                constraint.sides &= ~BoundsSide.HORIZONTAL

            world.get_resource(
                WorldBoundsBorder
            ).sides &= ~BoundsSide.HORIZONTAL

    def _wrap_balls(self, ctx):
        world = ctx.world

        if (
            not ctx.settings.wrap.enabled
            or world.get_resource(WrapMode).remaining <= 0
        ):
            return

        bounds = world.get_resource(WorldBounds).bounds

        for entity, _, transform in world.query(Ball, Transform):
            if world.has_component(entity, WaitingForLaunch):
                continue

            result = self._wrap.apply(
                bounds,
                transform.position,
                self._colliders.geometry(world, entity),
                sides=BoundsSide.HORIZONTAL,
            )

            if result.sides == BoundsSide.NONE:
                continue

            transform.position = result.position

            if world.has_component(entity, Trail):
                trail = world.get_component(entity, Trail)
                trail.points.clear()
                trail.clock = 0.0

    def _render_border(self, ctx):
        cfg = ctx.settings.wrap
        if not cfg.enabled or not cfg.animated_border:
            return

        mode = ctx.world.get_resource(WrapMode)

        if mode.remaining <= 0:
            return

        bounds = ctx.world.get_resource(WorldBounds).bounds
        period = cfg.dash_length + cfg.dash_gap

        for x in (bounds.left, bounds.right):
            y = bounds.top - period + mode.phase

            while y < bounds.bottom:
                start = max(bounds.top, y)
                end = min(
                    bounds.bottom,
                    y + cfg.dash_length,
                )

                if end > start:
                    ctx.render_queue.line(
                        a=Vec2(x, start),
                        b=Vec2(x, end),
                        color=(80, 220, 255),
                        thickness=2,
                        layer="world",
                        z=1,
                    )

                y += period


class CollisionSystem(GameSystem[ESceneTickContext]):
    """Detect gameplay pairs and filter ghost, held and pending contacts."""

    phase_orders = {
        SystemPhase.SIMULATION: 400,
        SystemPhase.POST_SIMULATION: 410,
    }

    def on_simulation(self, ctx):
        self._detect(ctx)

    def on_post_simulation(self, ctx):
        self._filter_contacts(ctx)

    def __init__(self):
        self._colliders = ColliderAccess()
        self._geometry = CollisionGeometry()

    def _target(self, world, entity, transform):
        collider = self._colliders.get(world, entity)
        position = transform.position
        if isinstance(collider, PolygonCollider):
            xs = [position.x + vertex.x for vertex in collider.vertices]
            ys = [position.y + vertex.y for vertex in collider.vertices]
            extent = min(xs), min(ys), max(xs), max(ys)
        elif isinstance(collider, BoxCollider):
            extent = (
                position.x - collider.size.width / 2,
                position.y - collider.size.height / 2,
                position.x + collider.size.width / 2,
                position.y + collider.size.height / 2,
            )
        else:
            extent = (
                position.x - collider.radius,
                position.y - collider.radius,
                position.x + collider.radius,
                position.y + collider.radius,
            )
        return entity, self._colliders.shape(position, collider), extent

    def _contacts(self, world, movers, targets):
        for entity, _, transform, collider in movers:
            position = transform.position
            radius = collider.radius
            shape = self._colliders.shape(position, collider)
            for other, target_shape, (left, top, right, bottom) in targets:
                if (
                    position.x + radius <= left
                    or position.x - radius >= right
                    or position.y + radius <= top
                    or position.y - radius >= bottom
                ):
                    continue
                result = self._geometry.find(shape, target_shape)
                if result is None:
                    continue
                normal, penetration = result
                if entity < other:
                    yield CollisionContact(entity, other, normal, penetration)
                else:
                    yield CollisionContact(
                        other, entity, normal * -1, penetration
                    )

    def _detect(self, ctx):
        world = ctx.world
        shields = [
            self._target(world, entity, transform)
            for entity, _, transform in world.query(PlayerShield, Transform)
        ]
        targets = shields + [
            self._target(world, entity, transform)
            for kind in (Enemy, Player)
            for entity, _, transform in world.query(kind, Transform)
        ]
        contacts = list(
            self._contacts(
                world, world.query(Ball, Transform, CircleCollider), targets
            )
        )
        contacts.extend(
            self._contacts(
                world, world.query(PowerUp, Transform, CircleCollider), shields
            )
        )
        contacts.sort(key=lambda contact: (contact.entity_a, contact.entity_b))
        world.get_resource(CollisionFrame).contacts[:] = contacts

    def _filter_contacts(self, ctx):
        world = ctx.world
        frame = world.get_resource(CollisionFrame)
        pending = world.get_resource(LifecycleQueue).despawns

        # Check raw contacts before removing ghost collisions.
        overlapping = set()

        for contact in frame.contacts:
            pair = match_contact(world, contact, Ball, GhostEnemy)

            if pair and pair[0] not in pending:
                overlapping.add(pair[1])

        for entity, ghost, rect in list(world.query(GhostEnemy, Polygon)):
            ghost.remaining = max(0.0, ghost.remaining - ctx.dt)

            # Wait until balls leave before becoming solid again.
            if not ctx.settings.bricks.ghosts_enabled or (
                ghost.remaining == 0 and entity not in overlapping
            ):
                rect.color = ghost.original_color
                world.remove_component(entity, GhostEnemy)

        kept = []

        for contact in frame.contacts:
            if contact.entity_a in pending or contact.entity_b in pending:
                continue

            pair = match_contact(world, contact, Ball, Enemy)

            if pair:
                ball, brick = pair

                if not world.has_component(
                    ball, WaitingForLaunch
                ) and not world.has_component(brick, GhostEnemy):
                    kept.append(contact)

                continue

            pair = match_contact(
                world, contact, Ball, PlayerShield
            ) or match_contact(world, contact, Ball, Player)

            if pair:
                if not world.has_component(pair[0], WaitingForLaunch):
                    kept.append(contact)

                continue

            if match_contact(world, contact, PowerUp, PlayerShield):
                kept.append(contact)

        frame.contacts[:] = kept


class EffectsSystem(GameSystem[ESceneTickContext]):
    """Update particle motion and trails, and present trail geometry."""

    phase_orders = {
        SystemPhase.SIMULATION: 35,
        SystemPhase.POST_SIMULATION: 550,
        SystemPhase.PRESENTATION: 35,
    }

    def __init__(self):
        self._particles = ParticleUpdateSystem()
        self._trails = TrailSystem()
        self._render_trails = TrailRenderSystem()

    def on_simulation(self, ctx):
        self._particles.step(ctx)

    def on_post_simulation(self, ctx):
        self._trails.step(ctx)

    def on_presentation(self, ctx):
        with profiler.span("effects.presentation", "effects_system"):
            self._render_trails.step(ctx)


class HUDSystem(GameSystem[ESceneTickContext]):
    """Synchronize score, lives, wave progress and active modifiers."""

    phase_orders = {
        SystemPhase.POST_SIMULATION: 560,
    }

    def on_post_simulation(self, ctx):
        if not ctx.settings.hud.enabled:
            return

        world = ctx.world
        lives = world.get_resource(Lives).count
        score = world.get_resource(Score).points
        state = world.get_resource(PowerUpState)
        waves = world.get_resource(Waves)

        effects = "  ".join(
            f"{POWERUP_STYLE[kind][0]}:{seconds:.0f}s"
            for kind, seconds in state.remaining.items()
            if ctx.settings.hud.show_powerup_timers and state.active(kind)
        )

        for _, _, text in world.query(UIDisplay, Text):
            text.content = f"Lives: {lives} | Score: {score} | Wave: {waves.current}/{waves.max}"

            if waves.completed:
                text.content += " | Complete!"
            elif lives == 0:
                text.content += " | Game over"

            if effects:
                text.content += f" | {effects}"


# Scene and application


@SceneRegistry.implementation("main")
class EScene(Scene[EWorld, EIntent, ESceneTickContext]):
    world_type = EWorld
    # query_strategy_type = IntersectionQueryStrategy
    intent_type = EIntent
    tick_context_type = ESceneTickContext
    factory_type = EEntityFactory
    shared_resource_types = (ShatterphaseSettings,)

    def bounds(self, ctx):
        width, height = ctx.viewport.virtual_w, ctx.viewport.virtual_h
        playfield_width = min(580, width - 80)
        return Bounds(
            left=(width - playfield_width) / 2,
            right=(width + playfield_width) / 2,
            top=40,
            bottom=height - 40,
        )

    def bounds_border(self, ctx):
        settings = self.world.get_resource(ShatterphaseSettings)
        sides = (
            BoundsSide.ALL
            if settings.persistent_balls
            else (BoundsSide.HORIZONTAL | BoundsSide.TOP)
        )
        return WorldBoundsBorder(
            thickness=2, sides=sides, color=settings.color.boundary
        )

    def resources(self, ctx):
        settings = self.world.get_resource(ShatterphaseSettings)
        bounds = self.bounds(ctx)
        area = Bounds(
            left=bounds.left + 64,
            right=bounds.right - 64,
            top=bounds.top + 34,
            bottom=bounds.top + bounds.height * 0.50,
        )
        definitions = wave_definitions(settings, area)
        bounds = self.bounds(ctx)
        if (
            max(settings.paddle.width, 2 * settings.player.radius)
            >= bounds.width
        ):
            raise ValueError("The playfield must be wider than the player")
        if (
            2 * settings.player.radius + settings.paddle.height
            >= bounds.height
        ):
            raise ValueError("The playfield must be taller than the player")
        self.particles = ParticleEmitter(
            self.world,
            max_particles=(
                settings.fx.particles.maximum
                if settings.fx.particles.enabled
                else 0
            ),
        )
        return (
            CollisionFrame(),
            Lives(settings.initial_lives),
            Score(),
            EnemyContactState(),
            PowerUpState(
                base_paddle_size=Size(
                    settings.paddle.width, settings.paddle.height
                ),
                base_ball_radius=settings.ball.radius,
                settings=settings.powerups,
            ),
            WrapMode(),
            WaveMotion(),
            area,
            Waves(iter(definitions), max=len(definitions)),
        )

    def spawn_definitions(self, ctx):
        settings = self.world.get_resource(ShatterphaseSettings)
        bounds = self.bounds(ctx)
        position = Vec2(bounds.center.x, bounds.bottom - 60)
        shield_position = position + Vec2(
            0, -(settings.player.radius + settings.paddle.height / 2)
        )
        return {
            "player": SpawnDefinition(
                "player",
                make_kwargs=lambda: {
                    "position": Vec2(position.x, position.y),
                    "radius": settings.player.radius,
                    "color": settings.color.paddle,
                },
            ),
            "player_shield": SpawnDefinition(
                "player_shield",
                make_kwargs=lambda: {
                    "position": Vec2(shield_position.x, shield_position.y),
                    "size": Size(
                        settings.paddle.width, settings.paddle.height
                    ),
                    "color": settings.color.paddle,
                },
            ),
            "e_ball": SpawnDefinition(
                "e_ball",
                make_kwargs=lambda: {
                    "position": shield_position
                    + Vec2(
                        0, -(settings.paddle.height / 2 + settings.ball.radius)
                    ),
                    "radius": settings.ball.radius,
                    "color": settings.color.ball,
                },
            ),
            "e_hex": SpawnDefinition(
                "e_hex",
                make_kwargs=lambda: {"vertices": hex_vertices(20)},
            ),
            "power_up": SpawnDefinition("power_up"),
            "aim": SpawnDefinition("aim"),
            "ui": SpawnDefinition(
                "ui",
                make_kwargs=lambda: {
                    "position": Vec2(bounds.center.x, 12),
                    "color": settings.color.text.primary,
                    "align": "center",
                },
            ),
        }

    def entities(self, ctx):
        settings = self.world.get_resource(ShatterphaseSettings)
        yield EntitySpawn("player")
        yield EntitySpawn("player_shield")
        # WaveSystem queues one ball for the first and each later wave.
        if settings.enable_aiming:
            yield EntitySpawn("aim")
        if settings.hud.enabled:
            yield EntitySpawn("ui")
        if settings.powerups.enabled and settings.powerups.test_powerup:
            kind = PowerUpKind[settings.powerups.test_powerup.upper()]
            bounds = self.bounds(ctx)
            yield EntitySpawn(
                "power_up",
                kwargs={
                    "position": Vec2(bounds.center.x, bounds.top + 100),
                    "radius": settings.powerups.pickup_radius,
                    "color": POWERUP_STYLE[kind][1],
                    "kind": kind,
                },
            )

    def game_systems(self, ctx):
        return (
            WaveSystem(),
            PlayerSystem(),
            BallSystem(),
            AimingSystem(self.camera_fx),
            EnemySystem(self.particles, self.screen_fx, self.camera_fx),
            PowerUpSystem(self.factory, self.particles),
            WrapSystem(),
            CollisionSystem(),
            EffectsSystem(),
            HUDSystem(),
        )

    def on_enter(self, ctx):
        pass

    def builtin_overrides(self, ctx):
        # Grouped contact hooks run after detection and before the response.
        # Keep response ahead of pickup collection and ball round rules.
        return {
            "collision_detection": None,
            "collision_response": SystemRegistration(
                CollisionResponseSystem(),
                phase=SystemPhase.POST_SIMULATION,
                order=500,
            ),
            "collision_direction": SystemRegistration(
                CollisionDirectionSystem(),
                phase=SystemPhase.POST_SIMULATION,
                order=530,
            ),
        }

    def on_present(self, ctx):
        viewport = ctx.scene_context.viewport
        ctx.render_queue.text(
            x=viewport.virtual_w / 2,
            y=viewport.virtual_h - 24,
            text="WASD: move   Space / left click: launch   Hold right click: aim",
            color=ctx.settings.color.text.secondary,
            font_size=14,
            align="center",
        )


def create_app(config: TatuyConfigDict | None = None) -> TatuyApp:
    """Create the reusable high-density entities pressure experiment."""
    defaults: TatuyConfigDict = {
        "engine": {
            "fps": 0,
            "debug_overlay": True,
        },
        "backend": {
            "window": {"width": 1280, "height": 720},
            "renderer": {"background_color": (15, 18, 32)},
            "capture": {
                "enabled": True,
            },
        },
        "settings": {
            "breakout": {
                # True: start with the densest enemy grid for profiling.
                "profiling_max_enemies": True,
                "paddle": {"curved": False},
                "powerups": {"drop_chance": 0.9, "allowed": ["multiball"]},
            },
            "replay": {
                "enabled": True,
                "filename": "entities.jsonl",
                "game_id": "entities",
                "initial_scene": "main",
                "seed": 42,
            },
        },
        "profiler": {"enabled": True},
    }
    return TatuyApp(merge_config(defaults, config or {}))


def main() -> None:
    create_app().run()


if __name__ == "__main__":
    main()
