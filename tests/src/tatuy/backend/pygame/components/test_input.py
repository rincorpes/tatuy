"""Pointer bounds and cursor caching."""

from unittest.mock import Mock

import pygame
import pytest

from tatuy.backend.pygame.components import input as module
from tatuy.backend.pygame.config import PygameInputConfig
from tatuy.input.pointer import Cursor


@pytest.mark.parametrize(
    "position,focused,has_surface,inside",
    [
        ((0, 0), True, True, True),
        ((9, 9), True, True, True),
        ((10, 0), True, True, False),
        ((-1, 0), True, True, False),
        ((1, 1), False, True, False),
        ((1, 1), True, False, False),
    ],
)
def test_pointer_inside_requires_focus_and_surface(
    monkeypatch,
    position,
    focused,
    has_surface,
    inside,
):
    fake = Mock()
    fake.mouse.get_pos.return_value = position
    fake.mouse.get_focused.return_value = focused
    fake.display.get_surface.return_value = (
        pygame.Surface((10, 10)) if has_surface else None
    )
    monkeypatch.setattr(module, "pygame", fake)
    state = module.PygameInput(PygameInputConfig()).get_pointer_state()
    assert state.position == position
    assert state.inside is inside


def test_cursor_only_updates_when_changed(monkeypatch):
    setter = Mock()
    monkeypatch.setattr(module.pygame.mouse, "set_cursor", setter)
    input_port = module.PygameInput(PygameInputConfig())
    input_port.set_cursor(Cursor.HAND)
    input_port.set_cursor(Cursor.HAND)
    input_port.set_cursor(Cursor.ARROW)
    assert setter.call_count == 2


def test_disabled_mouse_never_touches_platform(monkeypatch):
    fake = Mock()
    monkeypatch.setattr(module, "pygame", fake)
    port = module.PygameInput(PygameInputConfig(enable_mouse=False))
    state = port.get_pointer_state()
    port.set_cursor(Cursor.HAND)
    assert state.position == (0, 0) and state.inside is False
    assert fake.mock_calls == []


def test_gamepad_mode_is_explicitly_unsupported():
    with pytest.raises(NotImplementedError, match="gamepad"):
        module.PygameInput(PygameInputConfig(enable_gamepad=True))
