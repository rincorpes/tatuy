"""Target scaffolding keeps browser showcase metadata optional and reusable."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from tatuy_cli.scaffolding.model import CreateTargetRequest
from tatuy_cli.scaffolding.service import TargetScaffolder


def _scaffolder(tmp_path: Path) -> TargetScaffolder:
    engine = tmp_path / "tatuy"
    (engine / "examples" / "games").mkdir(parents=True)
    (engine / "examples" / "experiments").mkdir(parents=True)
    return TargetScaffolder(
        engine_root=engine,
        projects_root=tmp_path / "projects",
    )


def test_game_scaffold_uses_reusable_create_app_without_showcase_by_default(
    tmp_path: Path,
) -> None:
    result = _scaffolder(tmp_path).create(
        CreateTargetRequest(kind="game", name="tiny_game")
    )

    app = (result.path / "app.py").read_text(encoding="utf-8")
    assert "def create_app(config: TatuyConfigDict | None = None)" in app
    assert "create_app().run()" in app
    assert not (result.path / "tatuy.web.yml").exists()


def test_game_scaffold_can_opt_into_safe_showcase_metadata(tmp_path: Path) -> None:
    result = _scaffolder(tmp_path).create(
        CreateTargetRequest(
            kind="game",
            name="tiny_game",
            description="Small: browser candidate",
            tags=("input", "ecs"),
            showcase=True,
        )
    )

    profile = yaml.safe_load(
        (result.path / "tatuy.web.yml").read_text(encoding="utf-8")
    )
    showcase = profile["showcase"]
    assert showcase["id"] == "games/tiny-game"
    assert showcase["slug"] == "tiny-game"
    assert showcase["category"] == "game"
    assert showcase["source"] == "examples/games/001_tiny_game"
    assert showcase["docs"] == "docs/examples/games.md"
    assert showcase["web"] is False
    assert showcase["tags"] == ["game", "input", "ecs"]
    assert profile["app"]["loop"] == "asyncio"


def test_experiment_showcase_uses_experiment_docs(tmp_path: Path) -> None:
    result = _scaffolder(tmp_path).create(
        CreateTargetRequest(
            kind="experiment",
            name="physics_probe",
            showcase=True,
        )
    )

    profile = yaml.safe_load(
        (result.path / "tatuy.web.yml").read_text(encoding="utf-8")
    )
    showcase = profile["showcase"]
    assert showcase["id"] == "experiments/physics-probe"
    assert showcase["category"] == "experiment"
    assert showcase["docs"] == "docs/examples/experiments.md"
    assert showcase["web"] is False


def test_standalone_project_cannot_generate_repository_showcase_metadata(
    tmp_path: Path,
) -> None:
    with pytest.raises(ValueError, match="only supported for workspace"):
        _scaffolder(tmp_path).create(
            CreateTargetRequest(
                kind="project",
                name="standalone",
                destination=tmp_path / "standalone",
                showcase=True,
            )
        )
