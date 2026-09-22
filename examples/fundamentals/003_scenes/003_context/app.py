from __future__ import annotations

from dataclasses import dataclass

from tatuy.app import TatuyApp
from tatuy.ecs.world import World
from tatuy.scenes.context import Intent, SceneTickContext
from tatuy.scenes.registry import SceneRegistry
from tatuy.scenes.scene import Scene


class MyGameWorld(World): ...


@dataclass
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


def main():
    my_game = TatuyApp()
    my_game.run()


if __name__ == "__main__":
    main()
