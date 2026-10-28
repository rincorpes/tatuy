"""Deterministic helpers behind showcase thumbnail capture."""

from __future__ import annotations

from collections import deque

import pytest

import scripts.capture_showcase_thumbnails as thumbnails


class _FakeHtml:
    def __init__(self, readiness: list[bool]) -> None:
        self._readiness = deque(readiness)
        self._last = readiness[-1]

    def evaluate(self, expression: str) -> bool:
        assert expression == "() => window.__tatuy_ready__ === true"
        if self._readiness:
            self._last = self._readiness.popleft()
        return self._last


class _FakeRuntimeFrame:
    def __init__(self, readiness: list[bool]) -> None:
        self.html = _FakeHtml(readiness)

    def locator(self, selector: str) -> _FakeHtml:
        assert selector == "html"
        return self.html


class _FakePage:
    def __init__(self) -> None:
        self.waits: list[int] = []

    def wait_for_timeout(self, milliseconds: int) -> None:
        self.waits.append(milliseconds)


def test_wait_for_runtime_ready_waits_for_first_frame_signal(monkeypatch) -> None:
    times = iter([0.0, 0.1, 0.2, 0.3])
    monkeypatch.setattr(thumbnails.time, "monotonic", lambda: next(times))
    page = _FakePage()
    frame = _FakeRuntimeFrame([False, False, True])

    thumbnails._wait_for_runtime_ready(page, frame, timeout_ms=1_000, poll_ms=100)

    assert page.waits == [100, 100, 500]


def test_wait_for_runtime_ready_times_out_without_signal(monkeypatch) -> None:
    times = iter([0.0, 0.1, 1.1])
    monkeypatch.setattr(thumbnails.time, "monotonic", lambda: next(times))
    page = _FakePage()
    frame = _FakeRuntimeFrame([False, False, False])

    with pytest.raises(TimeoutError, match="did not report first-frame readiness"):
        thumbnails._wait_for_runtime_ready(page, frame, timeout_ms=1_000, poll_ms=100)
