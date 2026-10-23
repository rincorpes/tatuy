"""Runtime service composition honors optional capability switches."""

from unittest.mock import Mock

from tatuy.capture.null import NullCaptureService
from tatuy.engine.runtime import services as module


def test_defaults_keep_capture_enabled(monkeypatch):
    capture = object()
    factory = Mock(return_value=capture)
    monkeypatch.setattr(module, "create_capture_capability", factory)
    backend = Mock()

    services = module.RuntimeServices.defaults(backend)

    assert services.capture is capture
    factory.assert_called_once_with(backend, enabled=True)


def test_defaults_can_disable_capture(monkeypatch):
    capture = NullCaptureService()
    factory = Mock(return_value=capture)
    monkeypatch.setattr(module, "create_capture_capability", factory)
    backend = Mock()

    services = module.RuntimeServices.defaults(backend, capture_enabled=False)

    assert services.capture is capture
    assert services.capture.enabled is False
    factory.assert_called_once_with(backend, enabled=False)
