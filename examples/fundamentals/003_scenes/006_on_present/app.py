from __future__ import annotations

from tatuy import TatuyApp, TatuyConfigDict
from tatuy.ecs.world import World
from tatuy.math.vec2 import Vec2
from tatuy.scenes.context import Intent, SceneTickContext
from tatuy.scenes.registry import SceneRegistry
from tatuy.scenes.scene import Scene


class MyGameWorld(World): ...


class MyGameIntent(Intent):
    mouse_inside: bool = False
    focused: bool = True

    def update_from(self, input_frame):
        self.mouse_inside = input_frame.mouse_inside
        self.focused = input_frame.focused


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
        focus_status = "Focused" if ctx.intent.focused else "Unfocused"
        kwargs = {
            "position": Vec2(
                100,
                ctx.scene_context.viewport.virtual_h / 2 - 20,
            ),
            "text": f"Mouse is {status} Canvas | {focus_status}",
            "font_size": 40,
        }
        ctx.canvas.text(**kwargs)


def create_app(config: TatuyConfigDict | None = None) -> TatuyApp:
    return TatuyApp(config)


def main() -> None:
    create_app().run()


if __name__ == "__main__":
    main()
