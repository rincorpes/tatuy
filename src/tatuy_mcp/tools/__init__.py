from __future__ import annotations

from mcp.server import MCPServer

from tatuy_mcp.context import MCPContext
from tatuy_mcp.tools.files import register_file_tools
from tatuy_mcp.tools.git import register_git_tools
from tatuy_mcp.tools.info import register_info_tools
from tatuy_mcp.tools.projects import register_project_tools
from tatuy_mcp.tools.scaffolding import register_scaffolding_tools
from tatuy_mcp.tools.search import register_search_tools
from tatuy_mcp.tools.verification import register_verification_tools


def register_tools(server: MCPServer, context: MCPContext) -> None:
    register_info_tools(server, context)
    register_project_tools(server, context)
    register_file_tools(server, context)
    register_git_tools(server, context)
    register_search_tools(server, context)
    register_scaffolding_tools(server, context)
    register_verification_tools(server, context)


__all__ = ["register_tools"]
