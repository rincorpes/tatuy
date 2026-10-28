"""Frame input coordination."""

from __future__ import annotations

from tatuy.engine.runtime.services import RuntimeServices
from tatuy.events import EventCategory
from tatuy.input.frame import InputFrame
from tatuy.tooling.profiler import profiler


class FrameInputCollector:
    """Collect backend events and produce one input frame."""

    def __init__(self, services: RuntimeServices) -> None:
        self._services = services

    def collect(self) -> InputFrame:
        """Synchronize window and input events for the current frame."""
        with profiler.span("get_frame", "events"):
            events = self._services.events.get_event_frame()

        with profiler.span("window.sync", "events"):
            self._services.window.sync_events(events.get(EventCategory.WINDOW))
            self._services.viewport.resize(self._services.window.size)

        with profiler.span("input.sync", "events"):
            self._services.input.sync_events(
                events.get(EventCategory.INPUT),
                focused=self._services.window.focused,
            )

        return self._services.input.get_input_frame()
