"""Capture and replay input shortcuts."""

from __future__ import annotations

from dataclasses import replace

from tatuy.capture.service import CaptureService
from tatuy.capture.settings import ReplaySettings
from tatuy.commands import (
    EngineCommand,
    EngineCommandQueue,
    Screenshot,
    StartRecording,
    StartReplay,
    StartVideoRecording,
    StopRecording,
    StopReplay,
    StopVideoRecording,
)
from tatuy.engine.command_processor import EngineCommandProcessor
from tatuy.input.frame import InputFrame
from tatuy.input.keys import Key


class CaptureInputProcessor:
    """Translate reserved capture hotkeys into engine commands."""

    def __init__(
        self,
        capture: CaptureService,
        replay_settings: ReplaySettings,
        commands: EngineCommandQueue,
        command_processor: EngineCommandProcessor,
    ) -> None:
        self._capture = capture
        self._replay_settings = replay_settings
        self._commands = commands
        self._command_processor = command_processor

    def process(self, live_input: InputFrame) -> InputFrame:
        """Queue capture commands and remove reserved keys from gameplay input."""
        reserved: set[Key] = set()
        queued = False

        if self._capture.settings.hotkeys_enabled:
            reserved.update({Key.F2, Key.F7, Key.F8})

            if live_input.is_pressed(Key.F2):
                self._commands.push(Screenshot())
                queued = True

            if live_input.is_pressed(Key.F8) and self._capture.video_recording:
                self._commands.push(StopVideoRecording())
                queued = True
            elif (
                live_input.is_pressed(Key.F7) and not self._capture.video_busy
            ):
                self._commands.push(StartVideoRecording())
                queued = True

        if self._replay_settings.enabled:
            reserved.update({Key.F3, Key.F4, Key.F5, Key.F6})

            filename = self._replay_settings.filename
            command: EngineCommand | None = None

            if live_input.is_pressed(Key.F6) and self._capture.replay_playing:
                command = StopReplay()
            elif (
                live_input.is_pressed(Key.F4)
                and self._capture.replay_recording
            ):
                command = StopRecording()
            elif (
                live_input.is_pressed(Key.F5)
                and not self._capture.replay_playing
            ):
                command = StartReplay(filename)
            elif (
                live_input.is_pressed(Key.F3)
                and not self._capture.replay_recording
                and not self._capture.replay_playing
            ):
                command = StartRecording(filename)

            if command is not None:
                self._commands.push(command)
                queued = True

        if queued:
            self._command_processor.process()

        return replace(
            live_input,
            keys_down=live_input.keys_down - reserved,
            keys_pressed=live_input.keys_pressed - reserved,
            keys_released=live_input.keys_released - reserved,
        )
