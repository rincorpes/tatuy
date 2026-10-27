"""Application capability configuration preserves desktop defaults."""

from unittest.mock import Mock

from tatuy import app as app_module
from tatuy.capture.null import NullCaptureService
from tatuy.engine.runtime.loop.asyncio_loop import AsyncioLoop
from tatuy.replay.null import NullReplayService
from tatuy.engine.runtime.loop.python_loop import PythonLoop
from tatuy.engine.runtime.runtime import Runtime


def test_capture_capability_is_enabled_by_default(monkeypatch):
    created = object()
    factory = Mock(return_value=created)
    monkeypatch.setattr(app_module, "create_capture_capability", factory)

    app = app_module.TatuyApp()
    backend = Mock()

    assert app.capabilities_config.capture is True
    assert app.create_capture(backend) is created
    factory.assert_called_once_with(
        backend,
        enabled=True,
        settings=app.resources.get(app_module.CaptureSettings),
    )


def test_capture_capability_can_be_disabled(monkeypatch):
    created = NullCaptureService()
    factory = Mock(return_value=created)
    monkeypatch.setattr(app_module, "create_capture_capability", factory)

    app = app_module.TatuyApp({"capabilities": {"capture": False}})
    backend = Mock()
    capture = app.create_capture(backend)

    assert app.capabilities_config.capture is False
    assert capture is created
    assert capture.enabled is False
    factory.assert_called_once_with(
        backend,
        enabled=False,
        settings=app.resources.get(app_module.CaptureSettings),
    )


def test_replay_capability_is_enabled_by_default(monkeypatch):
    created = object()
    factory = Mock(return_value=created)
    monkeypatch.setattr(app_module, "create_replay_capability", factory)

    app = app_module.TatuyApp()

    assert app.capabilities_config.replay is True
    assert app.create_replay() is created
    factory.assert_called_once_with(
        enabled=True,
        settings=app.resources.get(app_module.ReplaySettings),
    )


def test_replay_capability_can_be_disabled_independently(monkeypatch):
    created = NullReplayService()
    factory = Mock(return_value=created)
    monkeypatch.setattr(app_module, "create_replay_capability", factory)

    app = app_module.TatuyApp(
        {"capabilities": {"capture": True, "replay": False}}
    )
    replay = app.create_replay()

    assert app.capabilities_config.capture is True
    assert app.capabilities_config.replay is False
    assert replay is created
    assert replay.enabled is False
    factory.assert_called_once_with(
        enabled=False,
        settings=app.resources.get(app_module.ReplaySettings),
    )


def test_python_loop_remains_the_default_loop():
    app = app_module.TatuyApp()

    assert app.app_config.loop == "python"
    assert isinstance(app.get_loop(), PythonLoop)


def test_asyncio_loop_uses_the_same_loop_setting():
    app = app_module.TatuyApp({"app": {"loop": "asyncio"}})

    assert app.app_config.loop == "asyncio"
    assert isinstance(app.get_loop(), AsyncioLoop)


def test_build_returns_one_runtime_with_configured_execution_mode(monkeypatch):
    app = app_module.TatuyApp(
        {
            "app": {"loop": "asyncio"},
            "capabilities": {"capture": False},
        }
    )
    backend = object()
    engine = Mock(config=app_module.EngineConfig())
    monkeypatch.setattr(app, "create_backend", Mock(return_value=backend))
    monkeypatch.setattr(app, "create_engine", Mock(return_value=engine))

    runtime = app.build()

    assert isinstance(runtime, Runtime)
    assert runtime.engine is engine
    assert isinstance(runtime.loop, AsyncioLoop)
    assert runtime.mode == "async"
