"""Engine cleanup retries, failure propagation, and event unsubscription."""

from unittest.mock import Mock

import pytest

from tatuy.engine import engine as module
from tatuy.engine.runtime.loop.python_loop import PythonLoop
from tatuy.events.bus import event_bus


@pytest.fixture
def runtime(monkeypatch):
    backend = Mock()
    services = Mock()
    bus = Mock()
    monkeypatch.setattr(module, "event_bus", bus)
    engine = module.Engine(backend, services=services)
    return engine, backend, services, bus


def test_stop_before_start_does_not_close_resources(runtime):
    engine, backend, services, bus = runtime
    engine.stop()
    services.replay.close.assert_not_called()
    services.capture.close.assert_not_called()
    backend.stop.assert_not_called()
    bus.clear.assert_not_called()


def test_successful_stop_is_idempotent(runtime):
    engine, backend, services, bus = runtime
    engine.start()
    engine.stop()
    engine.stop()
    assert not engine.running
    services.replay.close.assert_called_once_with()
    services.capture.close.assert_called_once_with()
    backend.stop.assert_called_once_with()
    bus.clear.assert_called_once_with()


@pytest.mark.parametrize("stage", ["replay", "capture", "backend"])
@pytest.mark.parametrize("error_type", [RuntimeError, KeyboardInterrupt])
def test_failed_cleanup_retries_only_unfinished_resources(
    runtime, stage, error_type
):
    engine, backend, services, bus = runtime
    engine.start()
    targets = {
        "replay": services.replay.close,
        "capture": services.capture.close,
        "backend": backend.stop,
    }
    target = targets[stage]
    failure = error_type("cleanup failed")
    target.side_effect = failure
    with pytest.raises(error_type) as caught:
        engine.stop()
    assert caught.value is failure
    assert not engine.running
    for resource in targets.values():
        resource.assert_called_once_with()
    bus.clear.assert_called_once_with()

    target.side_effect = None
    engine.stop()
    engine.stop()
    for name, resource in targets.items():
        assert resource.call_count == (2 if name == stage else 1)
    assert bus.clear.call_count == 2


@pytest.mark.parametrize("stage", ["replay", "capture", "backend"])
def test_cleanup_failure_unsubscribes_events(monkeypatch, runtime, stage):
    engine, backend, services, _ = runtime
    monkeypatch.setattr(module, "event_bus", event_bus)
    event_bus.clear()
    try:
        engine.start()
        subscriber = Mock()
        event_bus.on("quit", subscriber)
        target = {
            "replay": services.replay.close,
            "capture": services.capture.close,
            "backend": backend.stop,
        }[stage]
        target.side_effect = RuntimeError("cleanup failed")
        with pytest.raises(RuntimeError):
            engine.stop()
        event_bus.emit("quit")
        subscriber.assert_not_called()
    finally:
        event_bus.clear()


def test_start_refuses_pending_cleanup(runtime):
    engine, backend, _, _ = runtime
    engine.start()
    backend.stop.side_effect = RuntimeError("cleanup failed")
    with pytest.raises(RuntimeError):
        engine.stop()
    with pytest.raises(RuntimeError, match="stop"):
        engine.start()
    backend.init.assert_called_once_with()
    assert not engine.running


def test_startup_and_cleanup_failure_preserve_error_and_allow_retry(runtime):
    engine, backend, services, bus = runtime
    startup_error = ValueError("startup failed")
    cleanup_error = RuntimeError("cleanup failed")
    backend.init.side_effect = startup_error
    backend.stop.side_effect = cleanup_error
    with pytest.raises(ValueError) as caught:
        PythonLoop(target_fps=0).run(engine)
    assert caught.value is startup_error
    assert caught.value.__cause__ is cleanup_error
    bus.clear.assert_called_once_with()
    backend.stop.side_effect = None
    engine.stop()
    assert backend.stop.call_count == 2
    services.replay.close.assert_called_once_with()
    services.capture.close.assert_called_once_with()


def test_both_failed_resources_can_be_retried(runtime):
    engine, backend, services, bus = runtime
    engine.start()
    capture_error = ValueError("capture failed")
    backend_error = RuntimeError("backend failed")
    services.capture.close.side_effect = capture_error
    backend.stop.side_effect = backend_error
    with pytest.raises(RuntimeError) as caught:
        engine.stop()
    assert caught.value is backend_error
    assert caught.value.__context__ is capture_error
    bus.clear.assert_called_once_with()
    services.capture.close.side_effect = None
    backend.stop.side_effect = None
    engine.stop()
    services.replay.close.assert_called_once_with()
    assert services.capture.close.call_count == 2
    assert backend.stop.call_count == 2
