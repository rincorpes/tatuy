"""Frame input collection forwards portable window focus state."""

from types import SimpleNamespace
from unittest.mock import Mock

from tatuy.engine.frame_input import FrameInputCollector
from tatuy.events import EventFrame
from tatuy.input.frame import InputFrame


def test_collect_forwards_window_focus_to_input_service() -> None:
    events = Mock()
    events.get_event_frame.return_value = EventFrame()
    input_service = Mock()
    input_service.get_input_frame.return_value = InputFrame(focused=False)
    window = Mock(focused=False)
    window.size = object()
    viewport = Mock()
    services = SimpleNamespace(
        events=events,
        window=window,
        viewport=viewport,
        input=input_service,
    )

    frame = FrameInputCollector(services).collect()

    viewport.resize.assert_called_once_with(window.size)
    input_service.sync_events.assert_called_once_with([], focused=False)
    assert frame.focused is False
