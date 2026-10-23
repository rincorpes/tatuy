"""Behavior tests for screen effects."""

import pytest

from tatuy.features.fx.screen import ScreenEffectStack
from tatuy.features.fx.screen_effects import FlashEffect


def test_flash_effect_fades_and_finishes() -> None:
    effect = FlashEffect(duration=1.0, color=(10, 20, 30), peak_alpha=200)

    start = effect.snapshot()
    assert len(start) == 1
    assert start[0].color == (10, 20, 30, 200)

    effect.update(0.5)
    middle = effect.snapshot()
    assert middle[0].color == (10, 20, 30, 100)

    effect.update(0.5)
    assert effect.finished
    assert effect.snapshot() == ()


def test_screen_effect_stack_replaces_convenience_flash() -> None:
    stack = ScreenEffectStack()
    stack.flash(duration=1.0, color=(255, 0, 0), peak_alpha=100)
    stack.flash(duration=2.0, color=(255, 0, 0), peak_alpha=50)

    assert len(stack.effects) == 1
    assert isinstance(stack.effects[0], FlashEffect)
    assert stack.effects[0].peak_alpha == 100


def test_screen_effect_stack_removes_finished_effects() -> None:
    stack = ScreenEffectStack()
    stack.flash(duration=0.25)

    stack.update(0.25)

    assert stack.effects == ()
    assert stack.snapshot() == ()


def test_screen_effect_stack_rejects_invalid_delta_time() -> None:
    stack = ScreenEffectStack()

    with pytest.raises(ValueError):
        stack.update(-0.1)
