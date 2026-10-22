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
    """
    Pygame backend for tatuy.
    """

    events: PygameEvents
    window: PygameWindow
    input: PygameInput
    renderer: PygameRenderer
    audio: PygameAudio
    capture: PygameCapture

    def __init__(self, config: PygameBackendConfig):
        """
        Initialize the PygameBackend with the given config.
        """

        self.config = config
        self.viewport_transform = ViewportTransform()
        self.initialized = False
        self._platform_active = False

    def __str__(self) -> str:
        return f"PygameBackend(config={self.config})"

    def init(self):
        """Compose capabilities, rolling back platform state on failure."""
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
        """Release platform state; failed quits can be retried."""
        if not self._platform_active:
            return

        self.initialized = False
        # Retain capabilities (especially the SDL window wrapper) through quit.
        pygame.quit()
        self._platform_active = False
