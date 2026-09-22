from __future__ import annotations

from typing import Protocol

from tatuy.backend.config import AudioConfig


class Audio(Protocol):
    """
    Interface for audio operations.
    """

    config: AudioConfig

    def init(self):
        """
        Initialize audio subsystem.
        """

    def shutdown(self):
        """
        Shutdown the audio subsystem.
        """

    def load_sound(self, sound_id: str, path: str):
        """
        Load a sound file.
        """

    def play_sound(self, sound_id: str, loops: int = 0):
        """
        Play a loaded sound.
        """

    def set_master_volume(self, volume: int):
        """
        Set the master volume.
        """

    def set_sound_volume(self, sound_id: str, volume: int):
        """
        Set volume for a specific sound.
        """

    def stop_all(self):
        """
        Stop all currently playing sounds.
        """
