from pathlib import Path

from tatuy import TatuyApp
from tatuy.ecs import World
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

    def on_enter(self, ctx):
        ctx.audio.play("demo.sound")


def main() -> None:
    sound = (
        Path(__file__).resolve().parent.parent
        / "001_backend"
        / "008_audio"
        / "assets"
        / "test.wav"
    )
    TatuyApp(
        {
            "backend": {
                "audio": {
                    "enabled": True,
                    "sounds": [{"name": "demo.sound", "path": str(sound)}],
                }
            }
        }
    ).run()


if __name__ == "__main__":
    main()
