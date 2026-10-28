"""Publication structure validation for generated Tatuy web output."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tatuy.tooling.web.validation import WebOutputStructureValidator


def _output(tmp_path: Path) -> Path:
    output = tmp_path / "web"
    (output / "docs").mkdir(parents=True)
    (output / "play" / "demo").mkdir(parents=True)
    (output / "index.html").write_text("home", encoding="utf-8")
    (output / "docs" / "index.html").write_text("docs", encoding="utf-8")
    (output / "play" / "demo" / "index.html").write_text(
        "runtime", encoding="utf-8"
    )
    (output / "play" / "demo" / "build.json").write_text(
        "{}", encoding="utf-8"
    )
    (output / "build.json").write_text("{}", encoding="utf-8")
    (output / ".nojekyll").touch()
    (output / "manifest.json").write_text(
        json.dumps(
            {
                "targets": [
                    {
                        "slug": "demo",
                        "web": True,
                        "playable": True,
                        "entrypoint": "play/demo/index.html",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    return output


def test_structure_validator_accepts_complete_publication(tmp_path: Path) -> None:
    WebOutputStructureValidator().validate(_output(tmp_path))


def test_structure_validator_requires_docs_and_home(tmp_path: Path) -> None:
    output = _output(tmp_path)
    (output / "docs" / "index.html").unlink()

    with pytest.raises(FileNotFoundError, match="docs/index.html"):
        WebOutputStructureValidator().validate(output)


def test_structure_validator_requires_every_web_bundle(tmp_path: Path) -> None:
    output = _output(tmp_path)
    (output / "play" / "demo" / "index.html").unlink()

    with pytest.raises(FileNotFoundError, match="bundle for demo"):
        WebOutputStructureValidator().validate(output)


def test_structure_validator_rejects_duplicate_manifest_slugs(tmp_path: Path) -> None:
    output = _output(tmp_path)
    manifest = output / "manifest.json"
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["targets"].append(dict(payload["targets"][0]))
    manifest.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="Duplicate showcase slug"):
        WebOutputStructureValidator().validate(output)


def test_structure_validator_requires_referenced_screenshot(tmp_path: Path) -> None:
    output = _output(tmp_path)
    manifest = output / "manifest.json"
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["targets"][0]["screenshot"] = "assets/demo.png"
    manifest.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(FileNotFoundError, match="screenshot for demo"):
        WebOutputStructureValidator().validate(output)


def test_structure_validator_rejects_private_local_files(tmp_path: Path) -> None:
    output = _output(tmp_path)
    leaked = output / "play" / "demo" / ".env"
    leaked.write_text("TOKEN=secret\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Private/local file leaked"):
        WebOutputStructureValidator().validate(output)
