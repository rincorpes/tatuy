"""Regression coverage for reusable Tatuy web-target packaging."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import Mock

import pytest

from tatuy.tooling.web.builder import WebTargetBuilder
from tatuy.tooling.web.pygbag import PygbagPackager


class FakePackager:
    """Create deterministic static output without invoking Pygbag."""

    def __init__(self) -> None:
        self.calls: list[Path] = []

    def build(self, staging: Path) -> None:
        self.calls.append(staging)
        build_root = staging / "build" / "web"
        build_root.mkdir(parents=True)
        (build_root / "index.html").write_text(
            "<html></html>\n", encoding="utf-8"
        )
        (build_root / "app.tar.gz").write_bytes(b"archive")


def _builder_fixture(
    tmp_path: Path,
) -> tuple[WebTargetBuilder, Path, FakePackager]:
    repository = tmp_path / "repo"
    target = repository / "examples" / "demo"
    tatuy_source = repository / "src" / "tatuy"
    target.mkdir(parents=True)
    tatuy_source.mkdir(parents=True)
    (tatuy_source / "__init__.py").write_text("", encoding="utf-8")
    (target / "app.py").write_text(
        "def create_app(config): return config\n", encoding="utf-8"
    )
    (target / "helper.py").write_text("VALUE = 1\n", encoding="utf-8")
    assets = target / "assets"
    assets.mkdir()
    (assets / "sound.wav").write_bytes(b"audio")
    (target / "tatuy.web.yml").write_text(
        "showcase:\n"
        "  slug: demo-target\n"
        "  title: Demo Target\n"
        "  description: Browser demo\n"
        "app:\n"
        "  loop: asyncio\n",
        encoding="utf-8",
    )
    packager = FakePackager()
    builder = WebTargetBuilder(
        repository,
        staging_root=repository / ".tatuy" / "staging",
        output_root=repository / "build" / "web",
        tatuy_source=tatuy_source,
        pure_python_packages=(),
        packager=packager,  # type: ignore[arg-type]
    )
    return builder, target, packager


def test_prepare_stages_target_source_assets_and_host_config(
    tmp_path: Path,
) -> None:
    builder, target, _ = _builder_fixture(tmp_path)

    staging, metadata = builder.prepare(target)

    launcher = (staging / "main.py").read_text(encoding="utf-8")
    assert metadata.slug == "demo-target"
    assert metadata.title == "Demo Target"
    assert metadata.description == "Browser demo"
    assert (staging / "app.py").exists()
    assert (staging / "helper.py").exists()
    assert (staging / "assets" / "sound.wav").read_bytes() == b"audio"
    assert not (staging / "tatuy.web.yml").exists()
    assert "'loop': 'asyncio'" in launcher
    assert "'capture': False" in launcher
    assert "'replay': False" in launcher
    assert "'audio': {'auto_init': False}" in launcher
    assert "'enabled': False" not in launcher
    assert "'storage': {'provider': 'ephemeral'}" in launcher
    assert "showcase" not in launcher
    assert "web_package" not in launcher
    assert "await AsyncRuntimeHost().run(app.build())" in launcher


def test_prepare_changes_build_identity_when_target_changes(
    tmp_path: Path,
) -> None:
    builder, target, _ = _builder_fixture(tmp_path)

    first, _ = builder.prepare(target)
    first_name = first.name
    (target / "helper.py").write_text("VALUE = 2\n", encoding="utf-8")
    second, _ = builder.prepare(target)

    assert second.name != first_name
    assert not first.exists()


def test_prepare_packages_declared_repository_file_and_fingerprints_it(
    tmp_path: Path,
) -> None:
    builder, target, _ = _builder_fixture(tmp_path)
    shared = builder.repository_root / "shared" / "audio" / "test.wav"
    shared.parent.mkdir(parents=True)
    shared.write_bytes(b"first")
    profile = target / "tatuy.web.yml"
    profile.write_text(
        profile.read_text(encoding="utf-8")
        + "web_package:\n"
        + "  files:\n"
        + "    - source: shared/audio/test.wav\n"
        + "      destination: assets/external.wav\n",
        encoding="utf-8",
    )

    first, _ = builder.prepare(target)
    first_name = first.name
    assert (first / "assets" / "external.wav").read_bytes() == b"first"

    shared.write_bytes(b"second")
    second, _ = builder.prepare(target)

    assert second.name != first_name
    assert (second / "assets" / "external.wav").read_bytes() == b"second"


def test_build_invokes_packager_and_normalizes_output(tmp_path: Path) -> None:
    builder, target, packager = _builder_fixture(tmp_path)

    result = builder.build(target)

    assert packager.calls == [result.staging]
    assert result.output == builder.output_root / "play" / "demo-target"
    assert (result.output / "index.html").exists()
    assert (result.output / "app.tar.gz").read_bytes() == b"archive"
    assert result.manifest == builder.output_root / "manifest.json"
    assert (builder.output_root / ".nojekyll").exists()
    payload = json.loads(result.manifest.read_text(encoding="utf-8"))
    assert payload == {
        "targets": [
            {
                "slug": "demo-target",
                "title": "Demo Target",
                "description": "Browser demo",
                "entrypoint": "play/demo-target/index.html",
                "build_id": result.build_id,
            }
        ]
    }


def test_build_preserves_other_manifest_entries(tmp_path: Path) -> None:
    builder, target, _ = _builder_fixture(tmp_path)
    builder.output_root.mkdir(parents=True)
    (builder.output_root / "manifest.json").write_text(
        json.dumps(
            {
                "targets": [
                    {
                        "slug": "other",
                        "title": "Other",
                        "description": "",
                        "entrypoint": "play/other/index.html",
                        "build_id": "12345678",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    result = builder.build(target)
    payload = json.loads(result.manifest.read_text(encoding="utf-8"))

    assert [entry["slug"] for entry in payload["targets"]] == [
        "demo-target",
        "other",
    ]


def test_resolve_target_rejects_paths_outside_repository(
    tmp_path: Path,
) -> None:
    builder, _, _ = _builder_fixture(tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "app.py").write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="inside the repository"):
        builder.resolve_target(outside)


def test_pygbag_packager_invokes_static_build(
    monkeypatch, tmp_path: Path
) -> None:
    run = Mock()
    monkeypatch.setattr("tatuy.tooling.web.pygbag.subprocess.run", run)
    staging = tmp_path / "staging"
    packager = PygbagPackager(command=("python-web", "-m", "pygbag"))

    packager.build(staging)

    run.assert_called_once_with(
        [
            "python-web",
            "-m",
            "pygbag",
            "--PYBUILD",
            "3.12",
            "--ume_block",
            "0",
            "--build",
            str(staging),
        ],
        check=True,
    )


def test_pygbag_packager_can_suppress_sound_format_validation_for_local_smoke(
    monkeypatch, tmp_path: Path
) -> None:
    run = Mock()
    monkeypatch.setattr("tatuy.tooling.web.pygbag.subprocess.run", run)
    staging = tmp_path / "staging"
    packager = PygbagPackager(
        command=("python-web", "-m", "pygbag"),
        disable_sound_format_error=True,
    )

    packager.build(staging)

    command = run.call_args.args[0]
    assert "--disable-sound-format-error" in command
    assert command[-2:] == ["--build", str(staging)]
