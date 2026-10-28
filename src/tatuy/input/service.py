from __future__ import annotations

from tatuy.backend.backend import Backend
from tatuy.events import Event, EventType
from tatuy.graphics.viewport.service import ViewportService
from tatuy.input.frame import ButtonState, InputFrame
from tatuy.input.keys import Key
from tatuy.input.pointer import PointerState


class InputService:
    """Maintain input state and publish a snapshot for each engine step."""

    def __init__(
        self,
        backend: Backend,
        viewport: ViewportService | None = None,
    ):
        # Backend components are created during backend.init().
        # Keep the backend reference and resolve input when needed.
        self._backend = backend
        self._viewport = viewport

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

    def sync_events(
        self, events: list[Event], *, focused: bool = True
    ) -> None:
        """Advance input state once, including frames with no events."""
        if not self._backend.initialized:
            return
        config = self._backend.config.input
        if not config.enable_keyboard:
            self._keys_down.clear()
        if not config.enable_mouse:
            self._mouse_down.clear()
            self._mouse_pos = (0, 0)
            self._mouse_inside = False
        keys_pressed: set[Key] = set()
        keys_released: set[Key] = set()

        mouse_pressed: set[int] = set()
        mouse_released: set[int] = set()

        axes: dict[str, float] = {}
        text_parts: list[str] = []

        mouse_dx = 0
        mouse_dy = 0

        if not focused:
            keys_released.update(self._keys_down)
            mouse_released.update(self._mouse_down)
            self._keys_down.clear()
            self._mouse_down.clear()
            self._mouse_inside = False
            self._frame = InputFrame(
                keys_released=frozenset(keys_released),
                buttons={
                    f"mouse_{button}": ButtonState(
                        down=False,
                        pressed=False,
                        released=True,
                    )
                    for button in mouse_released
                },
                mouse_pos=self._mouse_pos,
                mouse_inside=False,
                focused=False,
            )
            return

        for event in events:
            keyboard = event.type in (
                EventType.KEYDOWN,
                EventType.KEYUP,
                EventType.TEXTINPUT,
            )
            if keyboard and not config.enable_keyboard:
                continue
            if not keyboard and not config.enable_mouse:
                continue
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

        pointer = (
            self._backend.input.get_pointer_state()
            if config.enable_mouse
            else PointerState()
        )

        pointer_inside = pointer.inside
        pointer_position = pointer.position
        if pointer_inside and self._viewport is not None:
            pointer_inside = self._viewport.contains_window_point(*pointer.position)
            if pointer_inside:
                pointer_position = self._viewport.window_to_virtual(*pointer.position)

        previous_mouse_pos = self._mouse_pos
        if pointer_inside:
            self._mouse_pos = pointer_position
            if self._mouse_inside:
                mouse_dx = self._mouse_pos[0] - previous_mouse_pos[0]
                mouse_dy = self._mouse_pos[1] - previous_mouse_pos[1]

        # Preserve the current policy: suppress relative movement when
        # outside the viewport and during the first frame back inside.
        if not pointer_inside or not self._mouse_inside:
            mouse_dx = 0
            mouse_dy = 0

        self._mouse_inside = pointer_inside

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
