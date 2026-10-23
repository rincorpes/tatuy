from __future__ import annotations

from mcp.server import MCPServer

from tatuy_mcp.context import MCPContext


def register_file_tools(server: MCPServer, context: MCPContext) -> None:
    @server.tool()
    def list_files(
        project: str,
        directory: str = ".",
    ) -> dict[str, object]:
        """List immediate children of a project-relative directory."""
        return context.files.list_directory(project, directory)

    @server.tool()
    def read_file(
        project: str,
        path: str,
        start_line: int = 1,
        end_line: int = 200,
    ) -> dict[str, object]:
        """Read an inclusive range of lines from a UTF-8 project file."""
        return context.files.read(
            project,
            path,
            start_line=start_line,
            end_line=end_line,
        )

    @server.tool()
    def create_file(
        project: str,
        path: str,
        content: str,
    ) -> dict[str, object]:
        """Create a new permitted UTF-8 project file."""
        return context.files.create_file(project, path, content)

    @server.tool()
    def edit_file(
        project: str,
        path: str,
        old_text: str,
        new_text: str,
        expected_sha256: str,
    ) -> dict[str, object]:
        """Replace one exact text region in an existing project file."""
        return context.files.edit_file(
            project,
            path,
            old_text=old_text,
            new_text=new_text,
            expected_sha256=expected_sha256,
        )

    @server.tool()
    def create_directory(
        project: str,
        path: str,
    ) -> dict[str, object]:
        """Create one directory inside a Tatuy development project."""
        return context.files.create_directory(project, path)

    @server.tool()
    def delete_path(
        project: str,
        path: str,
        expected_sha256: str | None = None,
    ) -> dict[str, object]:
        """Delete one permitted file or empty directory."""
        return context.files.delete(
            project,
            path,
            expected_sha256=expected_sha256,
        )
