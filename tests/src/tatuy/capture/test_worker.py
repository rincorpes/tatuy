"""Worker output bytes match the requested image format."""

import pytest
from PIL import Image

from tatuy.capture.models import CaptureJob, WorkerConfig
from tatuy.capture.worker import CaptureWorker


@pytest.mark.parametrize("image_format", ["PNG", "BMP"])
def test_worker_writes_requested_format(tmp_path, image_format):
    results = []
    worker = CaptureWorker(WorkerConfig(on_done=results.append))
    path = tmp_path / ("frame." + image_format.lower())
    job = CaptureJob(
        "test",
        path,
        w=1,
        h=1,
        pixels=bytes((0, 0, 255, 255)),
        image_format=image_format,
    )
    worker._q.put(job)
    worker._process_job(job)
    assert results[0].ok
    with Image.open(path) as image:
        assert image.format == image_format
        assert image.convert("RGB").getpixel((0, 0)) == (255, 0, 0)
    assert not path.with_name(path.name + ".tmp").exists()


def test_worker_reports_missing_pillow(monkeypatch, tmp_path):
    results = []
    worker = CaptureWorker(WorkerConfig(on_done=results.append))
    path = tmp_path / "frame.png"
    job = CaptureJob(
        "test",
        path,
        w=1,
        h=1,
        pixels=bytes((0, 0, 255, 255)),
        image_format="PNG",
    )

    def missing_pillow(_name):
        raise ModuleNotFoundError("No module named 'PIL'", name="PIL")

    monkeypatch.setattr("tatuy.capture.worker.import_module", missing_pillow)
    worker._q.put(job)
    worker._process_job(job)

    assert not results[0].ok
    assert "Image capture requires Pillow" in results[0].error
    assert not path.exists()
