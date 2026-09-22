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

    def __str__(self) -> str:
        return f"PygameBackend(config={self.config})"

    def init(self):
        audio_config = self.config.audio

        if audio_config.enabled:
            pygame.mixer.pre_init(
                frequency=int(audio_config.frequency),
                channels=int(audio_config.channels),
                buffer=int(audio_config.chunk_size),
            )
        pygame.init()

        self.events = PygameEvents(self.config.events)
        self.window = PygameWindow(self.config.window)
        self.input = PygameInput(self.config.input)

        self.renderer = PygameRenderer(
            self.config.renderer, self.window, self.viewport_transform
        )

        self.audio = PygameAudio(self.config.audio)
        if audio_config.enabled and audio_config.auto_init:
            self.audio.init()

        self.capture = PygameCapture(self.config.capture, self.window)

        self.initialized = True

    def stop(self):
        if not self.initialized:
            return

        pygame.quit()
        self.initialized = False
