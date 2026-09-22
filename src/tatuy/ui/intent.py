from __future__ import annotations

from dataclasses import dataclass

from tatuy.input.frame import InputFrame
from tatuy.scenes.context import Intent


@dataclass
class UiIntent(Intent):
    pointer_position: tuple[int, int] = (0, 0)
    pointer_inside: bool = False

    activate_down: bool = False
    activate_pressed: bool = False
    activate_released: bool = False

    def update_from(self, input_frame: InputFrame) -> None:
        self.pointer_position = input_frame.mouse_pos
        self.pointer_inside = input_frame.mouse_inside

        primary = input_frame.buttons.get("mouse_1")

        # Assign every field every update, including when there
        # is no mouse-button entry or this scene has no input.
        self.activate_down = primary.down if primary else False
        self.activate_pressed = primary.pressed if primary else False
        self.activate_released = primary.released if primary else False
