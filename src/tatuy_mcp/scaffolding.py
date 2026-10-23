from __future__ import annotations

from collections.abc import Sequence

from tatuy_cli.scaffolding.model import CreateTargetRequest, TatuySource
from tatuy_cli.scaffolding.service import TargetScaffolder
from tatuy_mcp.config import MCPConfig
from tatuy_mcp.projects.model import ProjectTatuySource, TargetKind
from tatuy_mcp.projects.registry import ProjectRegistry


class TatuyScaffolding:
    def __init__(
        self,
        config: MCPConfig,
        registry: ProjectRegistry,
    ) -> None:
        self._config = config
        self._registry = registry

    def create_target(
        self,
        *,
        kind: TargetKind,
        name: str,
        description: str = "",
        tags: Sequence[str] = (),
        tatuy_source: ProjectTatuySource | None = None,
        tatuy_version: str | None = None,
    ) -> dict[str, object]:
        expected_key = f"{kind}:{name}"
        if self._registry.contains(expected_key):
            raise ValueError(f"Target is already registered: {expected_key}")

        source: TatuySource | None = tatuy_source
        if kind in {"experiment", "game"}:
            source = "workspace"
            tatuy_version = None

        request = CreateTargetRequest(
            kind=kind,
            name=name,
            description=description,
            tags=tuple(tags),
            tatuy_source=source,
            tatuy_version=tatuy_version,
        )
        result = TargetScaffolder(
            engine_root=self._config.engine_root.resolve(strict=True),
            projects_root=self._config.projects_root,
            restrict_projects_to_root=True,
        ).create(request)
        self._registry.refresh()
        key = f"{result.kind}:{result.name}"
        return {
            "created": True,
            "key": key,
            "kind": result.kind,
            "name": result.name,
            "path": str(result.path),
            "manifest": str(result.manifest_path),
            "run_command": result.run_command,
        }
