from __future__ import annotations

from mcp.server import MCPServer

from tatuy_mcp.context import MCPContext


def register_verification_tools(
    server: MCPServer,
    context: MCPContext,
) -> None:
    @server.tool()
    def format_python(
        project: str,
        paths: list[str],
    ) -> dict[str, object]:
        """Format selected Python files or directories."""
        return context.formatter.format(project, paths)

    @server.tool()
    def run_tests(
        project: str,
        paths: list[str] | None = None,
        keyword: str | None = None,
    ) -> dict[str, object]:
        """Run targeted pytest verification."""
        return context.tests.run(
            project,
            paths=paths,
            keyword=keyword,
        )

    @server.tool()
    def run_mypy(
        project: str,
        paths: list[str] | None = None,
    ) -> dict[str, object]:
        """Run diagnostic mypy analysis against non-test Python code."""
        return context.analysis.run_mypy(project, paths=paths)

    @server.tool()
    def run_pylint(
        project: str,
        paths: list[str] | None = None,
    ) -> dict[str, object]:
        """Run diagnostic pylint analysis against non-test Python code."""
        return context.analysis.run_pylint(project, paths=paths)
