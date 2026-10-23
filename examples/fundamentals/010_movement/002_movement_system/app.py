from tatuy import TatuyApp
from tatuy.ecs import World
from tatuy.features.movement import DesiredMovement, Movement, Velocity
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
        self.world.add_component(entity, Transform(Vec2(120, 300)))
        self.world.add_component(entity, Velocity())
        self.world.add_component(entity, Movement(speed=150, acceleration=300))
        self.world.add_component(entity, DesiredMovement(Vec2(1, 0)))
        self.world.add_component(entity, Rect(Size(48, 48), (120, 220, 150)))


def main() -> None:
    # Movement calculates Velocity; velocity integration moves Transform.
    TatuyApp().run()


if __name__ == "__main__":
    main()
