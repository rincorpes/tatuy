from __future__ import annotations

from dataclasses import asdict, dataclass, field, fields, is_dataclass
from enum import Enum
from types import UnionType
from typing import Any, TypeVar, Union, get_args, get_origin, get_type_hints

from tatuy.backend.exceptions import BackendError
from tatuy.graphics.color import Color

ConfigT = TypeVar(
    "ConfigT",
    bound="BaseConfig",
)


class BackendConfigError(BackendError): ...


@dataclass(frozen=True)
class BaseConfig:
    def __str__(self) -> str:
        return f"{self.__class__.__name__}({asdict(self)})"


@dataclass(frozen=True)
class EventsConfig(BaseConfig): ...


@dataclass(frozen=True)
class WindowConfig(BaseConfig):
    """
    Configuration for a game window (not implemented).
    """

    width: int = 800
    height: int = 600
    title: str = "tatuy"
    resizable: bool = False


@dataclass(frozen=True)
class FontConfig:
    """
    Configuration for font rendering (not implemented).
    """

    name: str = "default"
    path: str | None = None
    size: int = 24


@dataclass(frozen=True)
class TextConfig(BaseConfig):
    """
    Configuration for font text.
    """

    fonts: tuple[FontConfig, ...] = ()
    default_font: str = "default"


@dataclass(frozen=True)
class RendererConfig(BaseConfig):
    """
    Configuration for the renderer (not implemented).
    """

    background_color: Color = (0, 0, 0)
    text: TextConfig = field(default_factory=TextConfig)


@dataclass(frozen=True)
class SoundConfig:
    """
    Configuration for audio settings (not implemented).
    """

    name: str
    path: str


@dataclass(frozen=True)
class AudioConfig(BaseConfig):
    """
    Configuration for audio settings (not implemented).
    """

    enabled: bool = False
    auto_init: bool = True
    master_volume: float = 1.0
    frequency: int = 44100
    channels: int = 2
    chunk_size: int = 2048
    sounds: tuple[SoundConfig, ...] = ()


# TODO: None of these currently have effect
@dataclass(frozen=True)
class InputConfig(BaseConfig):
    enable_keyboard: bool = True
    enable_mouse: bool = True
    enable_gamepad: bool = False


@dataclass(frozen=True)
class CaptureConfig(BaseConfig):
    enabled: bool = False
    directory: str = "captures"
    format: str = "png"


@dataclass(frozen=True)
class BackendConfig:
    """
    Settings for configuring the native backend.
    """

    name: str

    events: EventsConfig = field(default_factory=EventsConfig)
    window: WindowConfig = field(default_factory=WindowConfig)
    input: InputConfig = field(default_factory=InputConfig)
    renderer: RendererConfig = field(default_factory=RendererConfig)
    audio: AudioConfig = field(default_factory=AudioConfig)
    capture: CaptureConfig = field(default_factory=CaptureConfig)

    def to_dict(self) -> dict:
        """
        Convert the BackendConfig to a dictionary.

        :return: Dictionary representation of the settings.
        :rtype: dict
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> BackendConfig:
        try:
            return cls._dataclass_from_dict(cls, data)
        except (TypeError, ValueError) as error:
            raise BackendConfigError(str(error)) from error

    @classmethod
    def _decode(cls, value: Any, annotation: Any) -> Any:
        if value is None:
            return None

        if isinstance(annotation, type) and issubclass(annotation, Enum):
            return annotation(value)

        origin = get_origin(annotation)
        arguments = get_args(annotation)

        if origin in (Union, UnionType):
            valid_types = [
                item for item in arguments if item is not type(None)
            ]
            for item_type in valid_types:
                try:
                    return cls._decode(value, item_type)
                except (TypeError, ValueError):
                    pass
            return value

        if origin is tuple:
            item_type = arguments[0] if arguments else Any
            return tuple(cls._decode(item, item_type) for item in value)

        if origin is list:
            item_type = arguments[0] if arguments else Any
            return [cls._decode(item, item_type) for item in value]

        if origin is dict:
            key_type, item_type = arguments or (Any, Any)
            return {
                cls._decode(key, key_type): cls._decode(item, item_type)
                for key, item in value.items()
            }

        if isinstance(annotation, type) and is_dataclass(annotation):
            return cls._dataclass_from_dict(annotation, value)

        return value

    @classmethod
    def _dataclass_from_dict(
        cls, config_type: type, data: dict[str, Any]
    ) -> Any:
        annotations = get_type_hints(config_type)

        kwargs = {
            field.name: cls._decode(data[field.name], annotations[field.name])
            for field in fields(config_type)
            if field.init and field.name in data
        }
        return config_type(**kwargs)
