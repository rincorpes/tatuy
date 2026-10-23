from __future__ import annotations

from mcp.server import MCPServer

from tatuy_mcp.context import MCPContext


def register_project_tools(server: MCPServer, context: MCPContext) -> None:
    @server.tool()
    def list_projects() -> list[dict[str, str | bool]]:
        """List configured engine and game projects and their availability."""
        return [
            {
                "key": entry.key,
                "name": entry.name,
                "kind": entry.kind,
                "path": str(entry.path),
                "available": entry.path.is_dir(),
            }
            for entry in context.projects.list()
        ]
