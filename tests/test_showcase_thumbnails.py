"""Deterministic helpers behind showcase thumbnail capture."""

from __future__ import annotations

from collections import deque

import pytest

import scripts.capture_showcase_thumbnails as thumbnails


class _FakeCanvas:
    def __init__(self, frames: list[bytes]) -> None:
        self._frames = deque(frames)
        self._last = frames[-1]

    def screenshot(self) -> bytes:
        if self._frames:
            self._last = self._frames.popleft()
        return self._last


class _FakePage:
    def __init__(self) -> None:
        self.waits: list[int] = []

    def wait_for_timeout(self, milliseconds: int) -> None:
        self.waits.append(milliseconds)


def test_wait_for_rendered_canvas_waits_for_pixel_change(monkeypatch) -> None:
    times = iter([0.0, 0.1, 0.2])
    monkeypatch.setattr(thumbnails.time, "monotonic", lambda: next(times))
    page = _FakePage()
    canvas = _FakeCanvas([b"loading", b"loading", b"runtime"])

    thumbnails._wait_for_rendered_canvas(page, canvas, timeout_ms=1_000, poll_ms=100)

    assert page.waits == [100, 100, 500]


def test_wait_for_rendered_canvas_times_out_when_frame_never_changes(monkeypatch) -> None:
    times = iter([0.0, 0.1, 1.1])
    monkeypatch.setattr(thumbnails.time, "monotonic", lambda: next(times))
    page = _FakePage()
    canvas = _FakeCanvas([b"loading", b"loading", b"loading"])

    with pytest.raises(TimeoutError, match="did not advance beyond its loading frame"):
        thumbnails._wait_for_rendered_canvas(page, canvas, timeout_ms=1_000, poll_ms=100)
