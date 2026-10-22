"""Contract for sound loading, playback, volume, and mixer lifetime."""

from __future__ import annotations

from typing import Protocol

from tatuy.backend.config import AudioConfig


class Audio(Protocol):
    """Expose sound playback and volume operations behind a platform boundary.

    Attributes:
        config (AudioConfig): Read-only settings for this capability.
    """

    @property
    def config(self) -> AudioConfig:
        """Return the configuration without exposing reference reassignment.

        Returns:
            AudioConfig: Read-only configuration reference for this capability.
        """

    def init(self):
        """Initialize the configured audio device and preload configured sounds.

        Returns:
            None: This method does not return a value.
        """

    def shutdown(self):
        """Release the audio device resources owned by this capability.

        Returns:
            None: This method does not return a value.
        """

    def load_sound(self, sound_id: str, path: str):
        """Load a file and associate it with the supplied sound identifier.

        Args:
            sound_id (str): Identifier used to load or address a sound.
            path (str): Path to the source sound file.

        Returns:
            None: This method does not return a value.
        """

    def play_sound(self, sound_id: str, loops: int = 0):
        """Play a loaded sound, forwarding the requested loop count.

        Args:
            sound_id (str): Identifier used to load or address a sound.
            loops (int): Number of additional repetitions; -1 repeats
                indefinitely.

        Returns:
            None: This method does not return a value.
        """

    def set_master_volume(self, volume: int):
        """Set the master volume using the runtime integer range 0 through 128.

        Args:
            volume (int): Volume from 0 through 128, clamped to that range.

        Returns:
            None: This method does not return a value.
        """

    def set_sound_volume(self, sound_id: str, volume: int):
        """Set one sound volume using the runtime integer range 0 through 128.

        Args:
            sound_id (str): Identifier used to load or address a sound.
            volume (int): Volume from 0 through 128, clamped to that range.

        Returns:
            None: This method does not return a value.
        """

    def stop_all(self):
        """Stop currently playing sound channels.

        Returns:
            None: This method does not return a value.
        """
