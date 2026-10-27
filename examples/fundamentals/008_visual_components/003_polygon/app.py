from tatuy import TatuyApp, TatuyConfigDict
from tatuy.ecs import World
from tatuy.features.spatial import Transform
from tatuy.features.visual import Polygon
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
        self.world.add_component(
            entity,
            Polygon(
                (Vec2(-70, 50), Vec2(0, -70), Vec2(70, 50)),
                (120, 220, 150),
            ),
        )


def create_app(config: TatuyConfigDict | None = None) -> TatuyApp:
    return TatuyApp(config)


def main() -> None:
    create_app().run()


if __name__ == "__main__":
    main()
