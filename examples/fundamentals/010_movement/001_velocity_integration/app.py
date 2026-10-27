from tatuy import TatuyApp, TatuyConfigDict
from tatuy.ecs import World
from tatuy.features.movement import Velocity
from tatuy.features.spatial import Transform
from tatuy.features.visual import Circle
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
        self.world.add_component(entity, Transform(Vec2(120, 300)))
        self.world.add_component(entity, Velocity(Vec2(120, 0)))
        self.world.add_component(entity, Circle(24, (90, 170, 240)))


def create_app(config: TatuyConfigDict | None = None) -> TatuyApp:
    """Create the reusable movement fundamental application."""
    return TatuyApp(config)


def main() -> None:
    # Velocity + Transform automatically activate velocity integration.
    create_app().run()


if __name__ == "__main__":
    main()
