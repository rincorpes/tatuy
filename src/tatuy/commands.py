from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from tatuy.capture.replay_header import ReplayHeader
from tatuy.input.pointer import Cursor

if TYPE_CHECKING:
    from tatuy.backend.protocols.window import Window
    from tatuy.engine.engine import Engine
    from tatuy.engine.scene import ScenePolicy


@dataclass
class EngineCommandContext:
    engine: Engine
    window: Window
    cursor: Cursor = Cursor.ARROW
    end_batch: bool = False


class EngineCommand(ABC):

    @abstractmethod
    def execute(self, ctx: EngineCommandContext):
        raise NotImplementedError


@dataclass
class EngineCommandQueue:
    _items: list[EngineCommand] = field(default_factory=list)

    def push(self, cmd: EngineCommand):
        self._items.append(cmd)

    def drain(self) -> list[EngineCommand]:
        items = self._items
        self._items = []
        return items


@dataclass(frozen=True)
class SetCursor(EngineCommand):
    cursor: Cursor

    def execute(self, ctx: EngineCommandContext) -> None:
        ctx.cursor = self.cursor


@dataclass(frozen=True)
class SetWindowTitle(EngineCommand):
    title: str

    def execute(self, ctx: EngineCommandContext) -> None:
        ctx.window.set_title(self.title)


@dataclass(frozen=True)
class ChangeScene(EngineCommand):
    scene_id: str

    def execute(self, ctx: EngineCommandContext) -> None:
        ctx.engine.services.scene.change(
            self.scene_id,
            ctx.engine.scene_context,
        )

        ctx.cursor = Cursor.ARROW
        ctx.end_batch = True


@dataclass(frozen=True)
class Quit(EngineCommand):
    def execute(self, ctx: EngineCommandContext) -> None:
        ctx.engine.stop()
        ctx.end_batch = True


@dataclass(frozen=True)
class PushScene(EngineCommand):
    scene_id: str
    is_overlay: bool = False
    policy: ScenePolicy | None = None

    def execute(self, ctx: EngineCommandContext) -> None:
        ctx.engine.services.scene.push(
            self.scene_id,
            ctx.engine.scene_context,
            is_overlay=self.is_overlay,
            policy=self.policy,
        )

        ctx.cursor = Cursor.ARROW
        ctx.end_batch = True


@dataclass(frozen=True)
class StartRecording(EngineCommand):
    filename: str

    def execute(self, ctx: EngineCommandContext) -> None:
        engine = ctx.engine
        capture = engine.services.capture
        settings = engine.replay_settings

        if capture.replay_recording or capture.replay_playing:
            return

        entry = engine.services.scene.input_entry()

        if entry is None:
            raise RuntimeError("No active scene to record")

        scene_id = settings.initial_scene or entry.scene_id

        if not engine.services.scene.contains(scene_id):
            raise ValueError(f"Unknown replay scene: {scene_id}")

        viewport = engine.scene_context.viewport

        header = ReplayHeader(
            game_id=settings.game_id,
            initial_scene=scene_id,
            seed=settings.seed,
            fps=engine.config.fps,
            virtual_w=viewport.virtual_w,
            virtual_h=viewport.virtual_h,
            options=entry.scene.replay_options(engine.scene_context),
        )

        engine.scene_context.replay_header = header

        try:
            # Recreate the scene before recording its first update.
            engine.services.scene.change(
                scene_id,
                engine.scene_context,
            )

            capture.start_replay_record(
                filename=self.filename,
                header=header,
            )
        except Exception:
            engine.scene_context.replay_header = None
            raise

        ctx.cursor = Cursor.ARROW
        ctx.end_batch = True


@dataclass(frozen=True)
class StopRecording(EngineCommand):
    def execute(self, ctx: EngineCommandContext) -> None:
        if not ctx.engine.services.capture.replay_recording:
            return

        ctx.engine.services.capture.stop_replay_record()
        ctx.engine.scene_context.replay_header = None


@dataclass(frozen=True)
class StartReplay(EngineCommand):
    filename: str

    def execute(self, ctx: EngineCommandContext) -> None:
        engine = ctx.engine
        capture = engine.services.capture

        if capture.replay_playing:
            return

        # Flush and close an active recording before reading its file.
        capture.stop_replay_record()
        engine.scene_context.replay_header = None

        try:
            header = capture.start_replay_play(self.filename)
        except FileNotFoundError as exc:
            print(
                f"Replay file not found: {exc.filename}. "
                "Press F3 to record, then F4 to finish."
            )
            return

        try:
            if header.game_id != engine.replay_settings.game_id:
                raise ValueError("Replay belongs to a different game")

            if not engine.services.scene.contains(header.initial_scene):
                raise ValueError(
                    f"Unknown replay scene: {header.initial_scene}"
                )

            viewport = engine.scene_context.viewport

            if (
                viewport.virtual_w != header.virtual_w
                or viewport.virtual_h != header.virtual_h
            ):
                raise ValueError(
                    "Use the recorded window dimensions: "
                    f"{header.virtual_w}x{header.virtual_h}"
                )

            engine.scene_context.replay_header = header

            engine.services.scene.change(
                header.initial_scene,
                engine.scene_context,
            )
        except Exception:
            capture.stop_replay_play()
            engine.scene_context.replay_header = None
            raise

        ctx.cursor = Cursor.ARROW
        ctx.end_batch = True


@dataclass(frozen=True)
class StopReplay(EngineCommand):
    def execute(self, ctx: EngineCommandContext) -> None:
        engine = ctx.engine

        if not engine.services.capture.replay_playing:
            return

        engine.services.capture.stop_replay_play()
        engine.scene_context.replay_header = None

        engine.services.scene.change(
            engine.config.start_scene,
            engine.scene_context,
        )

        ctx.cursor = Cursor.ARROW
        ctx.end_batch = True


@dataclass(frozen=True)
class Screenshot(EngineCommand):
    label: str | None = None

    def execute(self, ctx: EngineCommandContext) -> None:
        path = ctx.engine.services.capture.request_screenshot(self.label)
        print(f"Screenshot requested: {path}")


@dataclass(frozen=True)
class StartVideoRecording(EngineCommand):
    def execute(self, ctx: EngineCommandContext) -> None:
        engine = ctx.engine
        entry = engine.services.scene.input_entry()

        label = entry.scene_id if entry is not None else "capture"
        engine.services.capture.start_video_record(label)


@dataclass(frozen=True)
class StopVideoRecording(EngineCommand):
    def execute(self, ctx: EngineCommandContext) -> None:
        ctx.engine.services.capture.stop_video_record()
