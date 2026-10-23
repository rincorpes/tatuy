from tatuy import TatuyApp
from tatuy.commands import SetWindowTitle
from tatuy.ecs import World
from tatuy.features.visual import Text
from tatuy.geometry.size import Size
from tatuy.scenes import Scene, SceneRegistry, SceneTickContext
from tatuy.ui import (
    Button,
    ButtonAppearance,
    ButtonState,
    Panel,
    PanelShape,
    UIFrame,
    UiIntent,
    UIInteraction,
    UiLayoutSystem,
    UiNode,
    UiPointerSystem,
)


class DemoWorld(World): ...


class DemoIntent(UiIntent): ...


class DemoContext(SceneTickContext[DemoWorld, DemoIntent]): ...


@SceneRegistry.implementation("main")
class DemoScene(Scene[DemoWorld, DemoIntent, DemoContext]):
    world_type = DemoWorld
    intent_type = DemoIntent
    tick_context_type = DemoContext

    def resources(self, ctx):
        return (UIFrame(), UIInteraction())

    def game_systems(self, ctx):
        return (UiLayoutSystem(), UiPointerSystem())

    def on_enter(self, ctx):
        button = self.world.create_entity()
        self.world.add_component(button, UiNode(Size(180, 64), z=1))
        self.world.add_component(
            button,
            Panel((70, 100, 150), shape=PanelShape.PILL),
        )
        self.world.add_component(
            button,
            Text(
                (255, 255, 255),
                content="Click me",
                font_size=24,
                align="center",
                valign="middle",
            ),
        )
        self.world.add_component(
            button,
            Button(
                commands=(SetWindowTitle("Tatuy button clicked"),),
                hover=ButtonAppearance(background=(100, 150, 220)),
                pressed=ButtonAppearance(background=(50, 80, 120)),
            ),
        )
        self.world.add_component(button, ButtonState())


def main() -> None:
    # UiIntent carries pointer state; UiPointerSystem drives ButtonState and commands.
    TatuyApp().run()


if __name__ == "__main__":
    main()
