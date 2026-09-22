from __future__ import annotations

from dataclasses import dataclass, field

from tatuy.backend.config import (
    AudioConfig,
    BackendConfig,
    CaptureConfig,
    EventsConfig,
    InputConfig,
    RendererConfig,
    WindowConfig,
)
from tatuy.backend.exceptions import BackendError


class BackendConfigError(BackendError): ...


@dataclass(frozen=True)
class PygameEventsConfig(EventsConfig):
    """
    Configuration for events
    """


@dataclass(frozen=True)
class PygameWindowConfig(WindowConfig):
    """
    Configuration for a game window.
    """

    title: str = "Pygame Backend"


@dataclass(frozen=True)
class PygameRendererConfig(RendererConfig):
    """
    Configuration for the renderer.
    """


@dataclass(frozen=True)
class PygameAudioConfig(AudioConfig):
    """
    Configuration for audio settings.
    """


@dataclass(frozen=True)
class PygameInputConfig(InputConfig):
    """
    Configuration for input
    """


@dataclass(frozen=True)
class PygameCaptureConfig(CaptureConfig):
    """
    Configuration for capture
    """


@dataclass(frozen=True)
class PygameBackendConfig(BackendConfig):
    """
    Settings for configuring the pygame backend.
    """

    name: str = "pygame"

    events: PygameEventsConfig = field(default_factory=PygameEventsConfig)
    window: PygameWindowConfig = field(default_factory=PygameWindowConfig)
    input: PygameInputConfig = field(default_factory=PygameInputConfig)
    renderer: PygameRendererConfig = field(
        default_factory=PygameRendererConfig
    )
    audio: PygameAudioConfig = field(default_factory=PygameAudioConfig)
    capture: PygameCaptureConfig = field(default_factory=PygameCaptureConfig)
