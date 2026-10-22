"""Exercise real Engine startup failures through PythonLoop."""

from unittest.mock import Mock

import pytest

from tatuy.engine import engine as module
from tatuy.engine.loop.python_loop import PythonLoop


@pytest.mark.parametrize("stage", ["backend", "window", "scene"])
def test_startup_failure_cleans_engine_resources(monkeypatch, stage):
    backend = Mock()
    services = Mock()
    bus = Mock()
    monkeypatch.setattr(module, "event_bus", bus)
    engine = module.Engine(backend, services=services)
    failure = RuntimeError(stage)
    target = {
        "backend": backend.init,
        "window": services.window.open,
        "scene": services.scene.change,
    }[stage]
    target.side_effect = failure
    with pytest.raises(RuntimeError) as caught:
        PythonLoop(target_fps=0).run(engine)
    assert caught.value is failure
    assert engine.running is False
    services.capture.close.assert_called_once_with()
    backend.stop.assert_called_once_with()
    bus.clear.assert_called_once_with()
    engine.stop()
    backend.stop.assert_called_once_with()
