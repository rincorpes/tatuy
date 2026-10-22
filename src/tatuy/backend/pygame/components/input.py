"""Observe Pygame pointer state and select cached system cursors."""

from __future__ import annotations

# pygame exposes some attributes dynamically.
# pylint: disable=no-member
import pygame

from tatuy.backend.backend_component import BackendComponent
from tatuy.backend.pygame.config import PygameInputConfig
from tatuy.input.pointer import Cursor, PointerState


class PygameInput(BackendComponent[PygameInputConfig]):
    """Observe enabled mouse input and cache successful native cursor selections.

    Args:
        config (PygameInputConfig): Settings used to configure this
            capability.

    Raises:
        NotImplementedError: Gamepad input is requested.
    """

    def __init__(self, config: PygameInputConfig):
        super().__init__(config)
        if config.enable_gamepad:
            raise NotImplementedError("Pygame gamepad input is not supported")
        self._cursor: Cursor | None = None

    def get_pointer_state(self) -> PointerState:
        """Observe pointer position and focus within the current display bounds.

        Return a neutral state without native calls when mouse input is disabled.

        Returns:
            PointerState: Pointer position and whether it lies inside the
                focused display; the default state when mouse input is
                disabled.

        Raises:
            pygame.error: A required native subsystem is unavailable or the
                platform operation fails.
        """
        if not self.config.enable_mouse:
            return PointerState()
        position = pygame.mouse.get_pos()
        surface = pygame.display.get_surface()

        inside = (
            surface is not None
            and pygame.mouse.get_focused()
            and surface.get_rect().collidepoint(position)
        )

        return PointerState(
            position=(int(position[0]), int(position[1])),
            inside=bool(inside),
        )

    def set_cursor(self, cursor: Cursor) -> None:
        """Select and cache an enabled system cursor; failed selections are not cached.

        Args:
            cursor (Cursor): System cursor to select.

        Returns:
            None: This method does not return a value.

        Raises:
            pygame.error: A required native subsystem is unavailable or the
                platform operation fails.
        """
        if not self.config.enable_mouse:
            return
        if cursor == self._cursor:
            return

        cursor_types = {
            Cursor.ARROW: pygame.SYSTEM_CURSOR_ARROW,
            Cursor.HAND: pygame.SYSTEM_CURSOR_HAND,
            Cursor.TEXT: pygame.SYSTEM_CURSOR_IBEAM,
        }

        pygame.mouse.set_cursor(pygame.cursors.Cursor(cursor_types[cursor]))
        self._cursor = cursor
