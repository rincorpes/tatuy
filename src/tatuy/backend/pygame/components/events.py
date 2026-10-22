"""Translate supported Pygame events into portable Tatuy event payloads."""

from __future__ import annotations

from typing import Any

# pygame exposes some attributes dynamically.
# pylint: disable=no-member
import pygame

from tatuy.backend.backend_component import BackendComponent
from tatuy.backend.config import InputConfig
from tatuy.backend.pygame.config import PygameEventsConfig
from tatuy.events import Event, EventCategory, EventType
from tatuy.input.keys import Key
from tatuy.tooling.profiler import profiler

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


PYGAME_KEY_TO_KEY.update(
    {
        pygame.K_LSHIFT: Key.LSHIFT,
        pygame.K_RSHIFT: Key.RSHIFT,
        pygame.K_LCTRL: Key.LCTRL,
        pygame.K_RCTRL: Key.RCTRL,
        pygame.K_LALT: Key.LALT,
        pygame.K_RALT: Key.RALT,
        pygame.K_LGUI: Key.LGUI,
        pygame.K_RGUI: Key.RGUI,
        pygame.K_KP0: Key.KP_0,
        pygame.K_KP1: Key.KP_1,
        pygame.K_KP2: Key.KP_2,
        pygame.K_KP3: Key.KP_3,
        pygame.K_KP4: Key.KP_4,
        pygame.K_KP5: Key.KP_5,
        pygame.K_KP6: Key.KP_6,
        pygame.K_KP7: Key.KP_7,
        pygame.K_KP8: Key.KP_8,
        pygame.K_KP9: Key.KP_9,
        pygame.K_KP_ENTER: Key.KP_ENTER,
        pygame.K_KP_PLUS: Key.KP_PLUS,
        pygame.K_KP_MINUS: Key.KP_MINUS,
        pygame.K_KP_MULTIPLY: Key.KP_MULTIPLY,
        pygame.K_KP_DIVIDE: Key.KP_DIVIDE,
        pygame.K_KP_PERIOD: Key.KP_PERIOD,
        pygame.K_KP_EQUALS: Key.KP_EQUALS,
    }
)

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
    """Drain native events and emit only supported, normalized Tatuy payloads.

    Args:
        config (PygameEventsConfig): Settings used to configure this
            capability.
        input_config (InputConfig | None): Input filters, or None to use
            the shared input defaults.
    """

    def __init__(
        self,
        config: PygameEventsConfig,
        input_config: InputConfig | None = None,
    ):
        super().__init__(config)
        self._input_config = input_config or InputConfig()

    def get_events(self) -> list[Event]:
        """Drain the native queue and translate supported events in their original order.

        Apply keyboard and mouse enable flags without filtering window or quit
        events. Discard unsupported events and native-only payload values.

        Returns:
            list[Event]: Supported events in platform queue order.

        Raises:
            pygame.error: A required native subsystem is unavailable or the
                platform operation fails.
        """
        events: list[Event] = []

        with profiler.span("pygame.poll", "backend"):
            pygame_events = pygame.event.get()

        with profiler.span("pygame.map", "backend"):
            for pygame_event in pygame_events:
                mapping = _EVENT_MAP.get(pygame_event.type)

                if mapping is None:
                    continue

                category, event_type = mapping
                if category == EventCategory.INPUT:
                    keyboard = event_type in (
                        EventType.KEYDOWN,
                        EventType.KEYUP,
                        EventType.TEXTINPUT,
                    )
                    if keyboard and not self._input_config.enable_keyboard:
                        continue
                    if not keyboard and not self._input_config.enable_mouse:
                        continue
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
        """Normalize native event attributes, discarding unsupported keys.

        Args:
            event_type (EventType): Normalized event type whose native
                attributes are translated.
            attrs (dict[str, Any]): Native event attributes to normalize into
                portable values.

        Returns:
            dict[str, Any] | None: Portable attributes, or None when the event
                should be discarded.

        Raises:
            KeyError: Required native attributes are missing.
            TypeError: Native attributes cannot be converted to portable
                values.
            ValueError: A numeric native attribute is malformed.
        """
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

            case (
                EventType.WINDOWMOVED
                | EventType.WINDOWRESIZED
                | EventType.WINDOWSIZECHANGED
            ):
                return {"x": int(attrs["x"]), "y": int(attrs["y"])}
            case _:
                # Native window wrappers and other backend values stay private.
                return {}
