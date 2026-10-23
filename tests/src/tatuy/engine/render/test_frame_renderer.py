"""Frame-render coordination ordering."""

from unittest.mock import Mock, call

from tatuy.engine.render.renderer import FrameRenderer


def test_frame_renderer_captures_between_content_and_presentation():
    events = Mock()
    backend = Mock()
    backend.initialized = True
    driver = Mock()
    viewport = Mock()
    window = Mock()
    capture = Mock()

    driver.render_frame_content.side_effect = lambda *_: events.content()
    capture.after_render.side_effect = lambda: events.capture()
    driver.present_frame.side_effect = lambda *_: events.present()

    FrameRenderer(
        backend,
        driver,
        viewport,
        window,
        capture,
    ).render([], 0.016)

    assert events.method_calls == [
        call.content(),
        call.capture(),
        call.present(),
    ]
