"""Render semantic rectangle and circle commands through Tatuy's render queue."""

from tatuy import TatuyApp
from tatuy.ecs import GameSystem, World
from tatuy.geometry.size import Size
from tatuy.math.vec2 import Vec2
from tatuy.scenes import Intent, Scene, SceneRegistry, SceneTickContext


class DemoWorld(World):
    """World used by the render-queue fundamental."""


class DemoIntent(Intent):
    """No-op intent for the rendering-only example."""

    def update_from(self, input_frame):
        """Ignore input because this example demonstrates rendering only."""
        del input_frame


class DemoContext(SceneTickContext[DemoWorld, DemoIntent]):
    """Typed context for the render-queue fundamental."""


class DrawSystem(GameSystem[DemoContext]):
    """Submit one rectangle and one circle to the semantic render queue."""

    def on_presentation(self, ctx: DemoContext) -> None:
        ctx.render_queue.rect(
            center=Vec2(300, 300),
            size=Size(180, 100),
            color=(90, 170, 240),
            z=0,
        )
        ctx.render_queue.circle(
            center=Vec2(500, 300),
            radius=50,
            color=(240, 150, 90),
            z=1,
        )


@SceneRegistry.implementation("main")
class DemoScene(Scene[DemoWorld, DemoIntent, DemoContext]):
    """Scene that exposes the render-queue drawing system."""

    world_type = DemoWorld
    intent_type = DemoIntent
    tick_context_type = DemoContext

    def game_systems(self, ctx):
        return (DrawSystem(),)

    def on_enter(self, ctx):
        pass


def create_app() -> TatuyApp:
    """Create the reusable Tatuy application for desktop or hosted launchers."""
    return TatuyApp()


def main() -> None:
    """Run the example with Tatuy's default desktop runtime host."""
    create_app().run()


if __name__ == "__main__":
    main()
