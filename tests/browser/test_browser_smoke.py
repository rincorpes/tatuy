"""Browser-level smoke coverage for one representative Tatuy web target."""

from __future__ import annotations

import os
import threading
import time
from base64 import b64encode
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Iterator

import pytest

playwright = pytest.importorskip("playwright.sync_api")
from playwright.sync_api import (  # type: ignore[import-not-found]
    Locator,
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


def _wait_for_runtime_ready(
    page: Page, runtime_frame, timeout_ms: int = 60_000
) -> None:
    """Wait for the generated Tatuy launcher to report its first completed frame."""
    html = runtime_frame.locator("html")
    deadline = time.monotonic() + (timeout_ms / 1000)
    while time.monotonic() < deadline:
        if html.evaluate("() => window.__tatuy_ready__ === true"):
            return
        page.wait_for_timeout(250)
    pytest.fail("Tatuy browser runtime did not report first-frame readiness")


def _visible_snake_center(page: Page, canvas: Locator) -> tuple[float, float]:
    """Locate Snake's green segment in a real browser canvas screenshot.

    A screenshot is decoded in a separate 2D canvas so the game renderer
    does not need to expose a readable rendering context or debug state.

    Args:
        page: Browser page owning the screenshot decoder.
        canvas: Rendered game canvas in the embedded runtime.

    Returns:
        Pixel coordinates of the green segment's visible center.
    """
    encoded_png = b64encode(canvas.screenshot()).decode("ascii")
    position = page.evaluate(
        """async (png) => {
            const image = new Image();
            image.src = "data:image/png;base64," + png;
            await image.decode();
            const scratch = document.createElement("canvas");
            scratch.width = image.naturalWidth;
            scratch.height = image.naturalHeight;
            const context = scratch.getContext("2d");
            if (!context) throw new Error("Screenshot decoder unavailable");
            context.drawImage(image, 0, 0);
            const pixels = context.getImageData(
                0, 0, scratch.width, scratch.height
            ).data;
            let count = 0;
            let sumX = 0;
            let sumY = 0;
            for (let offset = 0; offset < pixels.length; offset += 4) {
                // SnakeSegmentBlueprint uses RGB (80, 220, 140).
                if (
                    Math.abs(pixels[offset] - 80) <= 10 &&
                    Math.abs(pixels[offset + 1] - 220) <= 10 &&
                    Math.abs(pixels[offset + 2] - 140) <= 10
                ) {
                    const pixel = offset / 4;
                    sumX += pixel % scratch.width;
                    sumY += Math.floor(pixel / scratch.width);
                    count++;
                }
            }
            return count >= 40 ? [sumX / count, sumY / count] : null;
        }""",
        encoded_png,
    )
    assert position is not None, "Snake's green segment is not visible"
    return float(position[0]), float(position[1])


def _wait_for_snake_turn(
    page: Page,
    canvas: Locator,
    *,
    key: str,
    axis: int,
    sign: int,
    origin: tuple[float, float],
) -> tuple[float, float]:
    """Require a directional displacement while holding one WASD key.

    Args:
        page: Browser page sending actual keyboard events.
        canvas: Rendered game canvas to measure.
        key: Direction key to hold while checking motion.
        axis: Coordinate index (0 for horizontal, 1 for vertical).
        sign: Expected change direction (-1 or 1).
        origin: Position measured before the key press.

    Returns:
        First observed position at least half a grid cell along that axis.
    """
    page.keyboard.down(key)
    try:
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline:
            page.wait_for_timeout(100)
            position = _visible_snake_center(page, canvas)
            if (position[axis] - origin[axis]) * sign >= 14:
                return position
    finally:
        page.keyboard.up(key)
    pytest.fail(f"Snake did not turn for '{key}' in the browser")


def test_snake_wasd_changes_direction_in_browser(showcase_url: str) -> None:
    """Verify every WASD turn by observing rendered Snake displacement."""
    browser_name = os.environ.get("TATUY_BROWSER", "chromium").strip().lower()
    if browser_name not in {"chromium", "firefox", "webkit"}:
        pytest.fail(f"Unsupported TATUY_BROWSER: {browser_name}")

    with sync_playwright() as runtime:
        browser = getattr(runtime, browser_name).launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        fatal_errors = _collect_fatal_errors(page)
        try:
            page.goto(
                f"{showcase_url}/showcase/snake/",
                wait_until="domcontentloaded",
                timeout=60_000,
            )
            runtime_frame = page.frame_locator("#tatuy-runtime")
            canvas = runtime_frame.locator("canvas").first
            canvas.wait_for(state="visible", timeout=60_000)
            _wait_for_runtime_ready(page, runtime_frame)

            canvas.click(position={"x": 400, "y": 300})
            assert page.evaluate(
                "() => document.activeElement?.id === 'tatuy-runtime'"
            ), "Snake runtime iframe did not receive keyboard focus"

            position = _visible_snake_center(page, canvas)
            for key, axis, sign in (
                ("w", 1, -1),
                ("a", 0, -1),
                ("s", 1, 1),
                ("d", 0, 1),
            ):
                position = _wait_for_snake_turn(
                    page,
                    canvas,
                    key=key,
                    axis=axis,
                    sign=sign,
                    origin=position,
                )

            assert not fatal_errors, f"Fatal browser errors: {fatal_errors}"
        finally:
            browser.close()


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
            _wait_for_runtime_ready(page, runtime_frame)
            page.wait_for_timeout(250)

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


@pytest.mark.parametrize(
    ("slug", "title", "action"),
    [
        ("procedural-tree", "Procedural Tree", "r"),
        ("infection-arena", "Infection Arena", "t"),
        ("snake", "Snake", None),
    ],
)
def test_portfolio_showcase_candidates_start_in_browser(
    showcase_url: str,
    slug: str,
    title: str,
    action: str | None,
) -> None:
    """Smoke-test first-frame readiness for the three portfolio candidates.

    Tree regeneration and Infection Arena's reproduction toggle must visibly
    change the canvas. Snake's automatic movement means startup alone cannot
    prove directional keyboard control; that needs a dedicated gameplay check.
    """
    browser_name = os.environ.get("TATUY_BROWSER", "chromium").strip().lower()
    if browser_name not in {"chromium", "firefox", "webkit"}:
        pytest.fail(f"Unsupported TATUY_BROWSER: {browser_name}")

    with sync_playwright() as runtime:
        browser = getattr(runtime, browser_name).launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        fatal_errors = _collect_fatal_errors(page)
        try:
            page.goto(
                f"{showcase_url}/showcase/{slug}/",
                wait_until="domcontentloaded",
                timeout=60_000,
            )
            assert page.locator("h1").inner_text() == title

            runtime_frame = page.frame_locator("#tatuy-runtime")
            canvas = runtime_frame.locator("canvas").first
            canvas.wait_for(state="visible", timeout=60_000)
            _wait_for_runtime_ready(page, runtime_frame)
            canvas.click(position={"x": 400, "y": 300})
            page.wait_for_timeout(300)

            first_frame = canvas.screenshot()
            assert first_frame.startswith(b"\x89PNG\r\n\x1a\n")

            if action == "r":
                # Allow some initial branches to grow before restarting.
                page.wait_for_timeout(1000)
                before = canvas.screenshot()
            elif action == "t":
                # Pause simulation so only the HUD toggle changes.
                page.keyboard.press("p")
                page.wait_for_timeout(250)
                before = canvas.screenshot()
            else:
                before = None

            if action is not None:
                page.keyboard.press(action)
                page.wait_for_timeout(350)
                assert (
                    canvas.screenshot() != before
                ), f"{title} did not visibly respond to '{action}'"

            assert not fatal_errors, f"Fatal browser errors: {fatal_errors}"
        finally:
            browser.close()
