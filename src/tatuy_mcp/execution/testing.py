from __future__ import annotations

import sys
from collections.abc import Sequence

from tatuy_mcp.access.paths import ProjectPathResolver
from tatuy_mcp.execution.runner import CommandRunner
from tatuy_mcp.projects.registry import ProjectRegistry


class TestRunner:
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

    def run(
        self,
        project: str,
        *,
        paths: Sequence[str] | None = None,
        keyword: str | None = None,
    ) -> dict[str, object]:
        entry = self._registry.get(project)
        if entry.kind in {"experiment", "game"}:
            raise ValueError(
                "Tatuy experiments and games are executable validation "
                "targets, not pytest test suites."
            )

        root = self._registry.root(project)
        if keyword is not None:
            keyword = keyword.strip()
            if not keyword:
                keyword = None
            elif len(keyword) > 200:
                raise ValueError(
                    "pytest keyword must not exceed 200 characters"
                )

        if entry.kind == "engine":
            tests_root = self._paths.resolve_existing(project, "tests")
            if paths:
                targets = self._paths.resolve_many(
                    project,
                    paths,
                    max_paths=self._max_paths,
                )
                for target in targets:
                    if target != tests_root and not target.is_relative_to(
                        tests_root
                    ):
                        raise ValueError(
                            "Tatuy pytest targets must live under tests/. "
                            "Examples, experiments, and games are verified "
                            "as executable examples instead."
                        )
            else:
                targets = [tests_root]
        elif paths:
            targets = self._paths.resolve_many(
                project,
                paths,
                max_paths=self._max_paths,
            )
        else:
            tests = root / "tests"
            targets = [tests if tests.is_dir() else root]

        command = [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            *(str(target) for target in targets),
        ]
        if keyword is not None:
            command.extend(["-k", keyword])

        result = self._runner.run(command, cwd=root)
        return {
            "project": project,
            "paths": list(paths) if paths is not None else None,
            "keyword": keyword,
            "passed": result.completed and result.exit_code == 0,
            "result": result.as_dict(),
        }
