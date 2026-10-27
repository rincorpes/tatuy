from tatuy import TatuyApp, TatuyConfigDict
from tatuy.ecs import GameSystem, World
from tatuy.features.collision import BoxCollider, CollisionFrame
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


class CollisionFeedback(GameSystem[DemoContext]):
    def on_post_simulation(self, ctx: DemoContext) -> None:
        colliding = {
            entity
            for contact in ctx.world.get_resource(CollisionFrame).contacts
            for entity in (contact.entity_a, contact.entity_b)
        }
        for entity, rect in ctx.world.query(Rect):
            rect.color = (
                (240, 120, 100) if entity in colliding else (100, 180, 240)
            )


@SceneRegistry.implementation("main")
class DemoScene(Scene[DemoWorld, DemoIntent, DemoContext]):
    world_type = DemoWorld
    intent_type = DemoIntent
    tick_context_type = DemoContext

    def resources(self, ctx):
        return (CollisionFrame(),)

    def game_systems(self, ctx):
        return (CollisionFeedback(),)

    def on_enter(self, ctx):
        for position in (Vec2(360, 300), Vec2(430, 300)):
            entity = self.world.create_entity()
            self.world.add_component(entity, Transform(position))
            self.world.add_component(entity, BoxCollider(Size(100, 100)))
            self.world.add_component(
                entity, Rect(Size(100, 100), (100, 180, 240))
            )


def create_app(config: TatuyConfigDict | None = None) -> TatuyApp:
    """Create the reusable collision-detection example application."""
    return TatuyApp(config)


def main() -> None:
    create_app().run()


if __name__ == "__main__":
    main()
