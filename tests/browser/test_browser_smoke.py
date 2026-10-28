"""Browser-level smoke coverage for one representative Tatuy web target."""

from __future__ import annotations

import os
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Iterator

import pytest

playwright = pytest.importorskip("playwright.sync_api")
from playwright.sync_api import (  # type: ignore[import-not-found]
    Page,
    sync_playwright,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
WEB_ROOT = PROJECT_ROOT / "build" / "web"


@pytest.fixture(scope="module")
def showcase_url() -> Iterator[str]:
    """Serve the generated showcase from an ephemeral localhost port."""
    if not (WEB_ROOT / "index.html").is_file():
        pytest.fail(
            "build/web is missing; build the showcase before browser smoke tests"
        )

    handler = partial(SimpleHTTPRequestHandler, directory=str(WEB_ROOT))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    port = server.server_port
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()


_BENIGN_BROWSER_ERRORS = {
    "PyMain: BrowserFS not found",
}


def _collect_fatal_errors(page: Page) -> list[str]:
    errors: list[str] = []

    def collect(message: str) -> None:
        if message not in _BENIGN_BROWSER_ERRORS:
            errors.append(message)

    page.on("pageerror", lambda error: collect(str(error)))
    page.on(
        "console",
        lambda message: (
            collect(message.text) if message.type == "error" else None
        ),
    )
    return errors


def test_controlled_movement_renders_and_responds_to_keyboard(
    showcase_url: str,
) -> None:
    """Reach a rendered frame and prove keyboard input changes visible output."""
    browser_name = os.environ.get("TATUY_BROWSER", "chromium").strip().lower()
    if browser_name not in {"chromium", "firefox", "webkit"}:
        pytest.fail(f"Unsupported TATUY_BROWSER: {browser_name}")

    with sync_playwright() as runtime:
        browser_type = getattr(runtime, browser_name)
        browser = browser_type.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        fatal_errors = _collect_fatal_errors(page)
        try:
            page.goto(
                f"{showcase_url}/showcase/controlled-movement/",
                wait_until="domcontentloaded",
                timeout=60_000,
            )
            runtime_frame = page.frame_locator("#tatuy-runtime")
            canvas = runtime_frame.locator("canvas").first
            canvas.wait_for(state="visible", timeout=60_000)
            page.wait_for_timeout(1_500)

            canvas.click(position={"x": 400, "y": 300})
            before = canvas.screenshot()

            page.keyboard.down("d")
            page.wait_for_timeout(350)
            page.keyboard.up("d")
            page.wait_for_timeout(250)

            after = canvas.screenshot()
            assert (
                before != after
            ), "Keyboard input did not change the rendered canvas"
            assert not fatal_errors, f"Fatal browser errors: {fatal_errors}"
        finally:
            browser.close()
