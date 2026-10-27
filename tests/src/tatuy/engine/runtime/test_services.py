"""Runtime service composition honors optional capability switches."""

from unittest.mock import Mock

from tatuy.capture.null import NullCaptureService
from tatuy.engine.runtime import services as module
from tatuy.replay.null import NullReplayService
from tatuy.storage.ephemeral import EphemeralStorageProvider


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


def test_defaults_keep_replay_enabled(monkeypatch):
    replay = object()
    factory = Mock(return_value=replay)
    monkeypatch.setattr(module, "create_replay_capability", factory)
    backend = Mock()

    services = module.RuntimeServices.defaults(backend, capture_enabled=False)

    assert services.replay is replay
    factory.assert_called_once_with(enabled=True)


def test_defaults_can_disable_replay_independently(monkeypatch):
    replay = NullReplayService()
    factory = Mock(return_value=replay)
    monkeypatch.setattr(module, "create_replay_capability", factory)
    backend = Mock()

    services = module.RuntimeServices.defaults(
        backend,
        capture_enabled=False,
        replay_enabled=False,
    )

    assert services.capture.enabled is False
    assert services.replay is replay
    assert services.replay.enabled is False
    factory.assert_called_once_with(enabled=False)


def test_defaults_preserve_explicit_asset_provider():
    backend = Mock()
    assets = object()

    services = module.RuntimeServices.defaults(
        backend,
        capture_enabled=False,
        replay_enabled=False,
        assets=assets,
    )

    assert services.assets is assets


def test_defaults_preserve_explicit_storage_provider():
    backend = Mock()
    storage = EphemeralStorageProvider()

    services = module.RuntimeServices.defaults(
        backend,
        capture_enabled=False,
        replay_enabled=False,
        storage=storage,
    )

    assert services.storage is storage
    assert services.storage.persistent is False
