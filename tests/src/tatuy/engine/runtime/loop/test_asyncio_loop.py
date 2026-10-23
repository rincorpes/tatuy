"""Async loop lifecycle, yielding, and cleanup behavior."""

import asyncio
from unittest.mock import AsyncMock, Mock

import pytest

from tatuy.engine.runtime.loop import asyncio_loop as module


@pytest.mark.parametrize("stage", ["start", "step"])
@pytest.mark.parametrize("error_type", [RuntimeError, KeyboardInterrupt])
def test_failures_stop_engine(stage, error_type):
    engine = Mock(running=True)
    error = error_type(stage)
    getattr(engine, stage).side_effect = error

    with pytest.raises(error_type) as caught:
        asyncio.run(module.AsyncioLoop().run(engine))

    assert caught.value is error
    engine.stop.assert_called_once_with()
    if stage == "start":
        engine.step.assert_not_called()


@pytest.mark.parametrize("stage", ["start", "step"])
def test_cleanup_failure_does_not_hide_run_error(stage):
    engine = Mock(running=True)
    error = ValueError(stage)
    cleanup_error = RuntimeError("cleanup")
    getattr(engine, stage).side_effect = error
    engine.stop.side_effect = cleanup_error

    with pytest.raises(ValueError) as caught:
        asyncio.run(module.AsyncioLoop().run(engine))

    assert caught.value is error
    assert caught.value.__cause__ is cleanup_error
    engine.stop.assert_called_once_with()


def test_normal_exit_steps_yields_and_stops(monkeypatch):
    engine = Mock(running=True)
    sleeper = AsyncMock()
    monkeypatch.setattr(module, "sleep", sleeper)

    def stop_after_second_step(*_):
        if engine.step.call_count == 2:
            engine.running = False

    engine.step.side_effect = stop_after_second_step

    asyncio.run(module.AsyncioLoop().run(engine))

    engine.start.assert_called_once_with()
    assert engine.step.call_count == 2
    assert [call.args[1] for call in engine.step.call_args_list] == [0, 1]
    assert all(call.args[0] >= 0 for call in engine.step.call_args_list)
    assert sleeper.await_count == 2
    engine.stop.assert_called_once_with()


def test_cleanup_failure_after_normal_exit_propagates(monkeypatch):
    engine = Mock(running=False)
    error = RuntimeError("cleanup")
    engine.stop.side_effect = error
    sleeper = AsyncMock()
    monkeypatch.setattr(module, "sleep", sleeper)

    with pytest.raises(RuntimeError) as caught:
        asyncio.run(module.AsyncioLoop().run(engine))

    assert caught.value is error
    engine.stop.assert_called_once_with()
    sleeper.assert_not_awaited()
