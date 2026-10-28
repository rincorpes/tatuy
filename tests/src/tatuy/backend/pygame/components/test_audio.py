"""Audio forwarding, configuration volume, and outstanding regressions."""

from unittest.mock import Mock

import pytest

from tatuy.backend.config import SoundConfig
from tatuy.backend.pygame.components import audio as module
from tatuy.backend.pygame.config import PygameAudioConfig


@pytest.fixture
def mixer(monkeypatch):
    fake = Mock()
    fake.get_init.return_value = (44100, -16, 2)
    monkeypatch.setattr(module, "pygame", Mock(mixer=fake))
    monkeypatch.setattr(
        module.io.FileService,
        "validate_file_exists",
        Mock(return_value="ok.wav"),
    )
    return fake


def test_ready_reflects_enabled_initialized_mixer(mixer):
    audio = module.PygameAudio(PygameAudioConfig(enabled=True))
    assert audio.ready is True
    mixer.get_init.return_value = None
    assert audio.ready is False
    assert module.PygameAudio(PygameAudioConfig(enabled=False)).ready is False


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


def test_disabled_volume_and_stop_are_noops(mixer):
    audio = module.PygameAudio(PygameAudioConfig(enabled=False))
    audio.set_master_volume(64)
    audio.stop_all()
    assert mixer.mock_calls == []


def test_later_sound_inherits_master_volume(mixer):
    audio = module.PygameAudio(PygameAudioConfig(enabled=True))
    audio.set_master_volume(32)
    audio.load_sound("late", "late.wav")
    mixer.Sound.return_value.set_volume.assert_called_once_with(0.25)


@pytest.mark.parametrize("enabled", [False, True])
def test_unavailable_audio_operations_are_noops(mixer, enabled):
    audio = module.PygameAudio(PygameAudioConfig(enabled=enabled))
    mixer.get_init.return_value = None
    # Seed a cached sound to verify guards also protect existing handles.
    audio._sounds["hit"] = sound = Mock()
    module.io.FileService.validate_file_exists.reset_mock()

    audio.load_sound("late", "missing.wav")
    audio.play_sound("hit")
    audio.set_master_volume(64)
    audio.set_sound_volume("hit", 64)
    audio.stop_all()
    audio.shutdown()

    assert sound.mock_calls == []
    module.io.FileService.validate_file_exists.assert_not_called()
    assert "late" not in audio._sounds
    assert all(call[0] == "get_init" for call in mixer.mock_calls)
    if not enabled:
        assert mixer.mock_calls == []


def test_ready_audio_volume_and_stop_forward(mixer):
    audio = module.PygameAudio(PygameAudioConfig(enabled=True))
    audio.load_sound("hit", "hit.wav")
    audio.set_sound_volume("hit", 64)
    mixer.Sound.return_value.set_volume.assert_called_once_with(0.5)
    audio.set_master_volume(256)
    mixer.music.set_volume.assert_called_once_with(1.0)
    audio.stop_all()
    mixer.stop.assert_called_once_with()


def test_operations_after_shutdown_ignore_stale_sounds(mixer):
    audio = module.PygameAudio(PygameAudioConfig(enabled=True))
    audio.init()
    audio.load_sound("hit", "hit.wav")
    sound = mixer.Sound.return_value
    audio.shutdown()
    mixer.get_init.return_value = None
    mixer.reset_mock()
    sound.reset_mock()
    audio.play_sound("hit")
    audio.set_sound_volume("hit", 64)
    audio.set_master_volume(64)
    audio.stop_all()
    audio.shutdown()
    assert sound.mock_calls == []
    assert all(call[0] == "get_init" for call in mixer.mock_calls)


def test_explicit_init_failure_propagates_and_operations_remain_safe(mixer):
    audio = module.PygameAudio(PygameAudioConfig(enabled=True))
    mixer.init.side_effect = RuntimeError("device unavailable")
    mixer.get_init.return_value = None
    with pytest.raises(RuntimeError, match="device unavailable"):
        audio.init()
    mixer.reset_mock()
    audio.set_master_volume(64)
    audio.stop_all()
    assert all(call[0] == "get_init" for call in mixer.mock_calls)


@pytest.mark.parametrize(
    "volume,expected", [(-10, 0.0), (0, 0.0), (64, 0.5), (200, 1.0)]
)
def test_later_sound_inherits_clamped_master_volume(mixer, volume, expected):
    audio = module.PygameAudio(PygameAudioConfig(enabled=True))
    audio.set_master_volume(volume)
    audio.load_sound("late", "late.wav")
    mixer.Sound.return_value.set_volume.assert_called_once_with(expected)


def test_configured_master_applies_to_later_sounds(mixer):
    audio = module.PygameAudio(
        PygameAudioConfig(enabled=True, master_volume=0.25)
    )
    audio.init()
    audio.load_sound("late", "late.wav")
    mixer.Sound.return_value.set_volume.assert_called_once_with(0.25)


def test_per_sound_volume_overrides_without_changing_master(mixer):
    first, second, replacement = Mock(), Mock(), Mock()
    mixer.Sound.side_effect = [first, second, replacement]
    audio = module.PygameAudio(PygameAudioConfig(enabled=True))
    audio.set_master_volume(32)
    audio.load_sound("first", "first.wav")
    first.set_volume.assert_called_once_with(0.25)
    audio.set_sound_volume("first", 64)
    assert first.set_volume.call_args.args == (0.5,)
    audio.load_sound("second", "second.wav")
    second.set_volume.assert_called_once_with(0.25)

    # A later master update still replaces individual sound volumes.
    audio.set_master_volume(16)
    assert first.set_volume.call_args.args == (0.125,)
    assert second.set_volume.call_args.args == (0.125,)
    audio.load_sound("first", "replacement.wav")
    replacement.set_volume.assert_called_once_with(0.125)
    audio.play_sound("first")
    replacement.play.assert_called_once_with(loops=0)
    first.play.assert_not_called()


def test_unavailable_volume_request_does_not_change_retained_master(mixer):
    audio = module.PygameAudio(PygameAudioConfig(enabled=True))
    audio.set_master_volume(32)
    mixer.get_init.return_value = None
    audio.set_master_volume(64)
    mixer.get_init.return_value = (44100, -16, 2)
    audio.load_sound("late", "late.wav")
    mixer.Sound.return_value.set_volume.assert_called_once_with(0.25)
