from mcp.server import MCPServer

from tatuy_mcp.server import create_server


def test_create_server_returns_mcp_server() -> None:
    server = create_server()

    assert isinstance(server, MCPServer)
