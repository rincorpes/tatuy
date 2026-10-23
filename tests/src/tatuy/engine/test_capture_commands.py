"""Capture commands are safe when the capture capability is disabled."""

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


@pytest.mark.parametrize(
    "command",
    [
        Screenshot(),
        StartRecording("session.jsonl"),
        StartReplay("session.jsonl"),
        StartVideoRecording(),
    ],
)
def test_capture_start_commands_noop_when_capture_is_disabled(command):
    engine = Mock()
    engine.services.capture = NullCaptureService()
    context = EngineCommandContext(engine=engine, window=Mock())

    command.execute(context)

    assert context.end_batch is False
