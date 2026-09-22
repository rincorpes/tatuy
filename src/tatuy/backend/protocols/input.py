from __future__ import annotations

from typing import Protocol

from tatuy.backend.config import InputConfig
from tatuy.input.pointer import Cursor, PointerState


class Input(Protocol):
    """Backend operations for observing input devices."""

    config: InputConfig

    def get_pointer_state(self) -> PointerState: ...
    def set_cursor(self, cursor: Cursor): ...
