from tatuy import TatuyApp
from tatuy.ecs import GameSystem, World
from tatuy.geometry.size import Size
from tatuy.math.vec2 import Vec2
from tatuy.scenes import Intent, Scene, SceneRegistry, SceneTickContext


class DemoWorld(World): ...


class DemoIntent(Intent):
    def update_from(self, input_frame):
        pass


class DemoContext(SceneTickContext[DemoWorld, DemoIntent]): ...


class CanvasSystem(GameSystem[DemoContext]):
    def on_presentation(self, ctx: DemoContext) -> None:
        ctx.canvas.rect(
            position=Vec2(180, 220),
            size=Size(180, 100),
            color=(90, 170, 240),
        )
        ctx.canvas.circle(
            center=Vec2(520, 270),
            radius=55,
            color=(240, 150, 90),
        )
        ctx.canvas.text(
            position=Vec2(320, 420),
            text="Canvas is a simple immediate drawing facade",
            font_size=24,
        )


@SceneRegistry.implementation("main")
class DemoScene(Scene[DemoWorld, DemoIntent, DemoContext]):
    world_type = DemoWorld
    intent_type = DemoIntent
    tick_context_type = DemoContext

    def game_systems(self, ctx):
        return (CanvasSystem(),)

    def on_enter(self, ctx):
        pass


def main() -> None:
    TatuyApp().run()


if __name__ == "__main__":
    main()
