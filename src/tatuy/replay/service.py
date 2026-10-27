"""Filesystem-backed deterministic replay capability."""

from __future__ import annotations

from pathlib import Path

from tatuy.capture import events
from tatuy.capture.replay import ReplayPlayer, ReplayRecorder, ReplayRecorderConfig
from tatuy.capture.replay_frame import ReplayFrame
from tatuy.capture.replay_header import ReplayHeader
from tatuy.capture.settings import ReplaySettings
from tatuy.events.bus import event_bus
from tatuy.input.frame import InputFrame


class ReplayService:
    """Record and play deterministic input independently from media capture."""

    def __init__(self, settings: ReplaySettings | None = None) -> None:
        self.settings = settings or ReplaySettings()
        self.directory = self._resolve_directory(self.settings)
        self.recorder = ReplayRecorder()
        self.player = ReplayPlayer()
        self._header: ReplayHeader | None = None
        self._finished = False

    @property
    def enabled(self) -> bool:
        return True

    @property
    def recording(self) -> bool:
        return self.recorder.active

    @property
    def playing(self) -> bool:
        return self.player.active or self._finished

    @property
    def header(self) -> ReplayHeader | None:
        return self._header

    def start_record(self, *, filename: str, header: ReplayHeader) -> None:
        if self.recording or self.playing:
            raise RuntimeError("A replay session is already active")

        path = self.directory / filename
        self.recorder.start(ReplayRecorderConfig(path=path, header=header))
        self._header = header
        event_bus.emit(events.REPLAY_RECORD_STARTED, path=str(path))

    def stop_record(self) -> None:
        if not self.recording:
            return

        path = self.recorder.path
        self.recorder.stop()
        self._header = None
        event_bus.emit(
            events.REPLAY_RECORD_STOPPED,
            path=str(path) if path is not None else None,
        )

    def record_input(self, frame: InputFrame, dt: float) -> None:
        self.recorder.record(frame, dt)

    def start_play(self, filename: str) -> ReplayHeader:
        if self.recording or self.playing:
            raise RuntimeError("A replay session is already active")

        path = self.directory / filename
        header = self.player.start(path)
        self._header = header
        self._finished = False
        event_bus.emit(events.REPLAY_PLAY_STARTED, path=str(path))
        return header

    def next_frame(self) -> ReplayFrame | None:
        if self._finished:
            return None

        frame = self.player.next()
        if frame is None:
            self._finished = True
            event_bus.emit(events.REPLAY_PLAY_FINISHED)
        return frame

    def stop_play(self) -> None:
        was_playing = self.playing
        self.player.stop()
        self._finished = False
        if was_playing:
            self._header = None
            event_bus.emit(events.REPLAY_PLAY_STOPPED)

    def close(self) -> None:
        self.stop_record()
        self.stop_play()

    @staticmethod
    def _resolve_directory(settings: ReplaySettings) -> Path:
        root = Path(settings.root_dir).expanduser().resolve()
        directory = (root / settings.replays_dir).resolve()
        if not directory.is_relative_to(root):
            raise ValueError(
                f"Replay directory {settings.replays_dir!r} must be inside root_dir"
            )
        return directory
