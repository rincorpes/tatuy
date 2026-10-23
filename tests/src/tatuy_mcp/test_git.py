from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from tatuy_mcp.access.paths import ProjectPathResolver
from tatuy_mcp.access.policy import DEFAULT_ACCESS_POLICY
from tatuy_mcp.execution.git import GitWorkspace
from tatuy_mcp.execution.runner import CommandRunner


class StubProjects:
    def __init__(self, root: Path) -> None:
        self._root = root

    def root(self, key: str) -> Path:
        if key != "engine":
            raise ValueError(f"Unknown project: {key}")
        return self._root


def run_git(root: Path, *args: str) -> None:
    subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )


def create_workspace(root: Path) -> GitWorkspace:
    projects = StubProjects(root)
    paths = ProjectPathResolver(projects, DEFAULT_ACCESS_POLICY)
    commands = CommandRunner(timeout_seconds=10, max_output=100_000)
    return GitWorkspace(projects, paths, commands, max_paths=20)


def initialize_repo(root: Path) -> None:
    run_git(root, "init")
    run_git(root, "config", "user.email", "tatuy@example.com")
    run_git(root, "config", "user.name", "Tatuy Tests")
    tracked = root / "tracked.txt"
    tracked.write_text("before\n", encoding="utf-8")
    run_git(root, "add", "tracked.txt")
    run_git(root, "commit", "-m", "chore: initialize test repo")


def test_status_and_snapshot_include_untracked_files(tmp_path: Path) -> None:
    initialize_repo(tmp_path)
    workspace = create_workspace(tmp_path)
    (tmp_path / "tracked.txt").write_text("after\n", encoding="utf-8")
    (tmp_path / "new_file.txt").write_text("one\ntwo\n", encoding="utf-8")

    status = workspace.status("engine")
    snapshot = workspace.snapshot("engine")

    assert status["clean"] is False
    assert {item["path"] for item in status["files"]} == {
        "tracked.txt",
        "new_file.txt",
    }
    new_file = next(
        item for item in snapshot["files"] if item["path"] == "new_file.txt"
    )
    assert new_file["status"] == "untracked"
    assert new_file["additions"] == 2


def test_diff_includes_untracked_file_contents(tmp_path: Path) -> None:
    initialize_repo(tmp_path)
    workspace = create_workspace(tmp_path)
    nested = tmp_path / "new" / "nested"
    nested.mkdir(parents=True)
    (nested / "file.txt").write_text("hello\n", encoding="utf-8")

    status = workspace.status("engine")
    result = workspace.diff("engine")

    assert {item["path"] for item in status["files"]} == {
        "new/nested/file.txt"
    }
    assert "b/new/nested/file.txt" in result["diff"]
    assert "+hello" in result["diff"]


def test_commit_requires_short_conventional_message(tmp_path: Path) -> None:
    initialize_repo(tmp_path)
    workspace = create_workspace(tmp_path)

    with pytest.raises(ValueError, match="conventional prefix"):
        workspace.commit("engine", "update git workflow")

    with pytest.raises(ValueError, match="72 characters"):
        workspace.commit("engine", "feat: " + "x" * 80)


def test_stage_and_commit_selected_paths(tmp_path: Path) -> None:
    initialize_repo(tmp_path)
    workspace = create_workspace(tmp_path)
    (tmp_path / "tracked.txt").write_text("after\n", encoding="utf-8")

    staged = workspace.stage("engine", ["tracked.txt"])
    committed = workspace.commit("engine", "refactor: update tracked file")

    assert staged == {"staged": ["tracked.txt"]}
    assert committed["message"] == "refactor: update tracked file"
    assert committed["commit"]
    assert workspace.status("engine")["clean"] is True
