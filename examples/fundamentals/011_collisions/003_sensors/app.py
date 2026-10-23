from tatuy import TatuyApp
from tatuy.ecs import GameSystem, World
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


class SensorFeedback(GameSystem[DemoContext]):
    def on_post_simulation(self, ctx: DemoContext) -> None:
        frame = ctx.world.get_resource(CollisionFrame)
        for _, rect in ctx.world.query(Rect):
            rect.color = (120, 220, 150)
        if frame.contacts:
            for _, rect in ctx.world.query(Rect):
                rect.color = (240, 170, 80)


@SceneRegistry.implementation("main")
class DemoScene(Scene[DemoWorld, DemoIntent, DemoContext]):
    world_type = DemoWorld
    intent_type = DemoIntent
    tick_context_type = DemoContext

    def resources(self, ctx):
        return (CollisionFrame(),)

    def game_systems(self, ctx):
        return (SensorFeedback(),)

    def on_enter(self, ctx):
        sensor = self.world.create_entity()
        self.world.add_component(sensor, Transform(Vec2(120, 300)))
        self.world.add_component(sensor, Velocity(Vec2(140, 0)))
        self.world.add_component(
            sensor, BoxCollider(Size(60, 60), is_sensor=True)
        )
        self.world.add_component(sensor, CollisionBody())
        self.world.add_component(sensor, Rect(Size(60, 60), (120, 220, 150)))

        target = self.world.create_entity()
        self.world.add_component(target, Transform(Vec2(420, 300)))
        self.world.add_component(target, BoxCollider(Size(100, 180)))
        self.world.add_component(target, CollisionBody(inverse_mass=0.0))
        self.world.add_component(target, Rect(Size(100, 180), (120, 220, 150)))


def main() -> None:
    # Sensor contacts are detected but do not apply physical response.
    TatuyApp().run()


if __name__ == "__main__":
    main()
