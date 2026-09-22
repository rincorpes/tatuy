from __future__ import annotations

# Justification: Disabling no-member checks for pygame attributes since they are
# dynamically added after initialization.
# pylint: disable=no-member
import pygame

from tatuy import io
from tatuy.backend.backend_component import BackendComponent
from tatuy.backend.pygame.config import PygameAudioConfig


class PygameAudio(BackendComponent[PygameAudioConfig]):
    """
    Audio port for the tatuy pygame backend.
    """

    def __init__(self, config: PygameAudioConfig):
        super().__init__(config)
        self._sounds: dict[str, pygame.mixer.Sound] = {}

    def init(self):
        """
        Initialize the audio subsystem.
        """
        if not self.config.enabled:
            return
        pygame.mixer.init(
            frequency=int(self.config.frequency),
            channels=int(self.config.channels),
            buffer=int(self.config.chunk_size),
        )

        for sound in self.config.sounds:
            self.load_sound(sound.name, sound.path)

        # Config uses 0.0–1.0; the current audio API uses 0–128.
        normalized_volume = max(
            0.0,
            min(1.0, self.config.master_volume),
        )

        self.set_master_volume(round(normalized_volume * 128))

    def shutdown(self):
        """Shutdown the audio subsystem."""
        if not self.config.enabled:
            return
        pygame.mixer.quit()

    def load_sound(self, sound_id: str, path: str):
        """
        Load a sound file.
        """
        if not self.config.enabled:
            return
        if not sound_id:
            raise ValueError("sound_id cannot be empty")
        p = io.FileService.validate_file_exists(path)
        self._sounds[sound_id] = pygame.mixer.Sound(p)

    def play_sound(self, sound_id: str, loops: int = 0):
        """
        Play a loaded sound.
        """
        if not self.config.enabled:
            return
        s = self._sounds.get(sound_id)
        if s:
            s.play(loops=int(loops))

    def set_master_volume(self, volume: int):
        """
        Set the master volume.
        """
        v = max(0, min(128, int(volume))) / 128.0
        pygame.mixer.music.set_volume(v)
        for s in self._sounds.values():
            s.set_volume(v)

    def set_sound_volume(self, sound_id: str, volume: int):
        """
        Set the volume for a specific sound.
        """
        s = self._sounds.get(sound_id)
        if not s:
            return
        v = max(0, min(128, int(volume))) / 128.0
        s.set_volume(v)

    def stop_all(self):
        """Stop all currently playing sounds."""
        pygame.mixer.stop()
