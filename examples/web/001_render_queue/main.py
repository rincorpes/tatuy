"""Minimal Tatuy browser spike for pygame-ce + Pygbag."""

from __future__ import annotations

import asyncio

# Pygbag discovers WASM package dependencies from top-level imports in main.py.
# Keep this explicit even though Tatuy loads the concrete backend dynamically.
import pygame

from tatuy import TatuyApp
from tatuy.ecs import GameSystem, World
from tatuy.geometry.size import Size
from tatuy.input.keys import Key
from tatuy.math.vec2 import Vec2
from tatuy.scenes import Intent, Scene, SceneRegistry, SceneTickContext

PYGAME_PRELOAD = pygame


class DemoWorld(World):
    """World used by the web rendering spike."""


class DemoIntent(Intent):
    """Capture minimal keyboard and pointer state for browser verification."""

    move_up: bool = False
    pointer_position: tuple[int, int] = (500, 300)
    pointer_inside: bool = False

    def update_from(self, input_frame) -> None:
        self.move_up = input_frame.is_down(Key.W)
        self.pointer_position = input_frame.mouse_pos
        self.pointer_inside = input_frame.mouse_inside


class DemoContext(SceneTickContext[DemoWorld, DemoIntent]):
    """Typed scene context for the web rendering spike."""


class DrawSystem(GameSystem[DemoContext]):
    """Submit a rectangle and circle through Tatuy's semantic render queue."""

    def on_presentation(self, ctx: DemoContext) -> None:
        rect_y = 220 if ctx.intent.move_up else 300
        circle_position = (
            ctx.intent.pointer_position
            if ctx.intent.pointer_inside
            else (500, 300)
        )
        ctx.render_queue.rect(
            center=Vec2(300, rect_y),
            size=Size(180, 100),
            color=(90, 170, 240),
            z=0,
        )
        ctx.render_queue.circle(
            center=Vec2(*circle_position),
            radius=50,
            color=(240, 150, 90),
            z=1,
        )


@SceneRegistry.implementation("main")
class DemoScene(Scene[DemoWorld, DemoIntent, DemoContext]):
    """Single scene used by the first browser compatibility spike."""

    world_type = DemoWorld
    intent_type = DemoIntent
    tick_context_type = DemoContext

    def game_systems(self, ctx):
        del ctx
        return (DrawSystem(),)

    def on_enter(self, ctx) -> None:
        del ctx


async def main() -> None:
    """Run Tatuy through the explicit cooperative host path."""
    app = TatuyApp(
        {
            "capabilities": {"capture": False},
        }
    )
    await app.run_async()


asyncio.run(main())
