"""Shatterphase infection laboratory, independent of the tree experiments."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from tatuy import TatuyApp, TatuyConfigDict
from tatuy.ecs.system import GameSystem
from tatuy.ecs.world import World
from tatuy.geometry.size import Size
from tatuy.graphics.render.queue import RenderQueue
from tatuy.input.frame import InputFrame
from tatuy.input.keys import Key
from tatuy.math.vec2 import Vec2
from tatuy.scenes.context import Intent, SceneContext, SceneTickContext
from tatuy.scenes.registry import SceneRegistry
from tatuy.scenes.scene import Scene

if __package__:
    from .ecology import Arena, Ecology, Projectiles
else:  # Browser staging imports app.py as a top-level module.
    from ecology import Arena, Ecology, Projectiles


class MainWorld(World):
    """Owns the arena resource."""


@dataclass
class MainIntent(Intent):
    """Device snapshots are translated to laboratory commands."""

    pressed: set[Key] = field(default_factory=set)
    pointer: Vec2 = field(default_factory=Vec2.zero)
    pointer_inside: bool = False

    def update_from(self, input_frame: InputFrame) -> None:
        self.pressed = set(input_frame.keys_pressed)
        self.pointer = Vec2(*input_frame.mouse_pos)
        self.pointer_inside = input_frame.mouse_inside


class MainContext(SceneTickContext[MainWorld, MainIntent]):
    """Typed experiment context."""


class LaboratoryControls(GameSystem[MainContext]):
    """Edits and aiming remain available while simulation is paused."""

    def on_control(self, ctx: MainContext) -> None:
        arena = ctx.world.get_resource(Arena)
        keys = ctx.intent.pressed
        if Key.R in keys:
            arena = Arena(arena.settings, arena.seed)
            ctx.world.add_resource(arena)
        if Key.P in keys:
            arena.paused = not arena.paused
            arena.accumulator = 0.0
        if Key.T in keys:
            arena.spreading = not arena.spreading
        if Key.Y in keys:
            arena.seeding = not arena.seeding
        pointer = ctx.intent.pointer
        if ctx.intent.pointer_inside:
            arena.aim(pointer)
            index = arena.tile_at(pointer)
            for key, kind in (
                (Key.B, "bacteria"),
                (Key.G, "fungus"),
                (Key.M, "moss"),
                (Key.X, "clear"),
            ):
                if key in keys:
                    arena.place(index, kind)
            if Key.F in keys:
                arena.release_fungus(pointer)
        if Key.SPACE in keys:
            arena.launch()
        if Key.C in keys:
            arena.ball.flying = False


class ArenaSimulation(GameSystem[MainContext]):
    """Fixed steps bound collision travel and make spread reproducible."""

    def on_simulation(self, ctx: MainContext) -> None:
        arena = ctx.world.get_resource(Arena)
        if arena.paused:
            arena.accumulator = 0.0
            if Key.N in ctx.intent.pressed:
                Ecology.step(arena, 1 / 120)
                Projectiles.step(arena, 1 / 120)
            return
        arena.accumulator += max(0.0, min(ctx.dt, 0.25))
        while arena.accumulator >= 1 / 120:
            Ecology.step(arena, 1 / 120)
            Projectiles.step(arena, 1 / 120)
            arena.accumulator -= 1 / 120


class ArenaRenderer:
    """Uses Tatuy draw commands only; never mutates simulation state."""

    @staticmethod
    def ground(queue: RenderQueue, arena: Arena) -> None:
        """Draw moss health, colony health and reproduction progress."""
        cfg = arena.settings
        for index, tile in enumerate(arena.tiles):
            center = arena.position(index)
            color = (
                int(34 + tile.moss * 29),
                int(39 + tile.moss * 71),
                int(39 + tile.moss * 28),
            )
            queue.rect(
                center=center,
                size=Size(cfg.cell - 2, cfg.cell - 2),
                color=color,
            )
            if tile.bacteria:
                queue.circle(
                    center=center, radius=10, color=(205, 107, 125), z=2
                )
                queue.circle(
                    center=center + Vec2(-3, -2),
                    radius=2,
                    color=(99, 42, 67),
                    z=3,
                )
                queue.circle(
                    center=center + Vec2(4, 3),
                    radius=2,
                    color=(99, 42, 67),
                    z=3,
                )
                progress = min(1.0, tile.age / cfg.reproduction)
                queue.line(
                    a=center + Vec2(-10, 13),
                    b=center + Vec2(-10 + 20 * progress, 13),
                    color=(247, 173, 148),
                    thickness=2,
                    z=3,
                )
                if tile.bacteria == 1:
                    queue.line(
                        a=center + Vec2(-5, -5),
                        b=center + Vec2(5, 5),
                        color=(255, 224, 196),
                        z=4,
                    )
            elif tile.fungus:
                queue.line(
                    a=center + Vec2(0, 8),
                    b=center + Vec2(0, -5),
                    color=(207, 185, 224),
                    thickness=3,
                    z=2,
                )
                queue.circle(
                    center=center + Vec2(0, -5),
                    radius=7,
                    color=(177, 151, 213),
                    z=3,
                )

    @staticmethod
    def actors(queue: RenderQueue, arena: Arena) -> None:
        """Draw the core, tether, shield, ball and airborne seeds."""
        queue.circle(
            center=arena.center, radius=24, color=(196, 173, 218), z=5
        )
        queue.circle(
            center=arena.center + Vec2(0, -5),
            radius=17,
            color=(225, 204, 233),
            z=6,
        )
        queue.line(
            a=arena.center,
            b=arena.shield,
            color=(159, 132, 169),
            thickness=2,
            z=4,
        )
        normal = arena.direction
        tangent = Vec2(-normal.y, normal.x) * 30
        queue.line(
            a=arena.shield - tangent,
            b=arena.shield + tangent,
            color=(244, 206, 139),
            thickness=9,
            z=7,
        )
        queue.circle(
            center=arena.ball.position, radius=5, color=(244, 236, 200), z=8
        )
        if not arena.ball.flying:
            queue.line(
                a=arena.ball.position,
                b=arena.ball.position + normal * 45,
                color=(244, 206, 139),
                thickness=1,
                z=7,
            )
        for spore in arena.spores:
            color = (190, 160, 239) if spore.friendly else (250, 144, 151)
            queue.circle(center=spore.position, radius=4, color=color, z=8)

    @staticmethod
    def hud(queue: RenderQueue, arena: Arena) -> None:
        """Keep controls and ecology measurements visible."""
        bacteria = sum(bool(tile.bacteria) for tile in arena.tiles)
        moss = sum(tile.moss for tile in arena.tiles) / len(arena.tiles)
        status = "PAUSED" if arena.paused else "RUNNING"
        lines = [
            (12, "INFECTION ARENA | Shatterphase systems laboratory", 20),
            (
                40,
                f"{status}  Time {arena.elapsed:.1f}s  "
                f"Colonies {bacteria}  Moss {moss:.0%}  "
                f"Local support {arena.support():.0%}",
                15,
            ),
            (
                62,
                f"Health {arena.health:.0f}  Energy {arena.energy:.0f}/100  "
                f"Cleared {arena.destroyed}  Seeds blocked {arena.blocked}",
                15,
            ),
            (
                84,
                f"Reproduction [T]: {arena.spreading}  "
                f"Bacterial seeds [Y]: {arena.seeding}",
                15,
            ),
            (
                506,
                "Mouse: aim shield | SPACE: launch | C: recall | "
                "F: fungal spore (25 energy)",
                15,
            ),
            (
                528,
                "P: pause | N: one tick | R: reset same seed | "
                "T/Y: toggle reproduction/seeds",
                15,
            ),
            (
                550,
                "Under pointer: B bacteria | G fungus | M restore moss | "
                "X clear colony",
                15,
            ),
            (576, arena.message, 14),
        ]
        for y, text, size in lines:
            queue.text(
                x=14, y=y, text=text, font_size=size, color=(225, 226, 216)
            )


@SceneRegistry.implementation("main")
class MainScene(Scene[MainWorld, MainIntent, MainContext]):
    """Compose laboratory controls, simulation and presentation."""

    world_type = MainWorld
    intent_type = MainIntent
    tick_context_type = MainContext

    def resources(self, ctx: SceneContext) -> Iterable[object]:
        yield Arena()

    def game_systems(self, ctx: SceneContext) -> Iterable[GameSystem]:
        yield LaboratoryControls()
        yield ArenaSimulation()

    def on_enter(self, ctx: SceneContext) -> None:
        """Resources and systems are declared through scene hooks."""

    def on_present(self, ctx: MainContext) -> None:
        arena = ctx.world.get_resource(Arena)
        ArenaRenderer.ground(ctx.render_queue, arena)
        ArenaRenderer.actors(ctx.render_queue, arena)
        ArenaRenderer.hud(ctx.render_queue, arena)


def create_app(config: TatuyConfigDict | None = None) -> TatuyApp:
    """Create the reusable infection-arena application."""
    return TatuyApp(config)


def main() -> None:
    """Run through the Tatuy CLI target loader."""
    create_app().run()


if __name__ == "__main__":
    main()
