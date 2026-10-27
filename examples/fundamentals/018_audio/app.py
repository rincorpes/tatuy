from typing import cast

from tatuy import TatuyApp, TatuyConfigDict
from tatuy.assets import FilesystemAssetProvider
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
        ctx.audio.load_sound("demo.sound", ctx.assets.path("assets/test.wav"))
        ctx.audio.play("demo.sound")


def create_app(config: TatuyConfigDict | None = None) -> TatuyApp:
    defaults: TatuyConfigDict = {"backend": {"audio": {"enabled": True}}}
    merged = merge_config(defaults, config or {})
    assets = FilesystemAssetProvider.from_file(
        __file__,
        "../001_backend/008_audio",
    )
    return TatuyApp(cast(TatuyConfigDict, merged), assets=assets)


def main() -> None:
    create_app().run()


if __name__ == "__main__":
    main()
