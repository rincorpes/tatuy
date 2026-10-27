"""Compatibility tests for the legacy web-spike helper."""

from pathlib import Path
from unittest.mock import Mock

from scripts import prepare_web_spike


def test_prepare_delegates_to_reusable_web_builder(monkeypatch) -> None:
    """Keep the old helper as a thin wrapper around W6 tooling."""
    staging = Path(".tatuy/web-spike/render-queue-551fc8d2")
    builder = Mock()
    builder.prepare.return_value = (staging, object())
    monkeypatch.setattr(prepare_web_spike, "_builder", lambda: builder)

    result = prepare_web_spike.prepare()

    assert result == staging
    builder.prepare.assert_called_once_with(prepare_web_spike.SOURCE_TARGET)


def test_browser_urls_include_build_identity() -> None:
    """Bust the root HTML cache with the staged content fingerprint."""
    staging = Path(".tatuy/web-spike/render-queue-551fc8d2")

    normal, interactive = prepare_web_spike.browser_urls(staging, port=8766)

    assert normal == (
        "http://localhost:8766/index.html?"
        "PYGPI=http://localhost:8766/cdn/&TATUY_BUILD=551fc8d2#"
    )
    assert interactive == (
        "http://localhost:8766/index.html?"
        "PYGPI=http://localhost:8766/cdn/&TATUY_BUILD=551fc8d2&-i#"
    )
