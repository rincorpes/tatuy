"""Capture input handling respects disabled runtime capability composition."""

from unittest.mock import Mock

from tatuy.capture.null import NullCaptureService
from tatuy.capture.settings import ReplaySettings
from tatuy.commands import EngineCommandQueue
from tatuy.engine.capture_input import CaptureInputProcessor
from tatuy.input.frame import InputFrame
from tatuy.input.keys import Key


def test_disabled_capture_does_not_reserve_capture_or_replay_keys():
    command_processor = Mock()
    processor = CaptureInputProcessor(
        NullCaptureService(),
        ReplaySettings(enabled=True),
        EngineCommandQueue(),
        command_processor,
    )
    keys = frozenset({Key.F2, Key.F3, Key.F7, Key.F8})
    frame = InputFrame(
        keys_down=keys,
        keys_pressed=keys,
        keys_released=keys,
    )

    result = processor.process(frame)

    assert result.keys_down == keys
    assert result.keys_pressed == keys
    assert result.keys_released == keys
    command_processor.process.assert_not_called()
