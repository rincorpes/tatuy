"""Loop startup, execution, and cleanup boundaries."""

from unittest.mock import Mock

import pytest

from tatuy.engine.runtime.loop.python_loop import PythonLoop


@pytest.mark.parametrize("stage", ["start", "step"])
@pytest.mark.parametrize("error_type", [RuntimeError, KeyboardInterrupt])
def test_failures_stop_engine(stage, error_type):
    engine = Mock(running=True)
    error = error_type(stage)
    getattr(engine, stage).side_effect = error
    with pytest.raises(error_type) as caught:
        PythonLoop(target_fps=0).run(engine)
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
        PythonLoop(target_fps=0).run(engine)
    assert caught.value is error
    assert caught.value.__cause__ is cleanup_error
    engine.stop.assert_called_once_with()


def test_normal_exit_stops_engine():
    engine = Mock(running=True)
    engine.step.side_effect = lambda *_: setattr(engine, "running", False)
    PythonLoop(target_fps=0).run(engine)
    engine.start.assert_called_once_with()
    engine.step.assert_called_once()
    assert engine.step.call_args.args[1] == 0
    engine.stop.assert_called_once_with()


def test_cleanup_failure_after_normal_exit_propagates():
    engine = Mock(running=False)
    error = RuntimeError("cleanup")
    engine.stop.side_effect = error
    with pytest.raises(RuntimeError) as caught:
        PythonLoop().run(engine)
    assert caught.value is error
    engine.stop.assert_called_once_with()
