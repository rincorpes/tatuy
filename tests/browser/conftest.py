"""Fail clearly when Tatuy browser smoke tests are requested without Playwright."""

from importlib.util import find_spec
from pathlib import Path

import pytest

_BROWSER_DIR = Path(__file__).resolve().parent


def _explicit_browser_selection(arguments: list[str]) -> bool:
    """Check whether pytest explicitly targets the browser test directory.

    Args:
        arguments: Resolved pytest positional test targets.

    Returns:
        Whether any target is this directory or a test below it.
    """
    for argument in arguments:
        path = Path(argument.split("::", 1)[0]).resolve()
        if path == _BROWSER_DIR or _BROWSER_DIR in path.parents:
            return True
    return False


def pytest_sessionstart(session: pytest.Session) -> None:
    """Require Playwright only when browser smoke tests are explicitly selected.

    Broad test runs retain the module's optional ``pytest.importorskip``
    behavior. An explicit browser run instead reports actionable setup steps.

    Args:
        session: Active pytest session and selected test arguments.

    Raises:
        pytest.UsageError: If explicitly requested browser tests lack Playwright.
    """
    if not _explicit_browser_selection(session.config.args):
        return
    try:
        available = find_spec("playwright.sync_api") is not None
    except (ModuleNotFoundError, ValueError):
        available = False
    if not available:
        raise pytest.UsageError(
            "Playwright is required for Tatuy browser smoke tests.\n"
            "Install it: python -m pip install playwright\n"
            "Install the selected browser: "
            "python -m playwright install chromium\n"
            "Build the showcase: poetry run python scripts/build_showcase.py\n"
            "Rerun: python -m pytest tests/browser/test_browser_smoke.py -q\n"
            "For TATUY_BROWSER=firefox or webkit, install that browser too."
        )
