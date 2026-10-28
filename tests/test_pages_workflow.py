"""GitHub Pages workflow keeps the showcase build reproducible and metadata-driven."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = PROJECT_ROOT / ".github" / "workflows" / "pages.yml"


def test_pages_workflow_builds_from_showcase_metadata_before_deploy() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    expected_steps = [
        "scripts/build_showcase.py",
        "tests/browser/test_browser_smoke.py",
        "scripts/capture_showcase_thumbnails.py",
        "scripts/build_showcase_site.py",
        "scripts/validate_web_output.py",
        "actions/upload-pages-artifact@v4",
        "actions/configure-pages@v5",
        "actions/deploy-pages@v4",
    ]
    positions = [text.index(step) for step in expected_steps]

    assert positions == sorted(positions)
    assert 'PLAYWRIGHT_VERSION: "1.64.1"' in text
    assert 'python -m pip install "poetry==2.3.4"' in text
    assert "python -m playwright install --with-deps chromium" in text
    assert "path: build/web" in text
    assert "github.event_name != 'pull_request'" in text
    assert "pages: write" in text
    assert "id-token: write" in text
