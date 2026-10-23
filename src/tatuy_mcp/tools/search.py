from __future__ import annotations

from mcp.server import MCPServer

from tatuy_mcp.context import MCPContext


def register_search_tools(server: MCPServer, context: MCPContext) -> None:
    @server.tool()
    def search_code(
        project: str,
        query: str,
        directory: str = ".",
        case_sensitive: bool = False,
    ) -> dict[str, object]:
        """Find literal text in project source and documentation files."""
        return context.search.search_text(
            project,
            query,
            directory=directory,
            case_sensitive=case_sensitive,
        )
