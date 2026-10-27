from random import Random

from tatuy import TatuyApp, TatuyConfigDict
from tatuy.ecs import World
from tatuy.features.fx import (
    ParticleBurst,
    ParticleEmitter,
    ParticleUpdateSystem,
)
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
        return (ParticleUpdateSystem(),)

    def on_enter(self, ctx):
        ParticleEmitter(self.world, rng=Random(7), max_particles=100).emit(
            Vec2(400, 300),
            (100, 180, 240),
            ParticleBurst(
                count=40,
                speed_min=80,
                speed_max=220,
                lifetime_min=1.0,
                lifetime_max=2.0,
                radius_min=3,
                radius_max=7,
            ),
        )


def create_app(config: TatuyConfigDict | None = None) -> TatuyApp:
    return TatuyApp(config)


def main() -> None:
    create_app().run()


if __name__ == "__main__":
    main()
