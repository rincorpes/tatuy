"""
Input port implementation for the pygame backend.
Provides functionality to poll and map input events.
"""

# Justification: Disabling no-member checks for pygame attributes since they are
# dynamically added after initialization.
# pylint: disable=no-member

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, FrozenSet, Tuple

from tatuy.input.keys import Key


@dataclass(frozen=True)
class ButtonState:
    """
    State of a single action button.
    """

    down: bool
    pressed: bool
    released: bool

    def to_dict(self) -> Dict[str, bool]:
        """
        Convert the ButtonState to a dictionary.
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, bool]) -> ButtonState:
        """
        Create a ButtonState from a dictionary.
        """
        return cls(
            down=data.get("down", False),
            pressed=data.get("pressed", False),
            released=data.get("released", False),
        )


@dataclass(frozen=True)
class InputFrame:
    """
    Snapshot of input state for a single frame.
    """

    # Physical keys (device-level snapshot) – supports cheats & replay
    keys_down: FrozenSet[Key] = frozenset()
    keys_pressed: FrozenSet[Key] = frozenset()
    keys_released: FrozenSet[Key] = frozenset()

    # action buttons (jump, confirm, pause, etc.)
    buttons: Dict[str, ButtonState] = field(default_factory=dict)
    # axes (move_y, aim_x, etc.)
    axes: Dict[str, float] = field(default_factory=dict)
    # optional: pass through for UI needs
    mouse_pos: Tuple[int, int] = (0, 0)
    mouse_delta: Tuple[int, int] = (0, 0)
    mouse_inside: bool = False

    text_input: str = ""

    def is_down(self, key: Key) -> bool:
        return key in self.keys_down

    def is_pressed(self, key: Key) -> bool:
        return key in self.keys_pressed

    def to_dict(self) -> Dict[str, object]:
        """
        Convert the InputFrame to a dictionary.
        """
        data = asdict(self)

        # Convert ButtonState objects to dicts
        data["buttons"] = {
            name: state.to_dict() for name, state in self.buttons.items()
        }

        # Convert FrozenSet to list for serialization
        data["keys_down"] = [k.value for k in self.keys_down]
        data["keys_pressed"] = [k.value for k in self.keys_pressed]
        data["keys_released"] = [k.value for k in self.keys_released]
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> InputFrame:
        """
        Create an InputFrame from a dictionary.
        """
        return cls(
            keys_down=frozenset(Key(v) for v in data.get("keys_down", [])),
            keys_pressed=frozenset(
                Key(v) for v in data.get("keys_pressed", [])
            ),
            keys_released=frozenset(
                Key(v) for v in data.get("keys_released", [])
            ),
            buttons={
                name: ButtonState.from_dict(state)
                for name, state in data.get("buttons", {}).items()
            },
            axes=data.get("axes", {}),
            mouse_pos=tuple(data.get("mouse_pos", (0, 0))),
            mouse_delta=tuple(data.get("mouse_delta", (0, 0))),
            mouse_inside=bool(data.get("mouse_inside", False)),
            text_input=data.get("text_input", ""),
        )
