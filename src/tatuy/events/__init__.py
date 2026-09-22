"""
Core event types and structures.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from enum import Enum, auto
from typing import Any


def _build_dict(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value) and not isinstance(value, type):
        return {
            field_name: _build_dict(field_value)
            for field_name, field_value in asdict(value).items()
        }

    if isinstance(value, dict):
        return {key: _build_dict(item) for key, item in value.items()}

    if isinstance(value, (list, tuple, set)):
        return [_build_dict(item) for item in value]
    return value


class EventType(Enum):
    """
    High-level event types understood by the core.
    """

    # core
    UNKNOWN = auto()
    QUIT = auto()

    # input
    KEYDOWN = auto()
    KEYUP = auto()
    TEXTINPUT = auto()
    MOUSEMOTION = auto()
    MOUSEBUTTONDOWN = auto()
    MOUSEBUTTONUP = auto()
    MOUSEWHEEL = auto()

    # Window
    WINDOWRESIZED = auto()
    WINDOWMOVED = auto()
    WINDOWSIZECHANGED = auto()
    WINDOWMINIMIZED = auto()
    WINDOWMAXIMIZED = auto()
    WINDOWRESTORED = auto()
    WINDOWCLOSE = auto()


class EventCategory(str, Enum):
    """
    Categories of events for filtering purposes.
    """

    INPUT = "input"
    WINDOW = "window"


# Justification: Simple data container for now
# pylint: disable=too-many-instance-attributes
@dataclass(frozen=True)
class Event:
    """
    Core event type.
    """

    category: EventCategory
    type: EventType
    type_name: str
    attrs: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return _build_dict(self)


# pylint: enable=too-many-instance-attributes


@dataclass
class EventFrame:
    events: dict[EventCategory, list[Event]] = field(default_factory=dict)

    def add(self, event: Event) -> None:
        self.events.setdefault(event.category, []).append(event)

    def get(self, category: EventCategory) -> list[Event]:
        return self.events.get(category, [])
