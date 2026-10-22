"""Backend configuration decoding and validation."""

from dataclasses import FrozenInstanceError

import pytest

from tatuy.backend.config import BackendConfigError, FontConfig, SoundConfig
from tatuy.backend.pygame.config import PygameBackendConfig, PygameWindowConfig


def test_nested_configuration_and_round_trip():
    config = PygameBackendConfig.from_dict(
        {
            "window": {"width": 320, "height": 240, "resizable": True},
            "renderer": {
                "background_color": [10, 20, 30, 128],
                "text": {"fonts": [{"name": "ui", "path": None, "size": 18}]},
            },
            "audio": {
                "enabled": True,
                "master_volume": 1,
                "sounds": [{"name": "hit", "path": "hit.wav"}],
            },
        }
    )
    assert isinstance(config, PygameBackendConfig)
    assert isinstance(config.window, PygameWindowConfig)
    assert config.window.width == 320
    assert config.window.height == 240
    assert config.window.resizable is True
    assert config.renderer.background_color == (10, 20, 30, 128)
    assert config.renderer.text.fonts == (FontConfig("ui", None, 18),)
    assert config.audio.sounds == (SoundConfig("hit", "hit.wav"),)
    assert config.audio.master_volume == 1.0
    assert PygameBackendConfig.from_dict(config.to_dict()) == config


def test_defaults_are_independent_and_frozen():
    first = PygameBackendConfig.from_dict({})
    second = PygameBackendConfig.from_dict({})
    assert first.name == "pygame"
    assert first.window.width == 800
    assert first.window is not second.window
    with pytest.raises(FrozenInstanceError):
        first.window.width = 1


@pytest.mark.parametrize(
    "data",
    [
        {"unknown": 1},
        {"window": {"unknown": 1}},
        {"window": {"width": True}},
        {"window": {"width": "800"}},
        {"audio": {"enabled": 1}},
        {"renderer": {"background_color": [1, 2]}},
        {"audio": {"sounds": [{"name": "missing_path"}]}},
        {"window": None},
    ],
)
def test_invalid_config_is_wrapped(data):
    with pytest.raises(BackendConfigError) as error:
        PygameBackendConfig.from_dict(data)
    assert isinstance(error.value.__cause__, (TypeError, ValueError))


def test_exception_import_compatibility():
    from tatuy.backend.exceptions import BackendError
    from tatuy.backend.pygame.config import BackendConfigError as LegacyError
    from tatuy.backend.pygame.exceptions import PygameBackendError

    assert LegacyError is BackendConfigError
    assert issubclass(PygameBackendError, BackendError)
    with pytest.raises(LegacyError):
        PygameBackendConfig.from_dict({"unknown": 1})


def test_legacy_capture_settings_warn_without_enforcing():
    from tatuy.backend.config import CaptureConfig

    with pytest.warns(DeprecationWarning, match="CaptureSettings"):
        config = CaptureConfig(enabled=True, directory="old", format="bmp")
    assert config.enabled and config.directory == "old"
