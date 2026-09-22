from __future__ import annotations

from tatuy.backend.backend import Backend
from tatuy.backend.protocols.window import Window
from tatuy.events import Event, EventType
from tatuy.events.bus import event_bus
from tatuy.geometry.size import Size
from tatuy.math.vec2 import Vec2


class WindowService:
    def __init__(self, backend: Backend):
        self._backend = backend

    @property
    def _window(self) -> Window:
        return self._backend.window

    @property
    def size(self) -> Size:
        if not self._backend.initialized:
            return Size(0, 0)
        return self._window.size

    def open(self) -> None:
        self._window.open()

    def sync_events(self, events: list[Event]):
        if not self._backend.initialized:
            return
        for event in events:
            match event.type:
                case EventType.QUIT:
                    event_bus.emit("quit")
                    return
                case EventType.WINDOWMOVED:
                    old_position = self._window.position
                    self._window.position = Vec2(
                        float(event.attrs.get("x", 0.0)),
                        float(event.attrs.get("y", 0.0)),
                    )
                    event_bus.emit(
                        event.type_name,
                        data={
                            "old_position": old_position.to_tuple(),
                            "position": self._window.position.to_tuple(),
                        },
                    )

                case EventType.WINDOWRESIZED | EventType.WINDOWSIZECHANGED:
                    old_size = self._window.size
                    self._window.resize(
                        event.attrs.get("x", 0), event.attrs.get("y", 0)
                    )
                    event_bus.emit(
                        event.type_name,
                        data={
                            "old_size": old_size.to_tuple(),
                            "size": self._window.size.to_tuple(),
                        },
                    )

                case EventType.WINDOWMINIMIZED:
                    self._window.minimized = True
                    self._window.maximized = False
                    event_bus.emit(
                        event.type_name,
                        data={
                            "minimized": self._window.minimized,
                            "maximized": self._window.maximized,
                        },
                    )

                case EventType.WINDOWMAXIMIZED:
                    self._window.maximized = True
                    self._window.minimized = False
                    event_bus.emit(
                        event.type_name,
                        data={
                            "minimized": self._window.minimized,
                            "maximized": self._window.maximized,
                        },
                    )

                case EventType.WINDOWRESTORED:
                    self._window.minimized = False
                    self._window.maximized = False
                    event_bus.emit(
                        event.type_name,
                        data={
                            "minimized": self._window.minimized,
                            "maximized": self._window.maximized,
                        },
                    )

                case EventType.WINDOWCLOSE:
                    self._window.close_requested = True
                    event_bus.emit(
                        event.type_name,
                        data={"close_requested": self._window.close_requested},
                    )
