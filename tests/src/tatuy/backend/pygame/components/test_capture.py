"""Capture byte order and file forwarding."""

from unittest.mock import Mock

import pytest

from tatuy.backend.pygame.components import capture as module
from tatuy.backend.pygame.config import PygameCaptureConfig


def test_capture_returns_bgra_bytes(render_target):
    render_target.screen.set_at((0, 0), (10, 20, 30, 40))
    capture = module.PygameCapture(
        PygameCaptureConfig(),
        render_target.window,
    )
    width, height, data = capture.bgra8888_bytes()
    assert (width, height) == (40, 40)
    assert len(data) == width * height * 4
    assert data[:4] == bytes((30, 20, 10, 40))


def test_capture_empty_path_and_save_forwarding(monkeypatch, render_target):
    save = Mock()
    monkeypatch.setattr(module.pygame.image, "save", save)
    capture = module.PygameCapture(
        PygameCaptureConfig(),
        render_target.window,
    )
    assert capture.bmp("") is False
    save.assert_not_called()
    assert capture.bmp("frame.bmp") is True
    save.assert_called_once_with(render_target.screen, "frame.bmp")


@pytest.mark.xfail(strict=True, reason="B04: concrete capture requires path")
def test_capture_accepts_protocol_default_path(render_target):
    capture = module.PygameCapture(
        PygameCaptureConfig(),
        render_target.window,
    )
    assert capture.bmp() is False
