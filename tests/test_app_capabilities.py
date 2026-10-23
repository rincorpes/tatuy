"""Application capability configuration preserves desktop defaults."""

from unittest.mock import Mock

from tatuy import app as app_module
from tatuy.capture.null import NullCaptureService
from tatuy.engine.runtime.loop.asyncio_loop import AsyncioLoop
from tatuy.engine.runtime.loop.python_loop import PythonLoop
from tatuy.engine.runtime.runtime import AsyncRuntime


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


def test_sync_loop_remains_default_and_async_loop_is_separate():
    app = app_module.TatuyApp()

    assert app.app_config.loop == "python"
    assert app.app_config.async_loop == "asyncio"
    assert isinstance(app.get_loop(), PythonLoop)
    assert isinstance(app.get_async_loop(), AsyncioLoop)


def test_build_async_uses_explicit_async_runtime(monkeypatch):
    app = app_module.TatuyApp({"capabilities": {"capture": False}})
    backend = object()
    engine = object()
    loop = object()
    monkeypatch.setattr(app, "create_backend", Mock(return_value=backend))
    monkeypatch.setattr(app, "create_engine", Mock(return_value=engine))
    monkeypatch.setattr(app, "get_async_loop", Mock(return_value=loop))

    runtime = app.build_async()

    assert isinstance(runtime, AsyncRuntime)
    assert runtime.engine is engine
    assert runtime.loop is loop
