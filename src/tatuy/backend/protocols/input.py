"""Contract for pointer observation and system cursor selection."""

from __future__ import annotations

from typing import Protocol

from tatuy.backend.config import InputConfig
from tatuy.input.pointer import Cursor, PointerState


class Input(Protocol):
    """Observe the pointer and change the cursor without exposing native devices.

    Attributes:
        config (InputConfig): Settings for this capability.
    """

    config: InputConfig

    def get_pointer_state(self) -> PointerState:
        """Return pointer position in window coordinates and whether it is inside.

        Returns:
            PointerState: Pointer position and whether it lies inside the
                focused display; the default state when mouse input is
                disabled.
        """

    def set_cursor(self, cursor: Cursor):
        """Select the requested system cursor for enabled mouse input.

        Args:
            cursor (Cursor): System cursor to select.

        Returns:
            None: This method does not return a value.
        """
