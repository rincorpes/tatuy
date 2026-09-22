from __future__ import annotations

from tatuy.backend.backend import Backend
from tatuy.events import Event, EventType
from tatuy.input.frame import ButtonState, InputFrame
from tatuy.input.keys import Key


class InputService:
    """Maintain input state and publish a snapshot for each engine step."""

    def __init__(self, backend: Backend):
        # Backend components are created during backend.init().
        # Keep the backend reference and resolve input when needed.
        self._backend = backend

        self._keys_down: set[Key] = set()
        self._mouse_down: set[int] = set()
        self._mouse_pos: tuple[int, int] = (0, 0)
        self._mouse_inside = False
        self._frame = InputFrame()

    def reset(self) -> None:
        """Clear state when starting a new runtime session."""
        self._keys_down.clear()
        self._mouse_down.clear()
        self._mouse_pos = (0, 0)
        self._mouse_inside = False
        self._frame = InputFrame()

    def sync_events(self, events: list[Event]) -> None:
        """Advance input state once, including frames with no events."""
        if not self._backend.initialized:
            return
        keys_pressed: set[Key] = set()
        keys_released: set[Key] = set()

        mouse_pressed: set[int] = set()
        mouse_released: set[int] = set()

        axes: dict[str, float] = {}
        text_parts: list[str] = []

        mouse_dx = 0
        mouse_dy = 0

        for event in events:
            attrs = event.attrs

            match event.type:
                case EventType.KEYDOWN:
                    key = attrs["key"]

                    if key not in self._keys_down:
                        keys_pressed.add(key)

                    self._keys_down.add(key)

                case EventType.KEYUP:
                    key = attrs["key"]

                    if key in self._keys_down:
                        self._keys_down.remove(key)
                        keys_released.add(key)

                case EventType.TEXTINPUT:
                    text_parts.append(attrs["text"])

                case EventType.MOUSEMOTION:
                    x, y = attrs["pos"]
                    self._mouse_pos = (x, y)

                    dx, dy = attrs["rel"]
                    mouse_dx += dx
                    mouse_dy += dy

                case EventType.MOUSEBUTTONDOWN:
                    x, y = attrs["pos"]
                    self._mouse_pos = (x, y)

                    button = attrs["button"]

                    if button not in self._mouse_down:
                        mouse_pressed.add(button)

                    self._mouse_down.add(button)

                case EventType.MOUSEBUTTONUP:
                    x, y = attrs["pos"]
                    self._mouse_pos = (x, y)

                    button = attrs["button"]

                    if button in self._mouse_down:
                        self._mouse_down.remove(button)
                        mouse_released.add(button)

                case EventType.MOUSEWHEEL:
                    axes["wheel_x"] = axes.get("wheel_x", 0.0) + attrs["x"]
                    axes["wheel_y"] = axes.get("wheel_y", 0.0) + attrs["y"]

        pointer = self._backend.input.get_pointer_state()

        if pointer.inside:
            self._mouse_pos = pointer.position

        # Preserve the current policy: suppress relative movement when
        # outside the window and during the first frame back inside.
        if not pointer.inside or not self._mouse_inside:
            mouse_dx = 0
            mouse_dy = 0

        self._mouse_inside = pointer.inside

        observed_buttons = self._mouse_down | mouse_pressed | mouse_released

        buttons = {
            f"mouse_{button}": ButtonState(
                down=button in self._mouse_down,
                pressed=button in mouse_pressed,
                released=button in mouse_released,
            )
            for button in observed_buttons
        }

        self._frame = InputFrame(
            keys_down=frozenset(self._keys_down),
            keys_pressed=frozenset(keys_pressed),
            keys_released=frozenset(keys_released),
            buttons=buttons,
            axes=axes,
            mouse_pos=self._mouse_pos,
            mouse_delta=(mouse_dx, mouse_dy),
            mouse_inside=self._mouse_inside,
            text_input="".join(text_parts),
        )

    def get_input_frame(self) -> InputFrame:
        """Return the latest snapshot without advancing input state."""
        return self._frame
