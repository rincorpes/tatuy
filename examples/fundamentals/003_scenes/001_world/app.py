from __future__ import annotations

from typing import Any

from tatuy import TatuyApp, TatuyConfigDict
from tatuy.ecs.world import World
from tatuy.input.frame import InputFrame
from tatuy.scenes.context import Intent
from tatuy.scenes.registry import SceneRegistry
from tatuy.scenes.scene import Scene


class MyGameWorld(World): ...


class EmptyIntent(Intent):
    def update_from(self, input_frame: InputFrame) -> None:
        pass


@SceneRegistry.implementation("main")
class MyGameScene(Scene[MyGameWorld, EmptyIntent, Any]):

    world_type = MyGameWorld
    intent_type = EmptyIntent

    def on_enter(self, ctx):
        print("Main scene started")


def create_app(config: TatuyConfigDict | None = None) -> TatuyApp:
    return TatuyApp(config)


def main() -> None:
    create_app().run()


if __name__ == "__main__":
    main()
