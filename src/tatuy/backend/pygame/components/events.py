from __future__ import annotations

from typing import Any

# pygame exposes some attributes dynamically.
# pylint: disable=no-member
import pygame

from tatuy.backend.backend_component import BackendComponent
from tatuy.backend.pygame.config import PygameEventsConfig
from tatuy.events import Event, EventCategory, EventType
from tatuy.input.keys import Key

PYGAME_KEY_TO_KEY: dict[int, Key] = {
    pygame.K_ESCAPE: Key.ESCAPE,
    pygame.K_RETURN: Key.ENTER,
    pygame.K_SPACE: Key.SPACE,
    pygame.K_TAB: Key.TAB,
    pygame.K_BACKSPACE: Key.BACKSPACE,
    pygame.K_DELETE: Key.DELETE,
    pygame.K_UP: Key.UP,
    pygame.K_DOWN: Key.DOWN,
    pygame.K_LEFT: Key.LEFT,
    pygame.K_RIGHT: Key.RIGHT,
}

for letter in "abcdefghijklmnopqrstuvwxyz":
    PYGAME_KEY_TO_KEY[getattr(pygame, f"K_{letter}")] = Key[letter.upper()]

for number in range(10):
    PYGAME_KEY_TO_KEY[getattr(pygame, f"K_{number}")] = Key[f"NUM_{number}"]

for number in range(1, 13):
    PYGAME_KEY_TO_KEY[getattr(pygame, f"K_F{number}")] = Key[f"F{number}"]


_EVENT_MAP = {
    pygame.KEYDOWN: (EventCategory.INPUT, EventType.KEYDOWN),
    pygame.KEYUP: (EventCategory.INPUT, EventType.KEYUP),
    pygame.TEXTINPUT: (EventCategory.INPUT, EventType.TEXTINPUT),
    pygame.MOUSEMOTION: (EventCategory.INPUT, EventType.MOUSEMOTION),
    pygame.MOUSEBUTTONDOWN: (
        EventCategory.INPUT,
        EventType.MOUSEBUTTONDOWN,
    ),
    pygame.MOUSEBUTTONUP: (
        EventCategory.INPUT,
        EventType.MOUSEBUTTONUP,
    ),
    pygame.MOUSEWHEEL: (EventCategory.INPUT, EventType.MOUSEWHEEL),
    pygame.WINDOWMOVED: (
        EventCategory.WINDOW,
        EventType.WINDOWMOVED,
    ),
    pygame.WINDOWRESIZED: (
        EventCategory.WINDOW,
        EventType.WINDOWRESIZED,
    ),
    pygame.WINDOWSIZECHANGED: (
        EventCategory.WINDOW,
        EventType.WINDOWSIZECHANGED,
    ),
    pygame.QUIT: (EventCategory.WINDOW, EventType.QUIT),
    pygame.WINDOWMINIMIZED: (
        EventCategory.WINDOW,
        EventType.WINDOWMINIMIZED,
    ),
    pygame.WINDOWMAXIMIZED: (
        EventCategory.WINDOW,
        EventType.WINDOWMAXIMIZED,
    ),
    pygame.WINDOWRESTORED: (
        EventCategory.WINDOW,
        EventType.WINDOWRESTORED,
    ),
    pygame.WINDOWCLOSE: (
        EventCategory.WINDOW,
        EventType.WINDOWCLOSE,
    ),
}


class PygameEvents(BackendComponent[PygameEventsConfig]):
    """Collect pygame events and translate them into tatuy events."""

    def __init__(self, config: PygameEventsConfig):
        super().__init__(config)

    def get_events(self) -> list[Event]:
        events: list[Event] = []

        for pygame_event in pygame.event.get():
            mapping = _EVENT_MAP.get(pygame_event.type)

            if mapping is None:
                continue

            category, event_type = mapping
            attrs = self._translate_attrs(
                event_type,
                pygame_event.dict,
            )

            if attrs is None:
                continue

            events.append(
                Event(
                    category=category,
                    type=event_type,
                    type_name=event_type.name.lower(),
                    attrs=attrs,
                )
            )

        return events

    @staticmethod
    def _translate_attrs(
        event_type: EventType,
        attrs: dict[str, Any],
    ) -> dict[str, Any] | None:
        match event_type:
            case EventType.KEYDOWN | EventType.KEYUP:
                key = PYGAME_KEY_TO_KEY.get(attrs["key"])

                if key is None:
                    return None

                return {"key": key}

            case EventType.TEXTINPUT:
                return {"text": str(attrs["text"])}

            case EventType.MOUSEMOTION:
                x, y = attrs["pos"]
                dx, dy = attrs["rel"]

                return {
                    "pos": (int(x), int(y)),
                    "rel": (int(dx), int(dy)),
                }

            case EventType.MOUSEBUTTONDOWN | EventType.MOUSEBUTTONUP:
                x, y = attrs["pos"]

                return {
                    "button": int(attrs["button"]),
                    "pos": (int(x), int(y)),
                }

            case EventType.MOUSEWHEEL:
                return {
                    "x": float(attrs["x"]),
                    "y": float(attrs["y"]),
                }

            case _:
                # Preserve the existing window event payloads.
                return dict(attrs)
