from __future__ import annotations

import sys
from collections.abc import Sequence

from tatuy_mcp.access.paths import ProjectPathResolver
from tatuy_mcp.execution.runner import CommandRunner
from tatuy_mcp.projects.registry import ProjectRegistry


class PythonFormatter:
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

    def format(
        self,
        project: str,
        paths: Sequence[str],
    ) -> dict[str, object]:
        root = self._registry.root(project)
        targets = self._paths.resolve_many(
            project,
            paths,
            max_paths=self._max_paths,
        )
        for target in targets:
            if target.is_file() and target.suffix.casefold() != ".py":
                raise ValueError(
                    "format_python accepts Python files or directories"
                )

        arguments = [str(target) for target in targets]
        isort_result = self._runner.run(
            [sys.executable, "-m", "isort", *arguments],
            cwd=root,
        )
        if isort_result.exit_code != 0:
            return {
                "project": project,
                "paths": list(paths),
                "formatted": False,
                "isort": isort_result.as_dict(),
                "black": None,
            }

        black_result = self._runner.run(
            [sys.executable, "-m", "black", *arguments],
            cwd=root,
        )
        return {
            "project": project,
            "paths": list(paths),
            "formatted": black_result.exit_code == 0,
            "isort": isort_result.as_dict(),
            "black": black_result.as_dict(),
        }
