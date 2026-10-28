from pathlib import Path
from typing import cast

from tatuy import TatuyApp, TatuyConfigDict
from tatuy.assets import FilesystemAssetProvider
from tatuy.configuration import merge_config
from tatuy.ecs import World
from tatuy.input.keys import Key
from tatuy.math.vec2 import Vec2
from tatuy.scenes import Intent, Scene, SceneRegistry, SceneTickContext


class DemoWorld(World): ...


class DemoIntent(Intent):
    play_pressed: bool = False
    mute_pressed: bool = False

    def update_from(self, input_frame):
        self.play_pressed = input_frame.is_pressed(Key.SPACE)
        self.mute_pressed = input_frame.is_pressed(Key.M)


class DemoContext(SceneTickContext[DemoWorld, DemoIntent]): ...


@SceneRegistry.implementation("main")
class DemoScene(Scene[DemoWorld, DemoIntent, DemoContext]):
    world_type = DemoWorld
    intent_type = DemoIntent
    tick_context_type = DemoContext

    def on_enter(self, ctx):
        ctx.audio.load_sound("demo.sound", ctx.assets.path("assets/test.wav"))

    def on_tick(self, ctx):
        audio = ctx.scene_context.audio
        if ctx.intent.mute_pressed:
            audio.toggle_muted()
        if ctx.intent.play_pressed:
            audio.play("demo.sound")

    def on_present(self, ctx):
        audio = ctx.scene_context.audio
        status = "Ready" if audio.ready else "Locked - press SPACE or click first"
        if audio.last_error:
            status = f"Audio error: {audio.last_error}"
        elif audio.muted:
            status = "Muted"
        ctx.canvas.text(
            position=Vec2(80, 240),
            text="SPACE: play sound    M: mute/unmute",
            font_size=28,
        )
        ctx.canvas.text(
            position=Vec2(80, 290),
            text=f"Audio: {status}",
            font_size=24,
        )


def _asset_provider() -> FilesystemAssetProvider:
    target_root = Path(__file__).resolve().parent
    if (target_root / "assets").is_dir():
        return FilesystemAssetProvider(target_root)
    return FilesystemAssetProvider.from_file(
        __file__,
        "../001_backend/008_audio",
    )


def create_app(config: TatuyConfigDict | None = None) -> TatuyApp:
    defaults: TatuyConfigDict = {"backend": {"audio": {"enabled": True}}}
    merged = merge_config(defaults, config or {})
    return TatuyApp(
        cast(TatuyConfigDict, merged),
        assets=_asset_provider(),
    )


def main() -> None:
    create_app().run()


if __name__ == "__main__":
    main()
