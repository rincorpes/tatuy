from __future__ import annotations

# pygame exposes some attributes dynamically.
# pylint: disable=no-member
import pygame

from tatuy.backend.backend_component import BackendComponent
from tatuy.backend.pygame.config import PygameInputConfig
from tatuy.input.pointer import Cursor, PointerState


class PygameInput(BackendComponent[PygameInputConfig]):
    """Observe input devices through pygame."""

    def __init__(self, config: PygameInputConfig):
        super().__init__(config)
        self._cursor: Cursor | None = None

    def get_pointer_state(self) -> PointerState:
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
        if cursor == self._cursor:
            return

        cursor_types = {
            Cursor.ARROW: pygame.SYSTEM_CURSOR_ARROW,
            Cursor.HAND: pygame.SYSTEM_CURSOR_HAND,
            Cursor.TEXT: pygame.SYSTEM_CURSOR_IBEAM,
        }

        pygame.mouse.set_cursor(pygame.cursors.Cursor(cursor_types[cursor]))
        self._cursor = cursor
