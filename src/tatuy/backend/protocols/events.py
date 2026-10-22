"""Contract for collecting normalized Tatuy platform events."""

from __future__ import annotations

from typing import Protocol

from tatuy.backend.config import EventsConfig
from tatuy.events import Event


class Events(Protocol):
    """Collect supported platform events as normalized Tatuy events.

    Attributes:
        config (EventsConfig): Read-only settings for this capability.
    """

    @property
    def config(self) -> EventsConfig:
        """Return the configuration without exposing reference reassignment.

        Returns:
            EventsConfig: Read-only configuration reference for this capability.
        """

    def get_events(self) -> list[Event]:
        """Drain supported platform events into ordered, normalized Tatuy events.

        Returns:
            list[Event]: Supported events in platform queue order.
        """
