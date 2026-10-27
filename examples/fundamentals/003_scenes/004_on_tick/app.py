from __future__ import annotations

from dataclasses import dataclass

from tatuy import TatuyApp, TatuyConfigDict
from tatuy.ecs.world import World
from tatuy.scenes.context import Intent, SceneTickContext
from tatuy.scenes.registry import SceneRegistry
from tatuy.scenes.scene import Scene


class MyGameWorld(World): ...


@dataclass
class MyGameIntent(Intent):
    mouse_inside: bool = False

    def update_from(self, input_frame):
        pass


class MyGameSceneTickContext(SceneTickContext[MyGameWorld, MyGameIntent]): ...


@SceneRegistry.implementation("main")
class MyGameScene(Scene[MyGameWorld, MyGameIntent, MyGameSceneTickContext]):

    world_type = MyGameWorld
    intent_type = MyGameIntent
    tick_context_type = MyGameSceneTickContext

    def on_enter(self, ctx):
        print("Main scene started")

    def on_tick(self, ctx):
        print("Ticking")


def create_app(config: TatuyConfigDict | None = None) -> TatuyApp:
    return TatuyApp(config)


def main() -> None:
    create_app().run()


if __name__ == "__main__":
    main()
