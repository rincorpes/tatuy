from tatuy import TatuyApp
from tatuy.ecs import World
from tatuy.features.bounds import (
    BoundsBehavior,
    BoundsConstraint,
    WorldBoundsBorder,
)
from tatuy.features.collision import BoxCollider
from tatuy.features.movement import Velocity
from tatuy.features.spatial import Transform
from tatuy.features.visual import Rect
from tatuy.geometry.bounds import Bounds, BoundsSide
from tatuy.geometry.size import Size
from tatuy.math.vec2 import Vec2
from tatuy.scenes import Intent, Scene, SceneRegistry, SceneTickContext


class DemoWorld(World): ...


class DemoIntent(Intent):
    def update_from(self, input_frame):
        pass


class DemoContext(SceneTickContext[DemoWorld, DemoIntent]): ...


def add_box(
    world, position, velocity, behavior, color, *, sides=BoundsSide.ALL
):
    entity = world.create_entity()
    world.add_component(entity, Transform(position))
    world.add_component(entity, Velocity(velocity))
    world.add_component(entity, BoxCollider(Size(36, 36)))
    world.add_component(entity, BoundsConstraint(behavior, sides=sides))
    world.add_component(entity, Rect(Size(36, 36), color))


@SceneRegistry.implementation("main")
class DemoScene(Scene[DemoWorld, DemoIntent, DemoContext]):
    world_type = DemoWorld
    intent_type = DemoIntent
    tick_context_type = DemoContext

    def bounds(self, ctx):
        return Bounds(40, 40, 760, 560)

    def bounds_border(self, ctx):
        return WorldBoundsBorder(thickness=3)

    def on_enter(self, ctx):
        add_box(
            self.world,
            Vec2(90, 140),
            Vec2(-120, 0),
            BoundsBehavior.CLAMP,
            (100, 180, 240),
        )
        add_box(
            self.world,
            Vec2(220, 260),
            Vec2(-160, 0),
            BoundsBehavior.BOUNCE,
            (240, 150, 90),
        )
        add_box(
            self.world,
            Vec2(580, 380),
            Vec2(170, 0),
            BoundsBehavior.WRAP,
            (120, 220, 150),
        )
        add_box(
            self.world,
            Vec2(680, 500),
            Vec2(180, 0),
            BoundsBehavior.DESPAWN,
            (220, 100, 150),
        )
        add_box(
            self.world,
            Vec2(400, 70),
            Vec2(0, -100),
            BoundsBehavior.CLAMP,
            (190, 170, 240),
            sides=BoundsSide.LEFT | BoundsSide.RIGHT,
        )


def main() -> None:
    TatuyApp().run()


if __name__ == "__main__":
    main()
