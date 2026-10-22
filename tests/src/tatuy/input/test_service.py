"""Device flags govern snapshots, including cached held state."""

from dataclasses import replace
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from tatuy.backend.config import InputConfig
from tatuy.events import Event, EventCategory, EventType
from tatuy.input.keys import Key
from tatuy.input.pointer import PointerState
from tatuy.input.service import InputService


def event(kind, attrs):
    return Event(EventCategory.INPUT, kind, kind.name.lower(), attrs)


@pytest.mark.parametrize(
    "keyboard,mouse", [(False, True), (True, False), (False, False)]
)
def test_flags_filter_snapshot_and_polling(keyboard, mouse):
    port = Mock()
    port.get_pointer_state.return_value = PointerState((3, 4), True)
    backend = SimpleNamespace(
        initialized=True,
        input=port,
        config=SimpleNamespace(
            input=InputConfig(enable_keyboard=keyboard, enable_mouse=mouse)
        ),
    )
    service = InputService(backend)
    service.sync_events(
        [
            event(EventType.KEYDOWN, {"key": Key.A}),
            event(EventType.TEXTINPUT, {"text": "a"}),
            event(EventType.MOUSEBUTTONDOWN, {"button": 1, "pos": (3, 4)}),
            event(EventType.MOUSEWHEEL, {"x": 0, "y": 1}),
        ]
    )
    frame = service.get_input_frame()
    assert (Key.A in frame.keys_down) is keyboard
    assert frame.text_input == ("a" if keyboard else "")
    assert bool(frame.buttons) is mouse
    assert bool(frame.axes) is mouse
    assert port.get_pointer_state.call_count == int(mouse)


def test_disabling_devices_clears_held_state():
    port = Mock()
    port.get_pointer_state.return_value = PointerState((3, 4), True)
    backend = SimpleNamespace(
        initialized=True,
        input=port,
        config=SimpleNamespace(input=InputConfig()),
    )
    service = InputService(backend)
    service.sync_events(
        [
            event(EventType.KEYDOWN, {"key": Key.A}),
            event(EventType.MOUSEBUTTONDOWN, {"button": 1, "pos": (3, 4)}),
        ]
    )
    backend.config.input = replace(
        backend.config.input, enable_keyboard=False, enable_mouse=False
    )
    service.sync_events([])
    frame = service.get_input_frame()
    assert (
        not frame.keys_down and not frame.keys_released and not frame.buttons
    )
    assert not frame.mouse_inside and frame.mouse_pos == (0, 0)
