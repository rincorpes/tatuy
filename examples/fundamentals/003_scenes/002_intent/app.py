from __future__ import annotations

from typing import Any

from tatuy.app import TatuyApp
from tatuy.ecs.world import World
from tatuy.scenes.context import Intent
from tatuy.scenes.registry import SceneRegistry
from tatuy.scenes.scene import Scene


class MyGameWorld(World): ...


class MyGameIntent(Intent):
    def update_from(self, input_frame):
        print("Building intent")


@SceneRegistry.implementation("main")
class MyGameScene(Scene[MyGameWorld, MyGameIntent, Any]):

    world_type = MyGameWorld
    intent_type = MyGameIntent

    def on_enter(self, ctx):
        print("Main scene started")


def main():
    my_game = TatuyApp()
    my_game.run()


if __name__ == "__main__":
    main()
