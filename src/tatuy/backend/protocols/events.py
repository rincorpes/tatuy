from __future__ import annotations

from typing import Protocol

from tatuy.backend.config import EventsConfig
from tatuy.events import Event


class Events(Protocol):
    """
    Interface for input operations.
    """

    config: EventsConfig

    def get_events(self) -> list[Event]: ...
