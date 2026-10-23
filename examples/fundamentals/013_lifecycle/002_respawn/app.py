from tatuy import TatuyApp
from tatuy.ecs import EntityBlueprint, EntityFactory, World
from tatuy.features.lifecycle import DespawnReason, Respawn, SpawnDefinition
from tatuy.features.spatial import Transform
from tatuy.features.visual import Rect
from tatuy.geometry.size import Size
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


class BoxBlueprint(EntityBlueprint[DemoWorld]):
    def build(self, world, entity, **kwargs):
        world.add_component(entity, Transform(Vec2(400, 300)))
        world.add_component(entity, Rect(Size(64, 64), (240, 150, 90)))


class DemoFactory(EntityFactory):
    registry = {"box": BoxBlueprint}


@SceneRegistry.implementation("main")
class DemoScene(Scene[DemoWorld, DemoIntent, DemoContext]):
    world_type = DemoWorld
    intent_type = DemoIntent
    tick_context_type = DemoContext
    factory_type = DemoFactory

    def spawn_definitions(self, ctx):
        return {
            "respawning_box": SpawnDefinition(
                blueprint="box",
                lifetime=1.5,
                respawn=Respawn(
                    delay=1.0,
                    reasons=frozenset({DespawnReason.LIFETIME_EXPIRED}),
                ),
            )
        }

    def entities(self, ctx):
        return (EntitySpawn("respawning_box"),)

    def on_enter(self, ctx):
        pass


def main() -> None:
    # LIFETIME_EXPIRED entities wait one second, then respawn from the same definition.
    TatuyApp().run()


if __name__ == "__main__":
    main()
