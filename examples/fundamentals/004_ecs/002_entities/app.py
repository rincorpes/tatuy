from __future__ import annotations

from dataclasses import dataclass

from tatuy import TatuyApp
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
        self.world.create_entity()
        self.world.create_entity()

    def on_tick(self, ctx):
        state = self.world.get_resource(MyGameStateResource)
        entities = self.world.entities
        if ctx.intent.mouse_inside:
            if state.count_up:
                state.mouse_inside_count += 1
                state.count_up = False
                if entities:
                    for entity in tuple(entities):
                        self.world.destroy_entity(entity)
        else:
            state.count_up = True
            if len(entities) < state.mouse_inside_count:
                self.world.create_entity()

    def on_present(self, ctx):
        state = self.world.get_resource(MyGameStateResource)
        entities = len(self.world.entities)
        kwargs = {
            "position": Vec2(
                100,
                ctx.scene_context.viewport.window_h / 2 - 20,
            ),
            "text": (
                f"The mouse has been inside the canvas {state.mouse_inside_count} times and "
                f"there are {entities} entities"
            ),
            "font_size": 25,
        }
        ctx.canvas.text(**kwargs)


def main():
    my_game = TatuyApp()
    my_game.run()


if __name__ == "__main__":
    main()
