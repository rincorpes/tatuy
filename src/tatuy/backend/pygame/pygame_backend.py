"""Compose Pygame capabilities and manage transactional platform startup."""

from __future__ import annotations

# Justification: Disabling no-member checks for pygame attributes since they are
# dynamically added after initialization.
# pylint: disable=no-member
import pygame

from tatuy.backend.pygame.components.events import PygameEvents
from tatuy.graphics.viewport.transform import ViewportTransform

from .components.audio import PygameAudio
from .components.capture import PygameCapture
from .components.input import PygameInput
from .components.renderer import PygameRenderer
from .components.window import PygameWindow
from .config import PygameBackendConfig


class PygameBackend:
    """Compose Pygame capabilities and own their global platform lifetime.

    Args:
        config (PygameBackendConfig): Settings used to configure this
            capability.

    Attributes:
        config (PygameBackendConfig): Backend and capability settings.
        viewport_transform (ViewportTransform): Logical-to-display mapping.
        initialized (bool): Whether startup has completed successfully.
        events (PygameEvents): Event collection capability, available after init.
        window (PygameWindow): Window capability, available after init.
        input (PygameInput): Pointer capability, available after init.
        renderer (PygameRenderer): Drawing capability, available after init.
        audio (PygameAudio): Audio capability, available after init.
        capture (PygameCapture): Frame capture capability, available after init.
    """

    events: PygameEvents
    window: PygameWindow
    input: PygameInput
    renderer: PygameRenderer
    audio: PygameAudio
    capture: PygameCapture

    def __init__(self, config: PygameBackendConfig):

        self.config = config
        self.viewport_transform = ViewportTransform()
        self.initialized = False
        self._platform_active = False

    def __str__(self) -> str:
        return f"PygameBackend(config={self.config})"

    def init(self):
        """Initialize Pygame and compose capabilities, rolling back on failure.

        Repeated successful calls preserve capabilities. Unsupported gamepad mode
        and pending failed cleanup are rejected before new platform acquisition.
        If rollback also fails, preserve the startup error and chain the cleanup error.

        Returns:
            None: This method does not return a value.

        Raises:
            RuntimeError: A previous platform shutdown failed and cleanup is
                still pending.
            NotImplementedError: Gamepad support is requested.
            FileNotFoundError: A preloaded sound file does not exist.
            ValueError: A preloaded sound identifier is empty.
            pygame.error: A required native subsystem is unavailable or the
                platform operation fails.
        """
        if self.initialized:
            return
        if self._platform_active:
            raise RuntimeError("Call stop() before retrying initialization")

        if self.config.input.enable_gamepad:
            raise NotImplementedError("Pygame gamepad input is not supported")
        audio_config = self.config.audio
        if audio_config.enabled:
            pygame.mixer.pre_init(
                frequency=int(audio_config.frequency),
                channels=int(audio_config.channels),
                buffer=int(audio_config.chunk_size),
            )

        # Even pygame.init() can fail after acquiring some resources.
        self._platform_active = True
        try:
            pygame.init()
            self.events = PygameEvents(self.config.events, self.config.input)
            self.window = PygameWindow(self.config.window)
            self.input = PygameInput(self.config.input)
            self.renderer = PygameRenderer(
                self.config.renderer, self.window, self.viewport_transform
            )
            self.audio = PygameAudio(self.config.audio)
            if audio_config.enabled and audio_config.auto_init:
                self.audio.init()
            self.capture = PygameCapture(self.config.capture, self.window)
        except BaseException as startup_error:
            try:
                self.stop()
            except BaseException as cleanup_error:
                raise startup_error from cleanup_error
            raise

        self.initialized = True

    def stop(self):
        """Quit owned platform state while retaining native wrapper references.

        Repeated calls after successful cleanup are harmless. A failed quit leaves
        cleanup pending so stop can retry; the backend is no longer initialized.

        Returns:
            None: This method does not return a value.

        Raises:
            pygame.error: A required native subsystem is unavailable or the
                platform operation fails.
        """
        if not self._platform_active:
            return

        self.initialized = False
        # Retain capabilities (especially the SDL window wrapper) through quit.
        pygame.quit()
        self._platform_active = False
