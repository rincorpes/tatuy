"""Capture input handling respects disabled runtime capability composition."""

from unittest.mock import Mock

from tatuy.capture.null import NullCaptureService
from tatuy.capture.settings import ReplaySettings
from tatuy.commands import EngineCommandQueue
from tatuy.engine.capture_input import CaptureInputProcessor
from tatuy.input.frame import InputFrame
from tatuy.input.keys import Key
from tatuy.replay.null import NullReplayService


def test_disabled_capture_and_replay_do_not_reserve_runtime_keys():
    command_processor = Mock()
    processor = CaptureInputProcessor(
        NullCaptureService(),
        NullReplayService(),
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


def test_replay_hotkeys_remain_available_when_capture_is_disabled():
    command_processor = Mock()
    replay = Mock(enabled=True, recording=False, playing=False)
    processor = CaptureInputProcessor(
        NullCaptureService(),
        replay,
        ReplaySettings(enabled=True),
        EngineCommandQueue(),
        command_processor,
    )
    keys = frozenset({Key.F2, Key.F3, Key.F7, Key.F8})
    frame = InputFrame(
        keys_down=keys,
        keys_pressed=frozenset({Key.F3}),
        keys_released=frozenset(),
    )

    result = processor.process(frame)

    assert result.keys_down == frozenset({Key.F2, Key.F7, Key.F8})
    assert result.keys_pressed == frozenset()
    command_processor.process.assert_called_once_with()
