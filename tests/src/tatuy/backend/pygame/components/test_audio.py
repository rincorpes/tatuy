"""Audio forwarding, configuration volume, and outstanding regressions."""

from unittest.mock import Mock

import pytest

from tatuy.backend.config import SoundConfig
from tatuy.backend.pygame.components import audio as module
from tatuy.backend.pygame.config import PygameAudioConfig


@pytest.fixture
def mixer(monkeypatch):
    fake = Mock()
    monkeypatch.setattr(module, "pygame", Mock(mixer=fake))
    monkeypatch.setattr(
        module.io.FileService,
        "validate_file_exists",
        Mock(return_value="ok.wav"),
    )
    return fake


def test_disabled_load_play_and_shutdown_are_noops(mixer):
    audio = module.PygameAudio(PygameAudioConfig(enabled=False))
    audio.init()
    audio.load_sound("", "missing.wav")
    audio.play_sound("missing")
    audio.shutdown()
    assert mixer.mock_calls == []


@pytest.mark.parametrize("volume,expected", [(-1, 0), (0.5, 0.5), (2, 1)])
def test_config_volume_clamps_and_applies_to_preloaded_sounds(
    mixer,
    volume,
    expected,
):
    audio = module.PygameAudio(
        PygameAudioConfig(
            enabled=True,
            master_volume=volume,
            sounds=(SoundConfig("hit", "hit.wav"),),
        )
    )
    audio.init()
    mixer.init.assert_called_once_with(
        frequency=44100,
        channels=2,
        buffer=2048,
    )
    mixer.music.set_volume.assert_called_once_with(expected)
    mixer.Sound.return_value.set_volume.assert_called_once_with(expected)
    audio.play_sound("hit", loops=2)
    mixer.Sound.return_value.play.assert_called_once_with(loops=2)
    audio.shutdown()
    mixer.quit.assert_called_once_with()


def test_enabled_load_rejects_empty_id(mixer):
    with pytest.raises(ValueError, match="sound_id"):
        module.PygameAudio(PygameAudioConfig(enabled=True)).load_sound("", "x")


@pytest.mark.xfail(strict=True, reason="B02: disabled audio still calls mixer")
def test_disabled_volume_and_stop_are_noops(mixer):
    audio = module.PygameAudio(PygameAudioConfig(enabled=False))
    audio.set_master_volume(64)
    audio.stop_all()
    assert mixer.mock_calls == []


@pytest.mark.xfail(
    strict=True, reason="B03: later sounds ignore master volume"
)
def test_later_sound_inherits_master_volume(mixer):
    audio = module.PygameAudio(PygameAudioConfig(enabled=True))
    audio.set_master_volume(32)
    audio.load_sound("late", "late.wav")
    mixer.Sound.return_value.set_volume.assert_called_once_with(0.25)
