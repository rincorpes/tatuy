from __future__ import annotations

from dataclasses import dataclass

from tatuy import TatuyApp, TatuyConfigDict
from tatuy.ecs import EntityBlueprint, EntityFactory, World
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


@dataclass
class MyGameComponent:
    pos: Vec2


class MyGameEntityBlueprint(EntityBlueprint[MyGameWorld]):
    def create(self, world, **kwargs):
        entity = world.create_entity()
        w, h = kwargs.get("window_size")
        world.add_component(
            entity, MyGameComponent(Vec2(w / 2 - 25, h / 2 - 25))
        )


class MyGameEntityFactory(EntityFactory):
    registry = {"entity": MyGameEntityBlueprint}


@SceneRegistry.implementation("main")
class MyGameScene(Scene[MyGameWorld, MyGameIntent, MyGameSceneTickContext]):

    world_type = MyGameWorld
    intent_type = MyGameIntent
    tick_context_type = MyGameSceneTickContext
    factory_type = MyGameEntityFactory

    def on_enter(self, ctx):
        self.world.add_resource(MyGameStateResource())
        window_size = (ctx.viewport.virtual_w, ctx.viewport.virtual_h)
        self.factory.create("entity", window_size=window_size)

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
                100,
            ),
            "text": (
                f"The mouse has been inside the canvas {state.mouse_inside_count} times and "
                f"There is {len(self.world.entities)} entity"
            ),
            "font_size": 25,
        }
        ctx.canvas.text(**kwargs)


def create_app(config: TatuyConfigDict | None = None) -> TatuyApp:
    return TatuyApp(config)


def main() -> None:
    create_app().run()


if __name__ == "__main__":
    main()
