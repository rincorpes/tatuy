from tatuy import TatuyApp
from tatuy.ecs import EntityBlueprint, EntityFactory, World
from tatuy.features.lifecycle import SpawnDefinition
from tatuy.features.spatial import Transform
from tatuy.features.visual import Circle
from tatuy.math.vec2 import Vec2
from tatuy.scenes import (
    EntitySpawn,
    Intent,
    Scene,
    SceneRegistry,
    SceneTickContext,
)


class DemoWorld(World): ...


class DemoIntent(Intent):
    def update_from(self, input_frame):
        pass


class DemoContext(SceneTickContext[DemoWorld, DemoIntent]): ...


class DotBlueprint(EntityBlueprint[DemoWorld]):
    def build(self, world, entity, **kwargs):
        world.add_component(
            entity, Transform(kwargs.get("position", Vec2(400, 300)))
        )
        world.add_component(entity, Circle(28, (100, 180, 240)))


class DemoFactory(EntityFactory):
    registry = {"dot": DotBlueprint}


@SceneRegistry.implementation("main")
class DemoScene(Scene[DemoWorld, DemoIntent, DemoContext]):
    world_type = DemoWorld
    intent_type = DemoIntent
    tick_context_type = DemoContext
    factory_type = DemoFactory

    def spawn_definitions(self, ctx):
        return {
            "temporary_dot": SpawnDefinition(blueprint="dot", lifetime=2.0)
        }

    def entities(self, ctx):
        return (EntitySpawn("temporary_dot"),)

    def on_enter(self, ctx):
        pass


def main() -> None:
    # The entity is spawned during scene setup and despawns after two seconds.
    TatuyApp().run()


if __name__ == "__main__":
    main()
