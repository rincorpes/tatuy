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


class LayerSystem(GameSystem[DemoContext]):
    def on_presentation(self, ctx: DemoContext) -> None:
        ctx.render_queue.rect(
            center=Vec2(400, 300),
            size=Size(260, 160),
            color=(70, 90, 130),
            layer="world",
            z=0,
        )
        ctx.render_queue.circle(
            center=Vec2(400, 300),
            radius=70,
            color=(230, 140, 90),
            layer="effects",
            z=5,
        )
        ctx.render_queue.text(
            x=400,
            y=300,
            text="UI renders after world/effects",
            align="center",
            layer="ui",
            z=0,
        )


@SceneRegistry.implementation("main")
class DemoScene(Scene[DemoWorld, DemoIntent, DemoContext]):
    world_type = DemoWorld
    intent_type = DemoIntent
    tick_context_type = DemoContext

    def game_systems(self, ctx):
        return (LayerSystem(),)

    def on_enter(self, ctx):
        pass


def main() -> None:
    TatuyApp().run()


if __name__ == "__main__":
    main()
