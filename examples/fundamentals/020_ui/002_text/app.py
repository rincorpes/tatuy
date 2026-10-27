from tatuy import TatuyApp, TatuyConfigDict
from tatuy.ecs import World
from tatuy.features.visual import Text
from tatuy.geometry.size import Size
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
        label = self.world.create_entity()
        self.world.add_component(label, UiNode(Size(360, 80), z=1))
        self.world.add_component(label, Panel((50, 65, 95)))
        self.world.add_component(
            label,
            Text(
                (240, 240, 240),
                content="UI text is positioned by UiNode",
                font_size=26,
                align="center",
                valign="middle",
            ),
        )


def create_app(config: TatuyConfigDict | None = None) -> TatuyApp:
    return TatuyApp(config)


def main() -> None:
    create_app().run()


if __name__ == "__main__":
    main()
