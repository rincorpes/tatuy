from __future__ import annotations

from pathlib import Path

from tatuy_mcp.projects.discovery import discover_projects
from tatuy_mcp.projects.model import ProjectEntry


class ProjectRegistry:
    def __init__(
        self,
        *,
        engine_root: Path,
        projects_root: Path,
    ) -> None:
        self._engine_root = engine_root
        self._projects_root = projects_root
        self._entries: dict[str, ProjectEntry] = {}

    def refresh(self) -> list[ProjectEntry]:
        entries = discover_projects(
            engine_root=self._engine_root,
            projects_root=self._projects_root,
        )
        self._entries = {entry.key: entry for entry in entries}
        return entries

    def list(self) -> list[ProjectEntry]:
        return self.refresh()

    def get(self, key: str) -> ProjectEntry:
        self.refresh()
        try:
            return self._entries[key]
        except KeyError as exc:
            raise ValueError(f"Unknown project: {key}") from exc

    def contains(self, key: str) -> bool:
        self.refresh()
        return key in self._entries

    def root(self, key: str) -> Path:
        root = self.get(key).path.resolve(strict=True)
        if not root.is_dir():
            raise ValueError(f"Project root is not a directory: {key}")
        return root
