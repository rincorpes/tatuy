from __future__ import annotations

import sys
from collections.abc import Sequence
from pathlib import Path

from tatuy_mcp.access.paths import ProjectPathResolver
from tatuy_mcp.execution.runner import CommandRunner
from tatuy_mcp.projects.registry import ProjectRegistry


class PythonAnalyzer:
    def __init__(
        self,
        registry: ProjectRegistry,
        paths: ProjectPathResolver,
        runner: CommandRunner,
        *,
        max_paths: int,
    ) -> None:
        self._registry = registry
        self._paths = paths
        self._runner = runner
        self._max_paths = max_paths

    def run_mypy(
        self,
        project: str,
        *,
        paths: Sequence[str] | None = None,
    ) -> dict[str, object]:
        root = self._registry.root(project)
        command = [sys.executable, "-m", "mypy", "--show-error-codes"]
        if paths:
            targets = self._paths.resolve_many(
                project,
                paths,
                max_paths=self._max_paths,
            )
            validate_targets(root, targets, tool_name="run_mypy")
            command.extend(str(target.relative_to(root)) for target in targets)

        result = self._runner.run(command, cwd=root)
        return {
            "project": project,
            "paths": list(paths) if paths is not None else None,
            "clean": result.completed and result.exit_code == 0,
            "result": result.as_dict(),
        }

    def run_pylint(
        self,
        project: str,
        *,
        paths: Sequence[str] | None = None,
    ) -> dict[str, object]:
        root = self._registry.root(project)
        if paths:
            targets = self._paths.resolve_many(
                project,
                paths,
                max_paths=self._max_paths,
            )
        else:
            source_root = root / "src"
            targets = [source_root if source_root.is_dir() else root]

        validate_targets(root, targets, tool_name="run_pylint")
        arguments = [
            "." if target == root else str(target.relative_to(root))
            for target in targets
        ]
        command = [
            sys.executable,
            "-m",
            "pylint",
            "--output-format=text",
            "--reports=no",
            "--score=no",
            *arguments,
        ]
        result = self._runner.run(command, cwd=root)
        return {
            "project": project,
            "paths": list(paths) if paths is not None else None,
            "clean": result.completed and result.exit_code == 0,
            "categories": pylint_status_categories(result.exit_code),
            "result": result.as_dict(),
        }


def validate_targets(
    root: Path,
    targets: Sequence[Path],
    *,
    tool_name: str,
) -> None:
    tests_root = root / "tests"
    has_tests = tests_root.is_dir()
    if has_tests:
        tests_root = tests_root.resolve(strict=True)

    for target in targets:
        if target.is_file() and target.suffix.casefold() != ".py":
            raise ValueError(
                f"{tool_name} accepts Python files or directories"
            )
        if not has_tests:
            continue
        if target == tests_root or target.is_relative_to(tests_root):
            raise ValueError(
                f"{tool_name} does not analyze test files. "
                "Tests are verified with formatting and pytest."
            )
        if target == root:
            raise ValueError(
                f"{tool_name} cannot analyze the project root because "
                "it contains tests. Select source or example paths instead."
            )


def pylint_status_categories(exit_code: int | None) -> list[str]:
    if not isinstance(exit_code, int):
        return []
    flags = (
        (1, "fatal"),
        (2, "error"),
        (4, "warning"),
        (8, "refactor"),
        (16, "convention"),
        (32, "usage_error"),
    )
    return [name for flag, name in flags if exit_code & flag]
