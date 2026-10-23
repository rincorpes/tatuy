from tatuy import TatuyApp
from tatuy.ecs import World
from tatuy.features.movement import (
    DesiredMovement,
    Movement,
    MovementControls,
    Velocity,
)
from tatuy.features.spatial import Transform
from tatuy.features.visual import Rect
from tatuy.geometry.size import Size
from tatuy.input.keys import Key
from tatuy.math.vec2 import Vec2
from tatuy.scenes import Intent, Scene, SceneRegistry, SceneTickContext


class DemoWorld(World): ...


class DemoIntent(Intent):
    def update_from(self, input_frame):
        self.move_up = input_frame.is_down(Key.W)
        self.move_down = input_frame.is_down(Key.S)
        self.move_left = input_frame.is_down(Key.A)
        self.move_right = input_frame.is_down(Key.D)


class DemoContext(SceneTickContext[DemoWorld, DemoIntent]): ...


@SceneRegistry.implementation("main")
class DemoScene(Scene[DemoWorld, DemoIntent, DemoContext]):
    world_type = DemoWorld
    intent_type = DemoIntent
    tick_context_type = DemoContext

    def on_enter(self, ctx):
        entity = self.world.create_entity()
        self.world.add_component(entity, Transform(Vec2(400, 300)))
        self.world.add_component(entity, Velocity())
        self.world.add_component(entity, Movement(speed=220, acceleration=600))
        self.world.add_component(entity, DesiredMovement())
        self.world.add_component(entity, MovementControls())
        self.world.add_component(entity, Rect(Size(48, 48), (240, 150, 90)))


def main() -> None:
    # WASD -> Intent -> DesiredMovement -> Velocity -> Transform.
    TatuyApp().run()


if __name__ == "__main__":
    main()
