from types import SimpleNamespace
from unittest.mock import Mock, call

from tatuy.audio.service import AudioService


def _backend(*, enabled: bool = True, ready: bool = True):
    audio = Mock()
    audio.ready = ready
    return SimpleNamespace(
        initialized=True,
        config=SimpleNamespace(
            audio=SimpleNamespace(enabled=enabled, master_volume=1.0)
        ),
        audio=audio,
    )


def test_audio_service_forwards_ready_game_audio_operations_to_backend():
    backend = _backend()
    service = AudioService(backend)

    assert service.load_sound("hit", "assets/hit.wav") is True
    assert service.play("hit", loops=2) is True
    service.set_master_volume(80)
    service.set_sound_volume("hit", 60)
    service.stop_all()

    backend.audio.load_sound.assert_called_once_with("hit", "assets/hit.wav")
    backend.audio.play_sound.assert_called_once_with("hit", 2)
    backend.audio.set_master_volume.assert_called_once_with(80)
    backend.audio.set_sound_volume.assert_called_once_with("hit", 60)
    backend.audio.stop_all.assert_called_once_with()


def test_audio_service_defers_load_until_unlock():
    backend = _backend(ready=False)
    service = AudioService(backend)
    backend.audio.init.side_effect = lambda: setattr(backend.audio, "ready", True)

    assert service.load_sound("hit", "assets/hit.wav") is False
    backend.audio.load_sound.assert_not_called()

    assert service.unlock() is True

    backend.audio.init.assert_called_once_with()
    backend.audio.load_sound.assert_called_once_with("hit", "assets/hit.wav")
    backend.audio.set_master_volume.assert_called_once_with(128)
    assert service.last_error is None


def test_audio_service_unlock_failure_is_non_fatal_and_visible():
    backend = _backend(ready=False)
    backend.audio.init.side_effect = RuntimeError("audio unavailable")
    service = AudioService(backend)

    assert service.unlock() is False
    assert service.last_error == "audio unavailable"


def test_audio_service_mute_restores_desired_master_volume():
    backend = _backend()
    service = AudioService(backend)

    service.set_master_volume(80)
    service.set_muted(True)
    assert service.muted is True
    service.set_muted(False)

    assert backend.audio.set_master_volume.call_args_list[-3:] == [
        call(80),
        call(0),
        call(80),
    ]
    assert service.muted is False


def test_disabled_audio_stays_locked_and_does_not_queue_loads():
    backend = _backend(enabled=False, ready=False)
    service = AudioService(backend)

    assert service.load_sound("hit", "assets/hit.wav") is False
    assert service.unlock() is False
    backend.audio.init.assert_not_called()
    backend.audio.load_sound.assert_not_called()
