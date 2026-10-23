from tatuy import TatuyApp
from tatuy.ecs import World
from tatuy.features.fx import Trail, TrailRenderSystem, TrailSystem
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

    def game_systems(self, ctx):
        return (TrailSystem(), TrailRenderSystem())

    def on_enter(self, ctx):
        entity = self.world.create_entity()
        self.world.add_component(entity, Transform(Vec2(120, 300)))
        self.world.add_component(entity, Velocity(Vec2(150, 0)))
        self.world.add_component(entity, Circle(12, (240, 240, 240)))
        self.world.add_component(
            entity,
            Trail(
                duration=0.8,
                interval=1 / 45,
                radius=10,
                color=(100, 180, 240),
                max_points=48,
            ),
        )


def main() -> None:
    TatuyApp().run()


if __name__ == "__main__":
    main()
