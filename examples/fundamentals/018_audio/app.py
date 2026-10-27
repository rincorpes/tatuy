from pathlib import Path
from typing import cast

from tatuy import TatuyApp, TatuyConfigDict
from tatuy.configuration import merge_config
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


def create_app(config: TatuyConfigDict | None = None) -> TatuyApp:
    sound = (
        Path(__file__).resolve().parent.parent
        / "001_backend"
        / "008_audio"
        / "assets"
        / "test.wav"
    )
    defaults: TatuyConfigDict = {
        "backend": {
            "audio": {
                "enabled": True,
                "sounds": [{"name": "demo.sound", "path": str(sound)}],
            }
        }
    }
    merged = merge_config(defaults, config or {})
    return TatuyApp(cast(TatuyConfigDict, merged))


def main() -> None:
    create_app().run()


if __name__ == "__main__":
    main()
