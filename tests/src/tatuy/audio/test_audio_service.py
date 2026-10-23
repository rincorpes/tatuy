from unittest.mock import Mock

from tatuy.audio.service import AudioService


def test_audio_service_forwards_game_audio_operations_to_backend():
    backend = Mock()
    service = AudioService(backend)

    service.load_sound("hit", "assets/hit.wav")
    service.play("hit", loops=2)
    service.set_master_volume(80)
    service.set_sound_volume("hit", 60)
    service.stop_all()

    backend.audio.load_sound.assert_called_once_with("hit", "assets/hit.wav")
    backend.audio.play_sound.assert_called_once_with("hit", 2)
    backend.audio.set_master_volume.assert_called_once_with(80)
    backend.audio.set_sound_volume.assert_called_once_with("hit", 60)
    backend.audio.stop_all.assert_called_once_with()
