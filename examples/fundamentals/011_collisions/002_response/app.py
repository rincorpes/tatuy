from tatuy import TatuyApp
from tatuy.ecs import World
from tatuy.features.collision import BoxCollider, CollisionBody, CollisionFrame
from tatuy.features.movement import Velocity
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

    def resources(self, ctx):
        return (CollisionFrame(),)

    def on_enter(self, ctx):
        moving = self.world.create_entity()
        self.world.add_component(moving, Transform(Vec2(180, 300)))
        self.world.add_component(moving, Velocity(Vec2(180, 0)))
        self.world.add_component(moving, BoxCollider(Size(60, 60)))
        self.world.add_component(moving, CollisionBody(restitution=1.0))
        self.world.add_component(moving, Rect(Size(60, 60), (100, 180, 240)))

        wall = self.world.create_entity()
        self.world.add_component(wall, Transform(Vec2(520, 300)))
        self.world.add_component(wall, BoxCollider(Size(80, 220)))
        self.world.add_component(wall, CollisionBody(inverse_mass=0.0))
        self.world.add_component(wall, Rect(Size(80, 220), (220, 220, 220)))


def main() -> None:
    TatuyApp().run()


if __name__ == "__main__":
    main()
