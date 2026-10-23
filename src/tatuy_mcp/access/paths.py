from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from tatuy_mcp.access.policy import AccessPolicy
from tatuy_mcp.projects.registry import ProjectRegistry


class ProjectPathResolver:
    def __init__(
        self,
        registry: ProjectRegistry,
        policy: AccessPolicy,
    ) -> None:
        self._registry = registry
        self._policy = policy

    @staticmethod
    def _relative_path(value: str) -> Path:
        requested = Path(value)
        if requested.is_absolute() or requested.drive or requested.root:
            raise ValueError("Provide a project-relative path")
        return requested

    def resolve_existing(
        self,
        project: str,
        relative_path: str = ".",
    ) -> Path:
        root = self._registry.root(project)
        requested = self._relative_path(relative_path)
        self._policy.check_access(requested)
        target = (root / requested).resolve(strict=True)
        if not target.is_relative_to(root):
            raise ValueError("Path points outside the selected project")
        self._policy.check_access(target.relative_to(root))
        return target

    def resolve_new(self, project: str, relative_path: str) -> Path:
        root = self._registry.root(project)
        requested = self._relative_path(relative_path)
        self._policy.check_access(requested)
        target = (root / requested).resolve(strict=False)
        if not target.is_relative_to(root):
            raise ValueError("Path points outside the selected project")
        self._policy.check_access(target.relative_to(root))
        parent = target.parent.resolve(strict=True)
        if not parent.is_relative_to(root):
            raise ValueError(
                "Parent directory points outside the selected project"
            )
        if target.exists():
            raise ValueError(f"Path already exists: {relative_path}")
        return target

    def resolve_deletion(self, project: str, relative_path: str) -> Path:
        root = self._registry.root(project)
        requested = self._relative_path(relative_path)
        if requested == Path("."):
            raise ValueError("Cannot delete a project root")
        self._policy.check_access(requested)
        unresolved = root / requested
        if unresolved.is_symlink():
            raise ValueError("Deleting symbolic links is not supported")
        target = unresolved.resolve(strict=True)
        if target == root:
            raise ValueError("Cannot delete a project root")
        if not target.is_relative_to(root):
            raise ValueError("Path points outside the selected project")
        self._policy.check_access(target.relative_to(root))
        return target

    def resolve_many(
        self,
        project: str,
        paths: Sequence[str],
        *,
        max_paths: int,
    ) -> list[Path]:
        if not paths:
            raise ValueError("Provide at least one project-relative path")
        if len(paths) > max_paths:
            raise ValueError(f"Provide at most {max_paths} paths")
        return [self.resolve_existing(project, path) for path in paths]
