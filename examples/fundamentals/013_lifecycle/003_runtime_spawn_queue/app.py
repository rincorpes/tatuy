from tatuy import TatuyApp, TatuyConfigDict
from tatuy.ecs import EntityBlueprint, EntityFactory, GameSystem, World
from tatuy.features.lifecycle import LifecycleQueue, SpawnDefinition
from tatuy.features.spatial import Transform
from tatuy.features.visual import Circle
from tatuy.math.vec2 import Vec2
from tatuy.scenes import Intent, Scene, SceneRegistry, SceneTickContext


class DemoWorld(World): ...


class DemoIntent(Intent):
    def update_from(self, input_frame):
        pass


class DemoContext(SceneTickContext[DemoWorld, DemoIntent]): ...


class DotBlueprint(EntityBlueprint[DemoWorld]):
    def build(self, world, entity, **kwargs):
        world.add_component(entity, Transform(kwargs["position"]))
        world.add_component(entity, Circle(22, (120, 220, 150)))


class DemoFactory(EntityFactory):
    registry = {"dot": DotBlueprint}


class RuntimeSpawner(GameSystem[DemoContext]):
    def __init__(self) -> None:
        self.elapsed = 0.0
        self.spawned = False

    def on_simulation(self, ctx: DemoContext) -> None:
        self.elapsed += ctx.dt
        if self.spawned or self.elapsed < 1.0:
            return
        ctx.world.get_resource(LifecycleQueue).request_spawn(
            "runtime_dot",
            kwargs={"position": Vec2(400, 300)},
        )
        self.spawned = True


@SceneRegistry.implementation("main")
class DemoScene(Scene[DemoWorld, DemoIntent, DemoContext]):
    world_type = DemoWorld
    intent_type = DemoIntent
    tick_context_type = DemoContext
    factory_type = DemoFactory

    def spawn_definitions(self, ctx):
        return {"runtime_dot": SpawnDefinition(blueprint="dot")}

    def game_systems(self, ctx):
        return (RuntimeSpawner(),)

    def on_enter(self, ctx):
        pass


def create_app(config: TatuyConfigDict | None = None) -> TatuyApp:
    """Create the reusable runtime-spawn example application."""
    return TatuyApp(config)


def main() -> None:
    # LifecycleQueue lets gameplay request definition-based spawns at runtime.
    create_app().run()


if __name__ == "__main__":
    main()
