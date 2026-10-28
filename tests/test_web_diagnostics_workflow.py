"""Manual web diagnostics keep compatibility and performance evidence reproducible."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = PROJECT_ROOT / ".github" / "workflows" / "web-diagnostics.yml"


def test_web_diagnostics_cover_desktop_browsers_and_pressure_metrics() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "workflow_dispatch" in text
    assert "- chromium" in text
    assert "- firefox" in text
    assert "- webkit" in text
    assert 'TATUY_BROWSER: "${{ matrix.browser }}"' in text
    assert "tests/browser/test_browser_smoke.py" in text
    assert "examples/experiments/002_entities" in text
    assert "scripts/measure_web_performance.py" in text
    assert "actions/upload-artifact@v4" in text
    assert "build/diagnostics/web-performance.json" in text
