from __future__ import annotations

from mcp.server import MCPServer

from tatuy_mcp.context import MCPContext
from tatuy_mcp.projects.model import ProjectTatuySource, TargetKind


def register_scaffolding_tools(
    server: MCPServer,
    context: MCPContext,
) -> None:
    @server.tool()
    def create_tatuy_target(
        kind: TargetKind,
        name: str,
        description: str = "",
        tags: list[str] | None = None,
        tatuy_source: ProjectTatuySource | None = None,
        tatuy_version: str | None = None,
        showcase: bool = False,
    ) -> dict[str, object]:
        """Create a Tatuy experiment, reference game, or project."""
        return context.scaffolding.create_target(
            kind=kind,
            name=name,
            description=description,
            tags=tags or (),
            tatuy_source=tatuy_source,
            tatuy_version=tatuy_version,
            showcase=showcase,
        )
