"""Static showcase composition preserves docs and playable outputs."""

from __future__ import annotations

from pathlib import Path

import pytest

from tatuy.tooling.web.site import ShowcaseSiteBuilder


def _prepared_output(tmp_path: Path) -> Path:
    output = tmp_path / "build" / "web"
    docs = output / "docs"
    play = output / "play" / "render-queue"
    docs.mkdir(parents=True)
    play.mkdir(parents=True)
    (docs / "index.html").write_text("docs", encoding="utf-8")
    (play / "index.html").write_text("runtime", encoding="utf-8")
    (output / "manifest.json").write_text(
        '{"targets": []}\n', encoding="utf-8"
    )
    return output


def test_build_composes_shell_without_replacing_docs_play_or_manifest(
    tmp_path: Path,
) -> None:
    output = _prepared_output(tmp_path)
    docs_before = (output / "docs" / "index.html").read_text(encoding="utf-8")
    play_before = (output / "play" / "render-queue" / "index.html").read_text(
        encoding="utf-8"
    )
    manifest_before = (output / "manifest.json").read_text(encoding="utf-8")

    result = ShowcaseSiteBuilder(tmp_path, output_root=output).build()

    assert result == output
    assert (output / "index.html").is_file()
    assert (output / "assets" / "site.css").is_file()
    assert (output / "assets" / "site.js").is_file()
    assert (output / "showcase" / "render-queue" / "index.html").is_file()
    assert (output / ".nojekyll").exists()
    assert (output / "docs" / "index.html").read_text(
        encoding="utf-8"
    ) == docs_before
    assert (output / "play" / "render-queue" / "index.html").read_text(
        encoding="utf-8"
    ) == play_before
    assert (output / "manifest.json").read_text(
        encoding="utf-8"
    ) == manifest_before


def test_home_links_docs_featured_showcase_source_and_docs(
    tmp_path: Path,
) -> None:
    output = _prepared_output(tmp_path)

    ShowcaseSiteBuilder(tmp_path, output_root=output).build()

    home = (output / "index.html").read_text(encoding="utf-8")
    assert 'href="./docs/"' in home
    assert 'href="./showcase/render-queue/"' in home
    assert "examples/fundamentals/009_rendering/002_render_queue" in home
    assert 'href="./docs/learn/rendering/"' in home


def test_play_page_embeds_raw_runtime_and_exposes_controls(
    tmp_path: Path,
) -> None:
    output = _prepared_output(tmp_path)

    ShowcaseSiteBuilder(tmp_path, output_root=output).build()

    play_page = (
        output / "showcase" / "render-queue" / "index.html"
    ).read_text(encoding="utf-8")
    assert 'src="../../play/render-queue/index.html"' in play_page
    assert 'data-action="restart"' in play_page
    assert 'data-action="fullscreen"' in play_page
    assert "Audio disabled in browser-v0" in play_page


def test_build_requires_docs_output(tmp_path: Path) -> None:
    output = tmp_path / "build" / "web"
    playable = output / "play" / "render-queue"
    playable.mkdir(parents=True)
    (playable / "index.html").write_text("runtime", encoding="utf-8")

    with pytest.raises(
        FileNotFoundError, match="Documentation build not found"
    ):
        ShowcaseSiteBuilder(tmp_path, output_root=output).build()


def test_build_requires_featured_playable(tmp_path: Path) -> None:
    output = tmp_path / "build" / "web"
    docs = output / "docs"
    docs.mkdir(parents=True)
    (docs / "index.html").write_text("docs", encoding="utf-8")

    with pytest.raises(FileNotFoundError, match="Playable build not found"):
        ShowcaseSiteBuilder(tmp_path, output_root=output).build()
