from __future__ import annotations

from dataclasses import dataclass

from tatuy import TatuyApp, TatuyConfigDict
from tatuy.ecs import World
from tatuy.math.vec2 import Vec2
from tatuy.scenes import Intent, Scene, SceneRegistry, SceneTickContext


@dataclass
class MyGameStateResource:
    mouse_inside_count: int = 0
    count_up: bool = True


class MyGameWorld(World): ...


class MyGameIntent(Intent):
    mouse_inside: bool = False

    def update_from(self, input_frame):
        self.mouse_inside = input_frame.mouse_inside


class MyGameSceneTickContext(SceneTickContext[MyGameWorld, MyGameIntent]): ...


@SceneRegistry.implementation("main")
class MyGameScene(Scene[MyGameWorld, MyGameIntent, MyGameSceneTickContext]):

    world_type = MyGameWorld
    intent_type = MyGameIntent
    tick_context_type = MyGameSceneTickContext

    def on_enter(self, ctx):
        self.world.add_resource(MyGameStateResource())

    def on_tick(self, ctx):
        state = self.world.get_resource(MyGameStateResource)
        if ctx.intent.mouse_inside:
            if state.count_up:
                state.mouse_inside_count += 1
                state.count_up = False
        else:
            state.count_up = True

    def on_present(self, ctx):
        state = self.world.get_resource(MyGameStateResource)
        kwargs = {
            "position": Vec2(
                100,
                ctx.scene_context.viewport.virtual_h / 2 - 20,
            ),
            "text": f"The mouse has been inside the canvas {state.mouse_inside_count} times",
            "font_size": 40,
        }
        ctx.canvas.text(**kwargs)


def create_app(config: TatuyConfigDict | None = None) -> TatuyApp:
    return TatuyApp(config)


def main() -> None:
    create_app().run()


if __name__ == "__main__":
    main()
