from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Union


@dataclass(frozen=True)
class PointerState:
    """
    Current pointer observation.
    Coordinates are in window space, before viewport transformation.
    """

    position: tuple[int, int] = (0, 0)
    inside: bool = False

    def to_dict(self) -> dict[str, Union[tuple[int, int], bool]]:
        return asdict(self)


class Cursor(str, Enum):
    ARROW = "arrow"
    HAND = "hand"
    TEXT = "text"
