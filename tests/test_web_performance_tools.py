"""Pure helpers behind browser performance diagnostics stay deterministic."""

from __future__ import annotations

from pathlib import Path

import scripts.measure_web_performance as metrics


def test_percentile_handles_empty_and_ordered_values() -> None:
    assert metrics._percentile([], 0.95) == 0.0
    assert metrics._percentile([30.0, 10.0, 20.0], 0.0) == 10.0
    assert metrics._percentile([30.0, 10.0, 20.0], 1.0) == 30.0
    assert metrics._percentile([10.0, 20.0, 30.0, 40.0], 0.95) == 40.0


def test_bundle_bytes_sums_generated_bundle_files(
    tmp_path: Path,
    monkeypatch,
) -> None:
    web_root = tmp_path / "web"
    bundle = web_root / "play" / "demo"
    bundle.mkdir(parents=True)
    (bundle / "index.html").write_bytes(b"1234")
    (bundle / "archive.bin").write_bytes(b"123456")
    monkeypatch.setattr(metrics, "WEB_ROOT", web_root)

    assert metrics._bundle_bytes("demo") == 10
