"""Capture workflow settings own screenshot filenames and formats."""

from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from tatuy.capture import service as module
from tatuy.capture.settings import CaptureSettings, CaptureSettingsBuilder


@pytest.mark.parametrize("image_format", ["png", "bmp"])
def test_screenshot_settings_reach_worker(monkeypatch, tmp_path, image_format):
    worker = Mock()
    monkeypatch.setattr(module, "CaptureWorker", Mock(return_value=worker))
    backend = SimpleNamespace(capture=Mock())
    backend.capture.bgra8888_bytes.return_value = (
        1,
        1,
        bytes((0, 0, 255, 255)),
    )
    service = module.CaptureService(
        backend,
        CaptureSettings(
            root_dir=str(tmp_path),
            screenshot_format=image_format,
            hotkeys_enabled=False,
        ),
    )
    path = service.request_screenshot("test")
    assert path.endswith("." + image_format)
    service.after_render()
    job = worker.enqueue.call_args.args[0]
    assert job.image_format == image_format.upper()
    assert str(job.out_path) == path
    service.close()


def test_unknown_format_rejected():
    with pytest.raises(ValueError, match="screenshot_format"):
        CaptureSettings(screenshot_format="jpeg")
    with pytest.raises(ValueError, match="screenshot_format"):
        CaptureSettingsBuilder().build({"screenshot_format": "jpeg"})
