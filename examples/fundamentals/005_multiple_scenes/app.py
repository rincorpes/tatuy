from __future__ import annotations

from dataclasses import dataclass
from typing import cast

from tatuy import TatuyApp, TatuyConfigDict
from tatuy.commands import ChangeScene
from tatuy.configuration import merge_config
from tatuy.ecs import (
    BaseSystem,
    EntityBlueprint,
    EntityFactory,
    SystemPhase,
    World,
)
from tatuy.geometry.size import Size
from tatuy.input.keys import Key
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


class MyGameSimSystem(BaseSystem[MyGameSceneTickContext]):
    phase = SystemPhase.SIMULATION

    def step(self, ctx):
        state = ctx.world.get_resource(MyGameStateResource)
        if ctx.intent.mouse_inside:
            if state.count_up:
                state.mouse_inside_count += 1
                state.count_up = False
        else:
            state.count_up = True


class MyGamePresentationSystem(BaseSystem[MyGameSceneTickContext]):
    phase = SystemPhase.PRESENTATION

    def step(self, ctx):
        state = ctx.world.get_resource(MyGameStateResource)
        kwargs = {
            "position": Vec2(
                100,
                100,
            ),
            "text": (
                f"The mouse has been inside the canvas {state.mouse_inside_count} times and "
                f"There are {len(ctx.world.entities)} entities"
            ),
            "font_size": 25,
        }
        ctx.canvas.text(**kwargs)

        for _, my_comp in ctx.world.query(MyGameComponent):
            ctx.canvas.rect(
                position=my_comp.pos, size=Size(10, 10), color=(200, 200, 200)
            )


@SceneRegistry.implementation("main")
class MyGameScene(Scene[MyGameWorld, MyGameIntent, MyGameSceneTickContext]):

    world_type = MyGameWorld
    intent_type = MyGameIntent
    tick_context_type = MyGameSceneTickContext
    factory_type = MyGameEntityFactory

    def on_enter(self, ctx):
        self.world.add_resource(MyGameStateResource())
        window_size = (ctx.viewport.window_w, ctx.viewport.window_h)
        self.factory.create("entity", window_size=window_size)
        self.systems = (MyGameSimSystem(), MyGamePresentationSystem())


class InitialWorld(World): ...


class InitialIntent(Intent):
    enter_pressed: bool = False

    def update_from(self, input_frame):
        self.enter_pressed = input_frame.is_pressed(Key.ENTER)


class InitialSceneTickContext(
    SceneTickContext[InitialWorld, InitialIntent]
): ...


class InitializeSystem(BaseSystem[InitialSceneTickContext]):
    def step(self, ctx):
        if ctx.intent.enter_pressed:
            ctx.scene_context.commands.push(ChangeScene("main"))


class RenderInitializeSystem(BaseSystem[InitialSceneTickContext]):
    phase = SystemPhase.PRESENTATION

    def step(self, ctx):
        kwargs = {
            "position": Vec2(
                100,
                100,
            ),
            "text": "Pres ENTER to start",
            "font_size": 25,
        }
        ctx.canvas.text(**kwargs)


@SceneRegistry.implementation("initial")
class InitialScene(
    Scene[InitialWorld, InitialIntent, InitialSceneTickContext]
):
    world_type = InitialWorld
    intent_type = InitialIntent
    tick_context_type = InitialSceneTickContext

    def on_enter(self, ctx):
        self.systems = (
            InitializeSystem(),
            RenderInitializeSystem(),
        )


def create_app(config: TatuyConfigDict | None = None) -> TatuyApp:
    defaults: TatuyConfigDict = {"engine": {"start_scene": "initial"}}
    merged = merge_config(defaults, config or {})
    return TatuyApp(cast(TatuyConfigDict, merged))


def main() -> None:
    create_app().run()


if __name__ == "__main__":
    main()
