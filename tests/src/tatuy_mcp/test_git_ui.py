from __future__ import annotations

import asyncio

from tatuy_mcp.server import create_server
from tatuy_mcp.ui.git_review import (
    GIT_REVIEW_MIME_TYPE,
    GIT_REVIEW_RESOURCE_URI,
)


def test_git_review_tool_links_to_ui_resource() -> None:
    server = create_server()

    tools = asyncio.run(server.list_tools())
    review_tool = next(tool for tool in tools if tool.name == "git_review")

    assert review_tool.meta is not None
    assert review_tool.meta["ui"]["resourceUri"] == GIT_REVIEW_RESOURCE_URI
    assert review_tool.meta["openai/outputTemplate"] == GIT_REVIEW_RESOURCE_URI


def test_git_review_resource_serves_mcp_app_html() -> None:
    server = create_server()

    contents = list(asyncio.run(server.read_resource(GIT_REVIEW_RESOURCE_URI)))

    assert len(contents) == 1
    assert contents[0].mime_type == GIT_REVIEW_MIME_TYPE
    assert "git_snapshot" in contents[0].content
    assert "git_diff" in contents[0].content
    assert "ui/initialize" in contents[0].content
