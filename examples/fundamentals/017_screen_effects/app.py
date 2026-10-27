from tatuy import TatuyApp, TatuyConfigDict
from tatuy.ecs import World
from tatuy.features.spatial import Transform
from tatuy.features.visual import Rect
from tatuy.geometry.size import Size
from tatuy.math.vec2 import Vec2
from tatuy.scenes import Intent, Scene, SceneRegistry, SceneTickContext


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

    def on_enter(self, ctx):
        entity = self.world.create_entity()
        self.world.add_component(entity, Transform(Vec2(400, 300)))
        self.world.add_component(entity, Rect(Size(240, 140), (70, 100, 150)))
        self.screen_fx.flash(
            duration=1.5,
            color=(255, 255, 255),
            peak_alpha=220,
        )


def create_app(config: TatuyConfigDict | None = None) -> TatuyApp:
    return TatuyApp(config)


def main() -> None:
    # ScreenEffectStack is scene-owned and rendered by the presentation pipeline.
    create_app().run()


if __name__ == "__main__":
    main()
