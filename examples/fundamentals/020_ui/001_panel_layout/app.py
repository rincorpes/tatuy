from tatuy import TatuyApp, TatuyConfigDict
from tatuy.ecs import World
from tatuy.geometry.size import Size
from tatuy.math.vec2 import Vec2
from tatuy.scenes import Intent, Scene, SceneRegistry, SceneTickContext
from tatuy.ui import Panel, UIFrame, UiLayoutSystem, UiNode


class DemoWorld(World): ...


class DemoIntent(Intent):
    def update_from(self, input_frame):
        pass


class DemoContext(SceneTickContext[DemoWorld, DemoIntent]): ...


@SceneRegistry.implementation("main")
class DemoScene(Scene[DemoWorld, DemoIntent, DemoContext]):
    world_type = DemoWorld
    intent_type = DemoIntent
    tick_context_type = DemoContext

    def resources(self, ctx):
        return (UIFrame(),)

    def game_systems(self, ctx):
        return (UiLayoutSystem(),)

    def on_enter(self, ctx):
        container = self.world.create_entity()
        self.world.add_component(
            container,
            UiNode(Size(320, 220), anchor=(0.5, 0.5)),
        )
        self.world.add_component(container, Panel((70, 90, 130)))

        child = self.world.create_entity()
        self.world.add_component(
            child,
            UiNode(
                Size(120, 60),
                parent=container,
                anchor=(1.0, 1.0),
                offset=Vec2(-80, -50),
                z=1,
            ),
        )
        self.world.add_component(child, Panel((120, 180, 240)))


def create_app(config: TatuyConfigDict | None = None) -> TatuyApp:
    return TatuyApp(config)


def main() -> None:
    create_app().run()


if __name__ == "__main__":
    main()
