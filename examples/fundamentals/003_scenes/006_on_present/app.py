from __future__ import annotations

from tatuy.app import TatuyApp
from tatuy.ecs.world import World
from tatuy.math.vec2 import Vec2
from tatuy.scenes.context import Intent, SceneTickContext
from tatuy.scenes.registry import SceneRegistry
from tatuy.scenes.scene import Scene


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
        print("Main scene started")

    def on_tick(self, ctx):
        print(ctx.intent.mouse_inside)

    def on_present(self, ctx):
        status = "Outside"
        if ctx.intent.mouse_inside:
            status = "Inside"
        kwargs = {
            "position": Vec2(
                100,
                ctx.scene_context.viewport.window_h / 2 - 20,
            ),
            "text": f"Mouse is {status} Canvas",
            "font_size": 40,
        }
        ctx.canvas.text(**kwargs)


def main():
    my_game = TatuyApp()
    my_game.run()


if __name__ == "__main__":
    main()
