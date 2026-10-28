"""Deterministic experiment rules; no backend or scene dependencies."""

from __future__ import annotations

from dataclasses import dataclass, field
from math import atan2, ceil, cos, pi, sin
from random import Random

from tatuy.math.vec2 import Vec2


@dataclass(frozen=True)
class Settings:
    """Tuning knobs for the laboratory, in seconds and world pixels."""

    columns: int = 24
    rows: int = 14
    cell: int = 26
    left: int = 88
    top: int = 126
    reproduction: float = 6.0
    seed_interval: float = 15.0
    consumption: float = 0.10
    recovery: float = 0.08
    ball_speed: float = 290.0
    spore_speed: float = 90.0
    spore_cost: float = 25.0


@dataclass
class Tile:
    """Ground health and mutually exclusive rooted colony state."""

    moss: float = 0.75
    bacteria: int = 0
    fungus: bool = False
    age: float = 0.0
    seed_age: float = 0.0


@dataclass
class Ball:
    """A reusable bouncing containment projectile."""

    position: Vec2
    velocity: Vec2 = field(default_factory=Vec2.zero)
    flying: bool = False


@dataclass
class Spore:
    """A travelling colony seed with a fixed landing destination."""

    position: Vec2
    target: Vec2
    friendly: bool


class Arena:
    """Shared state. Colonies are fixed grid occupants, never moving actors."""

    def __init__(self, settings: Settings | None = None, seed: int = 42):
        self.settings = settings or Settings()
        self.seed = seed
        self.rng = Random(seed)
        cfg = self.settings
        self.center = Vec2(400, 386)
        self.tiles = [
            Tile(moss=self.rng.uniform(0.55, 1.0))
            for _ in range(cfg.columns * cfg.rows)
        ]
        self.angle = -pi / 2
        self.ball = Ball(self.center + self.direction * 87)
        self.spores: list[Spore] = []
        self.energy = 60.0
        self.health = 100.0
        self.elapsed = 0.0
        self.destroyed = 0
        self.blocked = 0
        self.paused = False
        self.spreading = True
        self.seeding = True
        self.accumulator = 0.0
        self.message = (
            "Contain infection. Protect moss. F sends a fungal spore."
        )
        for column, row in ((3, 2), (11, 1), (20, 3)):
            self.place(self.index(column, row), "bacteria")
        self.place(self.index(12, 6), "fungus")

    @property
    def direction(self) -> Vec2:
        """Outward direction of the orbital shield."""
        return Vec2(cos(self.angle), sin(self.angle))

    @property
    def shield(self) -> Vec2:
        """Shield center on the tether orbit."""
        return self.center + self.direction * 74

    def index(self, column: int, row: int) -> int:
        """Flatten a grid coordinate."""
        return row * self.settings.columns + column

    def position(self, index: int) -> Vec2:
        """Return a tile center in world coordinates."""
        cfg = self.settings
        row, column = divmod(index, cfg.columns)
        return Vec2(
            cfg.left + (column + 0.5) * cfg.cell,
            cfg.top + (row + 0.5) * cfg.cell,
        )

    def tile_at(self, position: Vec2) -> int | None:
        """Resolve ground under a point, rejecting arena margins."""
        cfg = self.settings
        column = int((position.x - cfg.left) // cfg.cell)
        row = int((position.y - cfg.top) // cfg.cell)
        if 0 <= column < cfg.columns and 0 <= row < cfg.rows:
            return self.index(column, row)
        return None

    def neighbors(self, index: int) -> list[int]:
        """Return cardinal neighbors without wrapping rows."""
        cfg = self.settings
        row, column = divmod(index, cfg.columns)
        return [
            self.index(x, y)
            for x, y in (
                (column - 1, row),
                (column + 1, row),
                (column, row - 1),
                (column, row + 1),
            )
            if 0 <= x < cfg.columns and 0 <= y < cfg.rows
        ]

    def occupiable(self, index: int) -> bool:
        """Keep rooted colonies outside the player core."""
        return (self.position(index) - self.center).length() > 49

    def place(self, index: int | None, kind: str) -> None:
        """Explicit sandbox editing, including while paused."""
        if index is None:
            return
        tile = self.tiles[index]
        if kind == "moss":
            tile.moss = 1.0
        elif kind == "clear":
            tile.bacteria, tile.fungus = 0, False
            tile.age = tile.seed_age = 0.0
        elif self.occupiable(index):
            tile.bacteria = 2 if kind == "bacteria" else 0
            tile.fungus = kind == "fungus"
            tile.age = tile.seed_age = 0.0

    def aim(self, target: Vec2) -> None:
        """Rotate the shield toward a world point."""
        offset = target - self.center
        if offset.length_squared() > 1:
            self.angle = atan2(offset.y, offset.x)

    def launch(self) -> None:
        """Release an attached ball outward from the shield."""
        if not self.ball.flying:
            self.ball.position = self.center + self.direction * 87
            self.ball.velocity = self.direction * self.settings.ball_speed
            self.ball.flying = True

    def release_fungus(self, target: Vec2) -> None:
        """Spend moss-supported energy on a friendly colony seed."""
        index = self.tile_at(target)
        if index is None or not self.occupiable(index):
            self.message = "Choose ground outside the fungus core."
            return
        if self.energy < self.settings.spore_cost:
            self.message = (
                "Not enough energy: healthy nearby moss restores it."
            )
            return
        if len(self.spores) >= 96:
            return
        self.energy -= self.settings.spore_cost
        self.spores.append(
            Spore(
                self.center + self.direction * 85, self.position(index), True
            )
        )

    def support(self) -> float:
        """Average nearby usable moss; infected ground contributes zero."""
        nearby = [
            (0.0 if tile.bacteria else tile.moss)
            for index, tile in enumerate(self.tiles)
            if (self.position(index) - self.center).length() < 145
            and self.occupiable(index)
        ]
        return sum(nearby) / len(nearby) if nearby else 0.0


class Ecology:
    """Spread uses a generation snapshot: newborns cannot chain this tick."""

    @staticmethod
    def step(arena: Arena, dt: float) -> None:
        """Advance rooted growth, moss and symbiotic support."""
        cfg = arena.settings
        old_moss = [tile.moss for tile in arena.tiles]
        births: set[int] = set()
        for index, tile in enumerate(arena.tiles):
            neighbors = arena.neighbors(index)
            if tile.bacteria:
                tile.moss = max(0.0, tile.moss - cfg.consumption * dt)
                tile.age += dt
                tile.seed_age += dt
                if tile.age >= cfg.reproduction:
                    tile.age %= cfg.reproduction
                    choices = [
                        n
                        for n in neighbors
                        if not arena.tiles[n].bacteria
                        and arena.tiles[n].moss > 0.15
                        and arena.occupiable(n)
                    ]
                    if arena.spreading and choices:
                        births.add(arena.rng.choice(choices))
                if tile.seed_age >= cfg.seed_interval:
                    tile.seed_age %= cfg.seed_interval
                    if arena.seeding and len(arena.spores) < 96:
                        target = arena.rng.randrange(len(arena.tiles))
                        arena.spores.append(
                            Spore(
                                arena.position(index),
                                arena.position(target),
                                False,
                            )
                        )
            else:
                source = any(old_moss[n] > 0.4 for n in neighbors)
                nursery = tile.fungus or any(
                    arena.tiles[n].fungus for n in neighbors
                )
                rate = cfg.recovery if nursery else cfg.recovery * 0.15
                if source or nursery:
                    tile.moss = min(1.0, tile.moss + rate * dt)
        for index in sorted(births):
            arena.place(index, "bacteria")
        support = arena.support()
        arena.energy = min(100.0, arena.energy + support * 7 * dt)
        # Starvation is gradual; the laboratory continues at zero health.
        arena.health = max(
            0.0, min(100.0, arena.health + (support - 0.35) * 3 * dt)
        )
        arena.elapsed += dt


class Projectiles:
    """Bounded substeps resolve ball contacts against local grid candidates."""

    @staticmethod
    def step(arena: Arena, dt: float) -> None:
        """Advance the ball and airborne seeds."""
        if arena.ball.flying:
            steps = max(1, ceil(arena.settings.ball_speed * dt / 4))
            for _ in range(steps):
                Projectiles._ball(arena, dt / steps)
        else:
            arena.ball.position = arena.center + arena.direction * 87
        survivors = []
        for spore in arena.spores:
            if Projectiles._spore(arena, spore, dt):
                survivors.append(spore)
        arena.spores = survivors

    @staticmethod
    def _ball(arena: Arena, dt: float) -> None:
        ball, cfg = arena.ball, arena.settings
        ball.position += ball.velocity * dt
        for axis, low, high in (
            ("x", cfg.left + 5, cfg.left + cfg.columns * cfg.cell - 5),
            ("y", cfg.top + 5, cfg.top + cfg.rows * cfg.cell - 5),
        ):
            value = getattr(ball.position, axis)
            if value < low or value > high:
                setattr(ball.position, axis, max(low, min(high, value)))
                setattr(ball.velocity, axis, -getattr(ball.velocity, axis))
        offset = ball.position - arena.shield
        normal = arena.direction
        tangent = Vec2(-normal.y, normal.x)
        if (
            abs(offset.dot(tangent)) < 35
            and abs(offset.dot(normal)) < 10
            and ball.velocity.dot(normal) < 0
        ):
            direction = (
                normal + tangent * (offset.dot(tangent) / 45)
            ).normalized()
            ball.velocity = direction * cfg.ball_speed
            ball.position += normal * 11
        # A miss recalls the ball rather than removing a life.
        if (ball.position - arena.center).length() < 23:
            ball.flying = False
            return
        column = int((ball.position.x - cfg.left) // cfg.cell)
        row = int((ball.position.y - cfg.top) // cfg.cell)
        for y in range(max(0, row - 1), min(cfg.rows, row + 2)):
            for x in range(max(0, column - 1), min(cfg.columns, column + 2)):
                index = arena.index(x, y)
                tile = arena.tiles[index]
                delta = ball.position - arena.position(index)
                radius = 15.0
                if tile.bacteria and delta.length_squared() < radius**2:
                    normal = delta.normalized()
                    if normal.length_squared() == 0:
                        normal = ball.velocity.normalized() * -1
                    ball.position = arena.position(index) + normal * radius
                    approach = ball.velocity.dot(normal)
                    if approach < 0:
                        ball.velocity -= normal * (2 * approach)
                        tile.bacteria -= 1
                        if not tile.bacteria:
                            arena.destroyed += 1
                            tile.age = tile.seed_age = 0.0
                    return

    @staticmethod
    def _spore(arena: Arena, spore: Spore, dt: float) -> bool:
        if not spore.friendly:
            if (spore.position - arena.shield).length() < 32:
                arena.blocked += 1
                return False
            if (spore.position - arena.ball.position).length() < 11:
                if arena.ball.flying:
                    arena.blocked += 1
                    return False
        delta = spore.target - spore.position
        distance = arena.settings.spore_speed * dt
        if delta.length() > distance:
            spore.position += delta.normalized() * distance
            return True
        index = arena.tile_at(spore.target)
        if index is not None and arena.occupiable(index):
            tile = arena.tiles[index]
            if spore.friendly:
                if not tile.bacteria:
                    arena.place(index, "fungus")
            elif tile.moss > 0.15 and not tile.bacteria:
                arena.place(index, "bacteria")
        return False
