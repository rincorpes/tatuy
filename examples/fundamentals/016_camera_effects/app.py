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
        for x in (250, 400, 550):
            entity = self.world.create_entity()
            self.world.add_component(entity, Transform(Vec2(x, 300)))
            self.world.add_component(
                entity, Rect(Size(80, 80), (100, 180, 240))
            )

        self.camera_fx.shake(duration=2.0, strength=18.0)


def create_app(config: TatuyConfigDict | None = None) -> TatuyApp:
    return TatuyApp(config)


def main() -> None:
    # CameraFX is scene-owned and automatically updated/presented by the engine.
    create_app().run()


if __name__ == "__main__":
    main()
