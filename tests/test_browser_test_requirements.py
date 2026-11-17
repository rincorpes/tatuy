"""Regression tests for explicit and optional Playwright dependency handling."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def browser_pytest_project(tmp_path: Path) -> Path:
    """Make a miniature test suite with Playwright deliberately unavailable.

    Args:
        tmp_path: Isolated pytest temporary directory.

    Returns:
        A temporary project containing the real browser test and conftest hook.
    """
    browser = tmp_path / "tests" / "browser"
    browser.mkdir(parents=True)
    for filename in ("conftest.py", "test_browser_smoke.py"):
        shutil.copyfile(
            PROJECT_ROOT / "tests" / "browser" / filename,
            browser / filename,
        )
    (tmp_path / "tests" / "test_unit.py").write_text(
        "def test_unit():\n    assert True\n", encoding="utf-8"
    )
    # Shadow any globally installed Playwright to enforce missing sync_api.
    fake_playwright = tmp_path / "playwright"
    fake_playwright.mkdir()
    (fake_playwright / "__init__.py").write_text(
        '"""Playwright stub without sync_api."""\n', encoding="utf-8"
    )
    return tmp_path


def _run_pytest(
    project: Path, target: str
) -> subprocess.CompletedProcess[str]:
    """Run isolated pytest with the fake missing-Playwright package.

    Args:
        project: Miniature test project and stub package location.
        target: Positional pytest test target.

    Returns:
        Subprocess result, including exit code and bounded diagnostics.
    """
    environment = os.environ.copy()
    environment["PYTHONPATH"] = (
        str(project) + os.pathsep + environment.get("PYTHONPATH", "")
    )
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-q", target],
        cwd=project,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )


@pytest.mark.parametrize(
    "target", ["tests/browser/test_browser_smoke.py", "tests/browser"]
)
def test_explicit_browser_selection_reports_install_steps(
    browser_pytest_project: Path, target: str
) -> None:
    """Explicit browser targets must fail clearly instead of silently skipping."""
    result = _run_pytest(browser_pytest_project, target)

    assert result.returncode == 4
    combined = result.stdout + result.stderr
    assert "Playwright is required for Tatuy browser smoke tests" in combined
    assert "python -m pip install playwright" in combined
    assert "python -m playwright install chromium" in combined
    assert "python -m pytest tests/browser/test_browser_smoke.py" in combined


def test_general_suite_keeps_optional_browser_skip(
    browser_pytest_project: Path,
) -> None:
    """Whole-suite collection should not fail when Playwright is optional."""
    result = _run_pytest(browser_pytest_project, "tests")

    assert result.returncode == 0, result.stdout + result.stderr
    assert "1 passed" in result.stdout
    assert "1 skipped" in result.stdout
