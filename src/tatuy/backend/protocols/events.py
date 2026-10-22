"""Contract for collecting normalized Tatuy platform events."""

from __future__ import annotations

from typing import Protocol

from tatuy.backend.config import EventsConfig
from tatuy.events import Event


class Events(Protocol):
    """Collect supported platform events as normalized Tatuy events.

    Attributes:
        config (EventsConfig): Settings for this capability.
    """

    config: EventsConfig

    def get_events(self) -> list[Event]:
        """Drain supported platform events into ordered, normalized Tatuy events.

        Returns:
            list[Event]: Supported events in platform queue order.
        """
