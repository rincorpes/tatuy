"""Capture browser-rendered thumbnails for every public Tatuy showcase target."""

from __future__ import annotations

import json
import shutil
import threading
import time
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WEB_ROOT = REPOSITORY_ROOT / "build" / "web"
THUMBNAIL_ROOT = WEB_ROOT / "assets" / "thumbnails"


class _QuietHandler(SimpleHTTPRequestHandler):
    """Serve the generated site without polluting CI logs with every asset request."""

    def log_message(self, format_string: str, *args: Any) -> None:
        """Suppress the default request log."""


def _playable_slugs() -> list[str]:
    manifest = WEB_ROOT / "manifest.json"
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    targets = payload.get("targets", [])
    if not isinstance(targets, list):
        raise TypeError("Showcase manifest targets must be a list")
    slugs = [
        str(target["slug"])
        for target in targets
        if isinstance(target, dict) and target.get("playable") is True
    ]
    if not slugs:
        raise ValueError("Showcase manifest has no playable targets")
    return sorted(slugs)


def _wait_for_rendered_canvas(
    page: Any,
    canvas: Any,
    *,
    timeout_ms: int = 20_000,
    poll_ms: int = 250,
) -> None:
    """Wait until Pygbag replaces its initial loading frame with runtime output."""
    initial = canvas.screenshot()
    deadline = time.monotonic() + (timeout_ms / 1000)
    while time.monotonic() < deadline:
        page.wait_for_timeout(poll_ms)
        if canvas.screenshot() != initial:
            page.wait_for_timeout(500)
            return
    raise TimeoutError("Runtime canvas did not advance beyond its loading frame")


def main() -> None:
    """Serve the composed site and capture each playable runtime canvas."""
    from playwright.sync_api import sync_playwright  # pylint: disable=import-error,import-outside-toplevel

    if not (WEB_ROOT / "index.html").is_file():
        raise FileNotFoundError("build/web is missing; build the showcase first")

    slugs = _playable_slugs()
    if THUMBNAIL_ROOT.exists():
        shutil.rmtree(THUMBNAIL_ROOT)
    THUMBNAIL_ROOT.mkdir(parents=True)

    handler = partial(_QuietHandler, directory=str(WEB_ROOT))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    port = server.server_port
    base_url = f"http://127.0.0.1:{port}"

    try:
        with sync_playwright() as runtime:
            browser = runtime.chromium.launch(headless=True)
            try:
                for slug in slugs:
                    page = browser.new_page(viewport={"width": 1280, "height": 900})
                    try:
                        page.goto(
                            f"{base_url}/showcase/{slug}/",
                            wait_until="domcontentloaded",
                            timeout=60_000,
                        )
                        canvas = page.frame_locator("#tatuy-runtime").locator(
                            "canvas"
                        ).first
                        canvas.wait_for(state="visible", timeout=60_000)
                        _wait_for_rendered_canvas(page, canvas)
                        canvas.screenshot(path=str(THUMBNAIL_ROOT / f"{slug}.png"))
                        print(f"Captured thumbnail: {slug}")
                    finally:
                        page.close()
            finally:
                browser.close()
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()

    print(f"Captured {len(slugs)} showcase thumbnails in {THUMBNAIL_ROOT}")


if __name__ == "__main__":
    main()
