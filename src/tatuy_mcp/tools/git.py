"""MCP tool registration for guarded Git operations."""

from __future__ import annotations

from mcp.server import MCPServer

from tatuy_mcp.context import MCPContext
from tatuy_mcp.ui.git_review import (
    GIT_REVIEW_HTML,
    GIT_REVIEW_MIME_TYPE,
    GIT_REVIEW_RESOURCE_URI,
)


def register_git_tools(server: MCPServer, context: MCPContext) -> None:
    """Register guarded Git review and commit tools."""

    @server.resource(
        GIT_REVIEW_RESOURCE_URI,
        name="tatuy-git-review",
        title="Tatuy Git Review",
        description="Interactive working-tree review for Tatuy projects.",
        mime_type=GIT_REVIEW_MIME_TYPE,
        meta={"ui": {"prefersBorder": True}},
    )
    def git_review_resource() -> str:
        """Return the Git review MCP App document."""
        return GIT_REVIEW_HTML

    @server.tool(
        title="Review Git changes",
        meta={
            "ui": {"resourceUri": GIT_REVIEW_RESOURCE_URI},
            "openai/outputTemplate": GIT_REVIEW_RESOURCE_URI,
        },
    )
    def git_review(project: str = "engine") -> dict[str, object]:
        """Render an interactive working-tree review for a project."""
        return {"project": project, **context.git.snapshot(project)}

    @server.tool()
    def git_status(project: str) -> dict[str, object]:
        """Return the current Git branch and changed files."""
        return context.git.status(project)

    @server.tool()
    def git_snapshot(project: str) -> dict[str, object]:
        """Return a compact Git change summary with per-file line counts."""
        return context.git.snapshot(project)

    @server.tool()
    def git_diff(
        project: str,
        path: str | None = None,
        staged: bool = False,
        context_lines: int = 3,
    ) -> dict[str, object]:
        """Return a Git diff, optionally limited to one project file."""
        return context.git.diff(
            project,
            path=path,
            staged=staged,
            context=context_lines,
        )

    @server.tool()
    def git_stage(project: str, paths: list[str]) -> dict[str, object]:
        """Stage selected project-relative paths for commit."""
        return context.git.stage(project, paths)

    @server.tool()
    def git_commit(project: str, message: str) -> dict[str, object]:
        """Commit staged changes with a short Conventional Commit message."""
        return context.git.commit(project, message)

    @server.tool()
    def git_log(project: str, limit: int = 10) -> dict[str, object]:
        """Return recent commit hashes and subjects."""
        return context.git.log(project, limit=limit)
