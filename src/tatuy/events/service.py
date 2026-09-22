from __future__ import annotations

from tatuy.backend.backend import Backend
from tatuy.events import EventFrame


class EventsService:
    """Collect a batch of normalized backend events."""

    def __init__(self, backend: Backend):
        self._backend = backend

    def get_event_frame(self) -> EventFrame:
        event_frame = EventFrame()

        for event in self._backend.events.get_events():
            event_frame.add(event)

        return event_frame
