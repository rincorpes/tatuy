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


class DrawSystem(GameSystem[DemoContext]):
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
    world_type = DemoWorld
    intent_type = DemoIntent
    tick_context_type = DemoContext

    def game_systems(self, ctx):
        return (DrawSystem(),)

    def on_enter(self, ctx):
        pass


def main() -> None:
    TatuyApp().run()


if __name__ == "__main__":
    main()
