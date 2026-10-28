"""Input-frame helpers identify browser-safe activation gestures."""

from tatuy.input.frame import ButtonState, InputFrame
from tatuy.input.keys import Key


def test_user_gesture_requires_key_or_pointer_button_press() -> None:
    assert InputFrame().has_user_gesture() is False
    assert InputFrame(keys_down=frozenset({Key.A})).has_user_gesture() is False
    assert InputFrame(keys_pressed=frozenset({Key.A})).has_user_gesture() is True
    assert (
        InputFrame(
            buttons={"mouse_1": ButtonState(down=True, pressed=True, released=False)}
        ).has_user_gesture()
        is True
    )


def test_pointer_release_does_not_count_as_activation_gesture() -> None:
    frame = InputFrame(
        buttons={"mouse_1": ButtonState(down=False, pressed=False, released=True)}
    )

    assert frame.has_user_gesture() is False
