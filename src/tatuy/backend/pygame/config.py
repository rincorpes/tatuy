"""Concrete Pygame configuration defaults and compatibility error exports."""

from __future__ import annotations

from dataclasses import dataclass, field

from tatuy.backend.config import AudioConfig, BackendConfig
from tatuy.backend.config import (
    BackendConfigError as _SharedBackendConfigError,
)
from tatuy.backend.config import (
    CaptureConfig,
    EventsConfig,
    InputConfig,
    RendererConfig,
    WindowConfig,
)

# Preserve the historical import path with the canonical error type.
BackendConfigError = _SharedBackendConfigError


@dataclass(frozen=True)
class PygameEventsConfig(EventsConfig):
    """Provide the Pygame event capability configuration."""


@dataclass(frozen=True)
class PygameWindowConfig(WindowConfig):
    """Configure a Pygame display with its implementation-specific default title.

    Args:
        width (int): Initial window width in screen pixels.
        height (int): Initial window height in screen pixels.
        title (str): Initial window caption.
        resizable (bool): Whether user-driven window resizing is allowed.

    Attributes:
        width (int): Initial window width in screen pixels.
        height (int): Initial window height in screen pixels.
        title (str): Initial window caption.
        resizable (bool): Whether user-driven window resizing is allowed.
    """

    title: str = "Pygame Backend"


@dataclass(frozen=True)
class PygameRendererConfig(RendererConfig):
    """Configure the Pygame clear color and text capability.

    Args:
        background_color (Color): Initial RGB or RGBA clear color.
        text (TextConfig): Font and text configuration.

    Attributes:
        background_color (Color): Initial RGB or RGBA clear color.
        text (TextConfig): Font and text configuration.
    """


@dataclass(frozen=True)
class PygameAudioConfig(AudioConfig):
    """Configure Pygame mixer initialization and preloaded sounds.

    Args:
        enabled (bool): Whether audio is enabled; deprecated for capture
            configuration.
        auto_init (bool): Whether backend startup should initialize enabled
            audio.
        master_volume (float): Initial master gain, clamped to 0.0 through
            1.0.
        frequency (int): Requested mixer sampling frequency in hertz.
        channels (int): Requested number of mixer output channels.
        chunk_size (int): Mixer buffer size in samples.
        sounds (tuple[SoundConfig, ...]): Sounds to preload during mixer
            initialization.

    Attributes:
        enabled (bool): Whether audio is enabled; deprecated for capture
            configuration.
        auto_init (bool): Whether backend startup should initialize enabled
            audio.
        master_volume (float): Initial master gain, clamped to 0.0 through
            1.0.
        frequency (int): Requested mixer sampling frequency in hertz.
        channels (int): Requested number of mixer output channels.
        chunk_size (int): Mixer buffer size in samples.
        sounds (tuple[SoundConfig, ...]): Sounds to preload during mixer
            initialization.
    """


@dataclass(frozen=True)
class PygameInputConfig(InputConfig):
    """Configure Pygame keyboard and mouse input; gamepad mode is unsupported.

    Args:
        enable_keyboard (bool): Whether keyboard and text events are
            emitted.
        enable_mouse (bool): Whether mouse events and pointer operations
            are enabled.
        enable_gamepad (bool): Whether gamepad support is requested; Pygame
            currently rejects True.

    Attributes:
        enable_keyboard (bool): Whether keyboard and text events are
            emitted.
        enable_mouse (bool): Whether mouse events and pointer operations
            are enabled.
        enable_gamepad (bool): Whether gamepad support is requested; Pygame
            currently rejects True.
    """


@dataclass(frozen=True)
class PygameCaptureConfig(CaptureConfig):
    """Retain legacy capture options; workflow policy belongs to CaptureSettings.

    Args:
        enabled (bool): Whether audio is enabled; deprecated for capture
            configuration.
        directory (str): Deprecated capture directory; save destinations
            belong to the caller.
        format (str): Deprecated image format; concrete capture uses the
            destination suffix.

    Attributes:
        enabled (bool): Whether audio is enabled; deprecated for capture
            configuration.
        directory (str): Deprecated capture directory; save destinations
            belong to the caller.
        format (str): Deprecated image format; concrete capture uses the
            destination suffix.
    """


@dataclass(frozen=True)
class PygameBackendConfig(BackendConfig):
    """Group concrete Pygame capability settings with the default backend name.

    Args:
        name (str): Configuration alias or backend implementation name.
        events (PygameEventsConfig): Event capability settings.
        window (PygameWindowConfig): Window capability settings.
        input (PygameInputConfig): Input capability settings.
        renderer (PygameRendererConfig): Renderer capability settings.
        audio (PygameAudioConfig): Audio capability settings.
        capture (PygameCaptureConfig): Capture capability settings.

    Attributes:
        name (str): Configuration alias or backend implementation name.
        events (PygameEventsConfig): Event capability settings.
        window (PygameWindowConfig): Window capability settings.
        input (PygameInputConfig): Input capability settings.
        renderer (PygameRendererConfig): Renderer capability settings.
        audio (PygameAudioConfig): Audio capability settings.
        capture (PygameCaptureConfig): Capture capability settings.
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
