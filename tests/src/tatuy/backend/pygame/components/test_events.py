"""Public event polling translates only supported Tatuy events."""

from unittest.mock import Mock

import pygame
import pytest

from tatuy.backend.pygame.components import events as module
from tatuy.backend.pygame.config import PygameEventsConfig
from tatuy.events import EventCategory, EventType
from tatuy.input.keys import Key


@pytest.mark.parametrize(
    "native,attrs,event_type,expected",
    [
        (
            pygame.KEYDOWN,
            {"key": pygame.K_a, "mod": 3},
            EventType.KEYDOWN,
            {"key": Key.A},
        ),
        (
            pygame.KEYUP,
            {"key": pygame.K_F12},
            EventType.KEYUP,
            {"key": Key.F12},
        ),
        (
            pygame.TEXTINPUT,
            {"text": "hello"},
            EventType.TEXTINPUT,
            {"text": "hello"},
        ),
        (
            pygame.MOUSEMOTION,
            {"pos": (3, 4), "rel": (-1, 2)},
            EventType.MOUSEMOTION,
            {"pos": (3, 4), "rel": (-1, 2)},
        ),
        (
            pygame.MOUSEBUTTONDOWN,
            {"button": 1, "pos": (3, 4)},
            EventType.MOUSEBUTTONDOWN,
            {"button": 1, "pos": (3, 4)},
        ),
        (
            pygame.MOUSEBUTTONUP,
            {"button": 1, "pos": (3, 4)},
            EventType.MOUSEBUTTONUP,
            {"button": 1, "pos": (3, 4)},
        ),
        (
            pygame.MOUSEWHEEL,
            {"x": -1, "y": 2},
            EventType.MOUSEWHEEL,
            {"x": -1.0, "y": 2.0},
        ),
        (
            pygame.WINDOWRESIZED,
            {"x": 640, "y": 480},
            EventType.WINDOWRESIZED,
            {"x": 640, "y": 480},
        ),
        (pygame.QUIT, {}, EventType.QUIT, {}),
    ],
)
def test_poll_translates_event(
    monkeypatch, native, attrs, event_type, expected
):
    event = pygame.event.Event(native, attrs)
    monkeypatch.setattr(module.pygame.event, "get", Mock(return_value=[event]))
    result = module.PygameEvents(PygameEventsConfig()).get_events()
    assert len(result) == 1
    assert result[0].type == event_type
    assert result[0].attrs == expected
    assert result[0].type_name == event_type.name.lower()
    category = (
        EventCategory.WINDOW
        if native
        in (
            pygame.WINDOWRESIZED,
            pygame.QUIT,
        )
        else EventCategory.INPUT
    )
    assert result[0].category == category


def test_unknown_events_and_keys_are_ignored(monkeypatch):
    native = [
        pygame.event.Event(pygame.USEREVENT, {}),
        pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_LSHIFT}),
    ]
    monkeypatch.setattr(module.pygame.event, "get", Mock(return_value=native))
    assert module.PygameEvents(PygameEventsConfig()).get_events() == []
