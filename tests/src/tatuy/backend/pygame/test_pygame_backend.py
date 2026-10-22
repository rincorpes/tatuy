"""Backend capability composition and shutdown."""

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
    "enabled,auto_init",
    [
        (False, True),
        (True, False),
        (True, True),
    ],
)
def test_initialization_composes_capabilities(platform, enabled, auto_init):
    config = PygameBackendConfig(
        audio=PygameAudioConfig(
            enabled=enabled,
            auto_init=auto_init,
            frequency=22050,
            channels=1,
            chunk_size=512,
        )
    )
    backend = module.PygameBackend(config)
    platform.init.assert_not_called()
    assert backend.initialized is False
    backend.init()
    platform.init.assert_called_once_with()
    assert backend.initialized is True
    backend.window.open.assert_not_called()
    module.PygameRenderer.assert_called_once_with(
        config.renderer,
        backend.window,
        backend.viewport_transform,
    )
    module.PygameCapture.assert_called_once_with(
        config.capture, backend.window
    )
    if enabled:
        platform.mixer.pre_init.assert_called_once_with(
            frequency=22050,
            channels=1,
            buffer=512,
        )
    else:
        platform.mixer.pre_init.assert_not_called()
    assert backend.audio.init.call_count == int(enabled and auto_init)
    backend.stop()
    backend.stop()
    platform.quit.assert_called_once_with()
    assert backend.initialized is False


def test_stop_before_init_is_safe(platform):
    module.PygameBackend(PygameBackendConfig()).stop()
    platform.quit.assert_not_called()


@pytest.mark.xfail(
    strict=True, reason="B01: failed init leaks pygame resources"
)
def test_failed_initialization_releases_platform(platform, monkeypatch):
    monkeypatch.setattr(
        module,
        "PygameRenderer",
        Mock(
            side_effect=RuntimeError("renderer setup failed"),
        ),
    )
    backend = module.PygameBackend(PygameBackendConfig())
    with pytest.raises(RuntimeError, match="renderer setup"):
        backend.init()
    backend.stop()
    platform.quit.assert_called_once_with()
