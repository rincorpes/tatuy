from __future__ import annotations

from mcp.server import MCPServer

from tatuy_mcp.context import MCPContext

MCP_SERVER_NAME = "Tatuy Development"


def register_info_tools(server: MCPServer, _: MCPContext) -> None:
    @server.tool()
    def server_info() -> dict[str, str]:
        """Describe this local game development server."""
        return {"name": MCP_SERVER_NAME, "status": "ready"}
