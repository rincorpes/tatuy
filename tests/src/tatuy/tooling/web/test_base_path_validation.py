"""GitHub Project Pages base-path safety for generated Tatuy web output."""

from __future__ import annotations

from pathlib import Path

import pytest

from tatuy.tooling.web.validation import WebOutputBasePathValidator


def test_validator_accepts_relative_external_and_anchor_urls(tmp_path: Path) -> None:
    output = tmp_path / "web"
    output.mkdir()
    (output / "index.html").write_text(
        """<link href="./assets/site.css">
<a href="./docs/">Docs</a>
<a href="#showcase">Showcase</a>
<a href="https://github.com/rincorpes/tatuy">GitHub</a>
<iframe src="./play/demo/index.html"></iframe>
""",
        encoding="utf-8",
    )
    assets = output / "assets"
    assets.mkdir()
    (assets / "site.css").write_text(
        "body { background-image: url('../images/bg.png'); }",
        encoding="utf-8",
    )

    WebOutputBasePathValidator().validate(output)


def test_validator_rejects_root_absolute_internal_urls(tmp_path: Path) -> None:
    output = tmp_path / "web"
    output.mkdir()
    (output / "index.html").write_text(
        '<link href="/assets/site.css"><iframe src="/play/demo/index.html"></iframe>',
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="unsafe for GitHub Project Pages"):
        WebOutputBasePathValidator().validate(output)


def test_validator_rejects_root_absolute_css_urls(tmp_path: Path) -> None:
    output = tmp_path / "web"
    output.mkdir()
    (output / "site.css").write_text(
        "body { background-image: url('/assets/bg.png'); }",
        encoding="utf-8",
    )

    violations = WebOutputBasePathValidator().find_violations(output)

    assert len(violations) == 1
    assert violations[0].path == Path("site.css")
    assert violations[0].url == "/assets/bg.png"
