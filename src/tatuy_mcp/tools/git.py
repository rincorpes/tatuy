"""MCP tool registration for guarded Git operations."""

from __future__ import annotations

from mcp.server import MCPServer

from tatuy_mcp.context import MCPContext


def register_git_tools(server: MCPServer, context: MCPContext) -> None:
    """Register guarded Git review and commit tools."""

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
