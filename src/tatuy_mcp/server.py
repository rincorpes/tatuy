from __future__ import annotations

from mcp.server import MCPServer

from tatuy_mcp.config import load_config
from tatuy_mcp.context import create_context
from tatuy_mcp.tools import register_tools
from tatuy_mcp.tools.info import MCP_SERVER_NAME


def create_server() -> MCPServer:
    config = load_config()
    context = create_context(config)
    server = MCPServer(MCP_SERVER_NAME)
    register_tools(server, context)
    return server


mcp = create_server()


if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="127.0.0.1",
        port=8000,
    )
