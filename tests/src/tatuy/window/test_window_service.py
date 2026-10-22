"""Native resize notifications observe rather than request display changes."""

from types import SimpleNamespace
from unittest.mock import Mock

from tatuy.events import Event, EventCategory, EventType
from tatuy.geometry.size import Size
from tatuy.window import service as module


def test_native_resize_retains_previous_size(monkeypatch):
    window = Mock(size=Size(320, 240))
    bus = Mock()
    monkeypatch.setattr(module, "event_bus", bus)
    service = module.WindowService(
        SimpleNamespace(initialized=True, window=window)
    )
    service.open()
    window.size = Size(400, 300)
    event = Event(
        EventCategory.WINDOW,
        EventType.WINDOWSIZECHANGED,
        "windowsizechanged",
        {"x": 400, "y": 300},
    )
    service.sync_events([event, event])
    window.resize.assert_not_called()
    assert window.sync_size.call_count == 2
    assert bus.emit.call_args_list[0].kwargs["data"] == {
        "old_size": (320, 240),
        "size": (400, 300),
    }
