"""Optional runtime commands are safe when capabilities are disabled."""

from unittest.mock import Mock

import pytest

from tatuy.capture.null import NullCaptureService
from tatuy.commands import (
    EngineCommandContext,
    Screenshot,
    StartRecording,
    StartReplay,
    StartVideoRecording,
)
from tatuy.replay.null import NullReplayService


@pytest.mark.parametrize("command", [Screenshot(), StartVideoRecording()])
def test_capture_start_commands_noop_when_capture_is_disabled(command):
    engine = Mock()
    engine.services.capture = NullCaptureService()
    context = EngineCommandContext(engine=engine, window=Mock())

    command.execute(context)

    assert context.end_batch is False


@pytest.mark.parametrize(
    "command",
    [StartRecording("session.jsonl"), StartReplay("session.jsonl")],
)
def test_replay_start_commands_noop_when_replay_is_disabled(command):
    engine = Mock()
    engine.services.replay = NullReplayService()
    context = EngineCommandContext(engine=engine, window=Mock())

    command.execute(context)

    assert context.end_batch is False
