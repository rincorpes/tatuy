"""Measure representative Tatuy browser target load and frame-cadence metrics."""

from __future__ import annotations

import argparse
import json
import statistics
import threading
import time
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WEB_ROOT = REPOSITORY_ROOT / "build" / "web"
DEFAULT_OUTPUT = REPOSITORY_ROOT / "build" / "diagnostics" / "web-performance.json"
DEFAULT_SLUGS = ("render-queue", "snake", "entities-pressure")


class _QuietHandler(SimpleHTTPRequestHandler):
    """Serve browser output without request-level log noise."""

    def log_message(self, format_string: str, *args: Any) -> None:
        """Suppress the default request log."""


def _bundle_bytes(slug: str) -> int:
    root = WEB_ROOT / "play" / slug
    if not root.is_dir():
        raise FileNotFoundError(f"Browser bundle not found: {root}")
    return sum(path.stat().st_size for path in root.rglob("*") if path.is_file())


def _percentile(values: list[float], percentile: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, round((len(ordered) - 1) * percentile)))
    return ordered[index]


def _load_to_canvas_ms(page: Any, url: str) -> float:
    started = time.perf_counter()
    page.goto(url, wait_until="domcontentloaded", timeout=60_000)
    page.locator("canvas").first.wait_for(state="visible", timeout=60_000)
    return (time.perf_counter() - started) * 1000.0


def _frame_intervals(page: Any, duration_ms: int = 2500) -> list[float]:
    result = page.evaluate(
        """duration => new Promise(resolve => {
          const intervals = [];
          let previous = null;
          const started = performance.now();
          function sample(now) {
            if (previous !== null) intervals.push(now - previous);
            previous = now;
            if (now - started >= duration) resolve(intervals);
            else requestAnimationFrame(sample);
          }
          requestAnimationFrame(sample);
        })""",
        duration_ms,
    )
    return [float(value) for value in result]


def _measure_target(browser: Any, base_url: str, slug: str) -> dict[str, Any]:
    context = browser.new_context(viewport={"width": 1280, "height": 900})
    page = context.new_page()
    url = f"{base_url}/play/{slug}/index.html"
    try:
        first_load_ms = _load_to_canvas_ms(page, url)
        intervals = _frame_intervals(page)
        cached_load_ms = _load_to_canvas_ms(page, url)
        memory_bytes = page.evaluate(
            """() => performance.memory?.usedJSHeapSize ?? null"""
        )
    finally:
        context.close()

    mean_interval = statistics.mean(intervals) if intervals else 0.0
    return {
        "slug": slug,
        "bundle_bytes": _bundle_bytes(slug),
        "first_load_to_canvas_ms": round(first_load_ms, 2),
        "cached_load_to_canvas_ms": round(cached_load_ms, 2),
        "average_browser_fps": round(1000.0 / mean_interval, 2)
        if mean_interval > 0
        else 0.0,
        "frame_interval_p95_ms": round(_percentile(intervals, 0.95), 2),
        "frame_interval_p99_ms": round(_percentile(intervals, 0.99), 2),
        "js_heap_bytes": int(memory_bytes) if isinstance(memory_bytes, (int, float)) else None,
    }


def main() -> None:
    """Measure selected raw browser bundles and write a JSON diagnostics report."""
    from playwright.sync_api import sync_playwright  # pylint: disable=import-error,import-outside-toplevel

    parser = argparse.ArgumentParser()
    parser.add_argument("--browser", choices=("chromium", "firefox", "webkit"), default="chromium")
    parser.add_argument("--slugs", nargs="+", default=list(DEFAULT_SLUGS))
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    handler = partial(_QuietHandler, directory=str(WEB_ROOT))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{server.server_port}"

    try:
        with sync_playwright() as runtime:
            browser_type = getattr(runtime, args.browser)
            browser = browser_type.launch(headless=True)
            try:
                metrics = [
                    _measure_target(browser, base_url, slug)
                    for slug in args.slugs
                ]
            finally:
                browser.close()
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()

    payload = {
        "browser": args.browser,
        "targets": metrics,
        "note": (
            "Frame cadence uses requestAnimationFrame and is a browser presentation "
            "proxy, not Tatuy profiler FPS."
        ),
    }
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Web performance report: {output}")


if __name__ == "__main__":
    main()
