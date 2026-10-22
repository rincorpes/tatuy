"""Pygame mixer operations with readiness guards and retained master volume."""

from __future__ import annotations

# Justification: Disabling no-member checks for pygame attributes since they are
# dynamically added after initialization.
# pylint: disable=no-member
import pygame

from tatuy import io
from tatuy.backend.backend_component import BackendComponent
from tatuy.backend.pygame.config import PygameAudioConfig


class PygameAudio(BackendComponent[PygameAudioConfig]):
    """Guard mixer operations and apply retained master volume to loaded sounds.

    Args:
        config (PygameAudioConfig): Settings used to configure this
            capability.
    """

    def __init__(self, config: PygameAudioConfig):
        super().__init__(config)
        self._sounds: dict[str, pygame.mixer.Sound] = {}
        self._master_volume: float | None = None

    def init(self):
        """Initialize enabled mixer audio, preload sounds, and apply configured volume.

        Disabled audio is a no-op. Device and sound-file initialization errors propagate.

        Returns:
            None: This method does not return a value.

        Raises:
            ValueError: A sound identifier is empty.
            FileNotFoundError: A configured sound file does not exist.
            pygame.error: A required native subsystem is unavailable or the
                platform operation fails.
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
        """Quit an enabled, initialized mixer; otherwise do nothing.

        Returns:
            None: This method does not return a value.

        Raises:
            pygame.error: A required native subsystem is unavailable or the
                platform operation fails.
        """
        if not self.config.enabled or not pygame.mixer.get_init():
            return
        pygame.mixer.quit()

    def load_sound(self, sound_id: str, path: str):
        """Load or replace a sound and apply the retained master gain when available.

        Disabled or uninitialized audio is a no-op. Empty identifiers raise
        ValueError when ready; file and native loading errors propagate.

        Args:
            sound_id (str): Identifier used to load or address a sound.
            path (str): Path to the source sound file.

        Returns:
            None: This method does not return a value.

        Raises:
            ValueError: A sound identifier is empty.
            FileNotFoundError: A configured sound file does not exist.
            pygame.error: A required native subsystem is unavailable or the
                platform operation fails.
        """
        if not self.config.enabled or not pygame.mixer.get_init():
            return
        if not sound_id:
            raise ValueError("sound_id cannot be empty")
        p = io.FileService.validate_file_exists(path)
        sound = pygame.mixer.Sound(p)
        if self._master_volume is not None:
            sound.set_volume(self._master_volume)
        self._sounds[sound_id] = sound

    def play_sound(self, sound_id: str, loops: int = 0):
        """Play a known sound when audio is ready; ignore disabled or missing sounds.

        Args:
            sound_id (str): Identifier used to load or address a sound.
            loops (int): Number of additional repetitions; -1 repeats
                indefinitely.

        Returns:
            None: This method does not return a value.

        Raises:
            pygame.error: A required native subsystem is unavailable or the
                platform operation fails.
        """
        if not self.config.enabled or not pygame.mixer.get_init():
            return
        s = self._sounds.get(sound_id)
        if s:
            s.play(loops=int(loops))

    def set_master_volume(self, volume: int):
        """Clamp volume to 0 through 128 and retain its normalized mixer gain.

        Apply the gain to music and existing sounds; later loads inherit it.
        Disabled or uninitialized audio ignores the request without retaining it.

        Args:
            volume (int): Volume from 0 through 128, clamped to that range.

        Returns:
            None: This method does not return a value.

        Raises:
            pygame.error: A required native subsystem is unavailable or the
                platform operation fails.
        """
        if not self.config.enabled or not pygame.mixer.get_init():
            return
        v = max(0, min(128, int(volume))) / 128.0
        pygame.mixer.music.set_volume(v)
        self._master_volume = v
        for s in self._sounds.values():
            s.set_volume(v)

    def set_sound_volume(self, sound_id: str, volume: int):
        """Override one loaded sound volume without changing the retained master gain.

        Args:
            sound_id (str): Identifier used to load or address a sound.
            volume (int): Volume from 0 through 128, clamped to that range.

        Returns:
            None: This method does not return a value.

        Raises:
            pygame.error: A required native subsystem is unavailable or the
                platform operation fails.
        """
        if not self.config.enabled or not pygame.mixer.get_init():
            return
        s = self._sounds.get(sound_id)
        if not s:
            return
        v = max(0, min(128, int(volume))) / 128.0
        s.set_volume(v)

    def stop_all(self):
        """Stop sound channels when audio is ready, leaving music ownership unchanged.

        Returns:
            None: This method does not return a value.

        Raises:
            pygame.error: A required native subsystem is unavailable or the
                platform operation fails.
        """
        if not self.config.enabled or not pygame.mixer.get_init():
            return
        pygame.mixer.stop()
