"""Platform rollback, repeated initialization, and cleanup retry."""

from unittest.mock import Mock

import pytest

from tatuy.backend.pygame import pygame_backend as module
from tatuy.backend.pygame.config import PygameAudioConfig, PygameBackendConfig


@pytest.fixture
def platform(monkeypatch):
    fake = Mock()
    monkeypatch.setattr(module, "pygame", fake)
    for name in (
        "PygameEvents",
        "PygameWindow",
        "PygameInput",
        "PygameRenderer",
        "PygameAudio",
        "PygameCapture",
    ):
        monkeypatch.setattr(module, name, Mock())
    return fake


@pytest.mark.parametrize(
    "failure", ["platform", "events", "window", "input", "audio", "capture"]
)
def test_initialization_failure_rolls_back(platform, failure):
    backend = module.PygameBackend(
        PygameBackendConfig(
            audio=PygameAudioConfig(enabled=True, auto_init=True)
        )
    )
    target = {
        "platform": platform.init,
        "events": module.PygameEvents,
        "window": module.PygameWindow,
        "input": module.PygameInput,
        "audio": module.PygameAudio.return_value.init,
        "capture": module.PygameCapture,
    }[failure]
    error = RuntimeError(failure)
    target.side_effect = error
    with pytest.raises(RuntimeError) as caught:
        backend.init()
    assert caught.value is error
    assert not backend.initialized
    platform.quit.assert_called_once_with()
    backend.stop()
    platform.quit.assert_called_once_with()
    target.side_effect = None
    backend.init()
    assert backend.initialized
    backend.stop()
    assert platform.quit.call_count == 2


def test_repeated_init_preserves_capabilities(platform):
    backend = module.PygameBackend(PygameBackendConfig())
    backend.init()
    window = backend.window
    backend.init()
    platform.init.assert_called_once_with()
    module.PygameWindow.assert_called_once_with(backend.config.window)
    assert backend.window is window
    backend.stop()


def test_failed_rollback_preserves_error_and_allows_cleanup_retry(platform):
    backend = module.PygameBackend(PygameBackendConfig())
    startup_error = ValueError("startup")
    cleanup_error = RuntimeError("quit")
    module.PygameRenderer.side_effect = startup_error
    platform.quit.side_effect = cleanup_error
    with pytest.raises(ValueError) as caught:
        backend.init()
    assert caught.value is startup_error
    assert caught.value.__cause__ is cleanup_error
    assert not backend.initialized
    with pytest.raises(RuntimeError, match="Call stop"):
        backend.init()
    platform.init.assert_called_once_with()
    platform.quit.side_effect = None
    backend.stop()
    module.PygameRenderer.side_effect = None
    backend.init()
    assert backend.initialized
    backend.stop()


def test_failed_stop_can_retry_and_retains_window(platform):
    backend = module.PygameBackend(PygameBackendConfig())
    backend.init()
    window = backend.window

    def fail_quit():
        assert backend.window is window
        raise RuntimeError("quit")

    platform.quit.side_effect = fail_quit
    with pytest.raises(RuntimeError, match="quit"):
        backend.stop()
    assert not backend.initialized
    with pytest.raises(RuntimeError, match="Call stop"):
        backend.init()
    platform.quit.side_effect = None
    backend.stop()
    backend.stop()
    assert platform.quit.call_count == 2
    assert backend.window is window
