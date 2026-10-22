"""Immutable backend configuration and dictionary decoding errors."""

from __future__ import annotations

import warnings
from dataclasses import asdict, dataclass, field
from typing import TypeVar

from tatuy.backend.exceptions import BackendError
from tatuy.dataclass_utils import dataclass_from_dict
from tatuy.graphics.color import Color

ConfigT = TypeVar(
    "ConfigT",
    bound="BaseConfig",
)


class BackendConfigError(BackendError):
    """Report invalid backend configuration with its original cause preserved."""


@dataclass(frozen=True)
class BaseConfig:
    """Provide a common representation for immutable capability settings."""

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({asdict(self)})"


@dataclass(frozen=True)
class EventsConfig(BaseConfig):
    """Configure event collection; currently has no shared options."""


@dataclass(frozen=True)
class WindowConfig(BaseConfig):
    """Configure initial window dimensions, title, and resize permission.

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

    width: int = 800
    height: int = 600
    title: str = "tatuy"
    resizable: bool = False


@dataclass(frozen=True)
class FontConfig:
    """Name a font path and its default logical rendering size.

    Args:
        name (str): Alias used to select this font.
        path (str | None): Source file path; None selects the built-in font
            where supported.
        size (int): Default font size in logical units.

    Attributes:
        name (str): Alias used to select this font.
        path (str | None): Source file path; None selects the built-in font
            where supported.
        size (int): Default font size in logical units.
    """

    name: str = "default"
    path: str | None = None
    size: int = 24


@dataclass(frozen=True)
class TextConfig(BaseConfig):
    """Configure font aliases and the font selected when a name is omitted.

    Args:
        fonts (tuple[FontConfig, ...]): Available named font
            configurations.
        default_font (str): Alias selected when no font name is supplied.

    Attributes:
        fonts (tuple[FontConfig, ...]): Available named font
            configurations.
        default_font (str): Alias selected when no font name is supplied.
    """

    fonts: tuple[FontConfig, ...] = ()
    default_font: str = "default"


@dataclass(frozen=True)
class RendererConfig(BaseConfig):
    """Configure the initial clear color and available text fonts.

    Args:
        background_color (Color): Initial RGB or RGBA clear color.
        text (TextConfig): Font and text configuration.

    Attributes:
        background_color (Color): Initial RGB or RGBA clear color.
        text (TextConfig): Font and text configuration.
    """

    background_color: Color = (0, 0, 0)
    text: TextConfig = field(default_factory=TextConfig)


@dataclass(frozen=True)
class SoundConfig:
    """Associate a sound identifier with its source file path.

    Args:
        name (str): Identifier used to load and play this sound.
        path (str): Required path to the source sound file.

    Attributes:
        name (str): Identifier used to load and play this sound.
        path (str): Required path to the source sound file.
    """

    name: str
    path: str


@dataclass(frozen=True)
class AudioConfig(BaseConfig):
    """Configure mixer startup, initial master volume, and preloaded sounds.

    Args:
        enabled (bool): Whether audio operations are enabled.
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
        enabled (bool): Whether audio operations are enabled.
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

    enabled: bool = False
    auto_init: bool = True
    master_volume: float = 1.0
    frequency: int = 44100
    channels: int = 2
    chunk_size: int = 2048
    sounds: tuple[SoundConfig, ...] = ()


@dataclass(frozen=True)
class InputConfig(BaseConfig):
    """Control keyboard, mouse, and implementation-supported gamepad input.

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

    enable_keyboard: bool = True
    enable_mouse: bool = True
    enable_gamepad: bool = False


@dataclass(frozen=True)
class CaptureConfig(BaseConfig):
    """Retain deprecated backend capture fields for configuration compatibility.

    Args:
        enabled (bool): Deprecated capture flag, accepted but ignored.
        directory (str): Deprecated capture directory; save destinations
            belong to the caller.
        format (str): Deprecated image format; concrete capture uses the
            destination suffix.

    Attributes:
        enabled (bool): Deprecated capture flag, accepted but ignored.
        directory (str): Deprecated capture directory; save destinations
            belong to the caller.
        format (str): Deprecated image format; concrete capture uses the
            destination suffix.

    Warns:
        DeprecationWarning: Nondefault legacy capture settings are ignored.
    """

    enabled: bool = False
    directory: str = "captures"
    format: str = "png"

    def __post_init__(self) -> None:
        if (
            self.enabled
            or self.directory != "captures"
            or self.format != "png"
        ):
            warnings.warn(
                "Backend capture enabled/directory/format are deprecated and ignored; "
                "use CaptureSettings for capture workflows",
                DeprecationWarning,
                stacklevel=2,
            )


@dataclass(frozen=True)
class BackendConfig:
    """Group immutable capability settings for a named backend.

    Args:
        name (str): Configuration alias or backend implementation name.
        events (EventsConfig): Event capability settings.
        window (WindowConfig): Window capability settings.
        input (InputConfig): Input capability settings.
        renderer (RendererConfig): Renderer capability settings.
        audio (AudioConfig): Audio capability settings.
        capture (CaptureConfig): Capture capability settings.

    Attributes:
        name (str): Configuration alias or backend implementation name.
        events (EventsConfig): Event capability settings.
        window (WindowConfig): Window capability settings.
        input (InputConfig): Input capability settings.
        renderer (RendererConfig): Renderer capability settings.
        audio (AudioConfig): Audio capability settings.
        capture (CaptureConfig): Capture capability settings.
    """

    name: str

    events: EventsConfig = field(default_factory=EventsConfig)
    window: WindowConfig = field(default_factory=WindowConfig)
    input: InputConfig = field(default_factory=InputConfig)
    renderer: RendererConfig = field(default_factory=RendererConfig)
    audio: AudioConfig = field(default_factory=AudioConfig)
    capture: CaptureConfig = field(default_factory=CaptureConfig)

    def to_dict(self) -> dict:
        """Return a recursive dataclass dictionary suitable for configuration round trips.

        Returns:
            dict: Recursively converted configuration values.
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> BackendConfig:
        """Decode nested configuration values into this concrete dataclass.

        Raise BackendConfigError, chained from the original TypeError or ValueError,
        when fields, nested types, or constructor validation reject the input.

        Args:
            data (dict): Configuration dictionary to decode.

        Returns:
            BackendConfig: Decoded immutable backend configuration.

        Raises:
            BackendConfigError: Configuration data cannot be decoded into the
                declared settings.
        """
        try:
            return dataclass_from_dict(cls, data)
        except (TypeError, ValueError) as error:
            raise BackendConfigError(str(error)) from error
