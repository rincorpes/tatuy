from tatuy import TatuyApp, TatuyConfigDict
from tatuy.ecs import World
from tatuy.engine import SystemRegistration
from tatuy.features.collision import (
    BoxCollider,
    CollisionBody,
    CollisionFrame,
    CollisionResponseSystem,
    CollisionVelocities,
    CollisionVelocityRule,
)
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


class HorizontalBounceRule(CollisionVelocityRule):
    def resolve(self, world, contact):
        a = world.get_component(contact.entity_a, Velocity)
        b = world.get_component(contact.entity_b, Velocity)
        return CollisionVelocities(
            Vec2(-a.value.x, a.value.y),
            Vec2(-b.value.x, b.value.y),
        )


@SceneRegistry.implementation("main")
class DemoScene(Scene[DemoWorld, DemoIntent, DemoContext]):
    world_type = DemoWorld
    intent_type = DemoIntent
    tick_context_type = DemoContext

    def resources(self, ctx):
        return (CollisionFrame(),)

    def builtin_overrides(self, ctx):
        return {
            "collision_response": SystemRegistration(
                CollisionResponseSystem(
                    velocity_rules=(HorizontalBounceRule(),)
                ),
                order=500,
                active=lambda tick: bool(
                    tick.world.get_resource(CollisionFrame).contacts
                ),
            )
        }

    def on_enter(self, ctx):
        for position, velocity, color in (
            (Vec2(220, 300), Vec2(120, 0), (100, 180, 240)),
            (Vec2(580, 300), Vec2(-120, 0), (240, 150, 90)),
        ):
            entity = self.world.create_entity()
            self.world.add_component(entity, Transform(position))
            self.world.add_component(entity, Velocity(velocity))
            self.world.add_component(entity, BoxCollider(Size(60, 60)))
            self.world.add_component(entity, CollisionBody())
            self.world.add_component(entity, Rect(Size(60, 60), color))


def create_app(config: TatuyConfigDict | None = None) -> TatuyApp:
    """Create the reusable custom-collision-response example application."""
    return TatuyApp(config)


def main() -> None:
    create_app().run()


if __name__ == "__main__":
    main()
