from __future__ import annotations

from pathlib import Path

from tatuy.backend.backend import Backend


class AudioService:
    """Coordinate runtime audio readiness, deferred loads, and mute state.

    Args:
        backend: Active runtime backend that owns the concrete audio device.

    Attributes:
        last_error: Most recent deferred audio initialization/load error, if any.
    """

    def __init__(self, backend: Backend):
        self.backend = backend
        configured_volume = getattr(backend.config.audio, "master_volume", 1.0)
        if not isinstance(configured_volume, (int, float)):
            configured_volume = 1.0
        self._master_volume = round(max(0.0, min(1.0, configured_volume)) * 128)
        self._muted = False
        self._pending_sounds: dict[str, str] = {}
        self.last_error: str | None = None

    @property
    def enabled(self) -> bool:
        """Return whether the configured backend audio capability is enabled."""
        return bool(self.backend.config.audio.enabled)

    @property
    def ready(self) -> bool:
        """Return whether the concrete backend audio device is initialized."""
        if not self.backend.initialized or not hasattr(self.backend, "audio"):
            return False
        return bool(self.backend.audio.ready)

    @property
    def muted(self) -> bool:
        """Return whether runtime master output is muted."""
        return self._muted

    def unlock(self) -> bool:
        """Initialize deferred audio after a user gesture and flush pending loads.

        Returns:
            True when audio is ready after the call; otherwise False.
        """
        if not self.enabled or not self.backend.initialized:
            return False
        try:
            if not self.ready:
                self.backend.audio.init()
            if not self.ready:
                return False
            pending = tuple(self._pending_sounds.items())
            for sound_id, path in pending:
                self.backend.audio.load_sound(sound_id, path)
            self._pending_sounds.clear()
            self._apply_master_volume()
            self.last_error = None
            return True
        except (OSError, RuntimeError, ValueError) as exc:
            self.last_error = str(exc)
            return False

    def load_sound(self, sound_id: str, file_path: str | Path) -> bool:
        """Load a sound immediately when ready or defer it until audio unlocks."""
        path = str(file_path)
        if not self.enabled:
            return False
        if not self.ready:
            self._pending_sounds[sound_id] = path
            return False
        self.backend.audio.load_sound(sound_id, path)
        return True

    def play(self, sound_id: str, loops: int = 0) -> bool:
        """Play a loaded sound when audio is ready."""
        if not self.ready:
            return False
        self.backend.audio.play_sound(sound_id, loops)
        return True

    def set_master_volume(self, volume: int) -> None:
        """Retain and apply the desired master volume using the 0-128 range."""
        self._master_volume = max(0, min(128, int(volume)))
        self._apply_master_volume()

    def set_sound_volume(self, sound_id: str, volume: int) -> None:
        """Set one sound volume when audio is ready."""
        if self.ready:
            self.backend.audio.set_sound_volume(sound_id, volume)

    def set_muted(self, muted: bool) -> None:
        """Mute or restore runtime master output without losing desired volume."""
        self._muted = bool(muted)
        self._apply_master_volume()

    def toggle_muted(self) -> bool:
        """Toggle mute state and return the new state."""
        self.set_muted(not self._muted)
        return self._muted

    def stop_all(self) -> None:
        """Stop active sounds when audio is ready."""
        if self.ready:
            self.backend.audio.stop_all()

    def _apply_master_volume(self) -> None:
        if not self.ready:
            return
        self.backend.audio.set_master_volume(0 if self._muted else self._master_volume)
