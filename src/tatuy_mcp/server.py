from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from mcp.server import MCPServer

from tatuy_cli.scaffolding.model import CreateTargetRequest
from tatuy_cli.scaffolding.service import TargetScaffolder
from tatuy_mcp.projects import ProjectEntry, discover_projects

load_dotenv()

mcp = MCPServer("Game Development")

TargetKind = Literal[
    "experiment",
    "game",
    "project",
]

ProjectTatuySource = Literal[
    "local",
    "pypi",
]

ENGINE_ROOT = Path(
    os.getenv(
        "TATUY_ENGINE_PATH",
        "path/to/engine",
    )
)

PROJECTS_ROOT = Path(
    os.getenv(
        "TATUY_PROJECTS_PATH",
        str(ENGINE_ROOT.parent),
    )
)

PROJECTS: dict[str, Path] = {}
PROJECT_ENTRIES: dict[str, ProjectEntry] = {}

BLOCKED_DIRECTORIES = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    "build",
    "dist",
}

BLOCKED_FILENAMES = {
    "credentials.json",
    "secrets.json",
}

BLOCKED_EXTENSIONS = {
    ".pem",
    ".key",
    ".p12",
    ".pfx",
}


def refresh_projects() -> list[ProjectEntry]:
    entries = discover_projects(
        engine_root=ENGINE_ROOT,
        projects_root=PROJECTS_ROOT,
    )

    PROJECTS.clear()
    PROJECTS.update({entry.key: entry.path for entry in entries})

    PROJECT_ENTRIES.clear()
    PROJECT_ENTRIES.update({entry.key: entry for entry in entries})

    return entries


def check_access(relative_path: Path) -> None:
    """Reject paths excluded from the development tools."""
    parts = [part.casefold() for part in relative_path.parts]

    if any(part in BLOCKED_DIRECTORIES for part in parts):
        raise ValueError("Path belongs to an excluded directory")

    name = relative_path.name.casefold()

    if name.startswith(".env") or name in BLOCKED_FILENAMES:
        raise ValueError("File is excluded from project access")

    if relative_path.suffix.casefold() in BLOCKED_EXTENSIONS:
        raise ValueError("File type is excluded from project access")


@mcp.tool()
def list_projects() -> list[dict[str, str | bool]]:
    """List configured engine and game projects and their availability."""

    entries = refresh_projects()

    return [
        {
            "key": entry.key,
            "name": entry.name,
            "kind": entry.kind,
            "path": str(entry.path),
            "available": entry.path.is_dir(),
        }
        for entry in entries
    ]


def resolve_project_path(
    project: str,
    relative_path: str = ".",
) -> Path:
    """Resolve an existing, permitted path inside a project."""

    refresh_projects()

    if project not in PROJECTS:
        raise ValueError(f"Unknown project: {project}")

    root = PROJECTS[project].resolve(strict=True)

    if not root.is_dir():
        raise ValueError(f"Project root is not a directory: {project}")

    requested = Path(relative_path)

    if requested.is_absolute() or requested.drive or requested.root:
        raise ValueError("Provide a project-relative path")

    # Check the requested name and the resolved destination.
    check_access(requested)

    target = (root / requested).resolve(strict=True)

    if not target.is_relative_to(root):
        raise ValueError("Path points outside the selected project")

    check_access(target.relative_to(root))

    return target


@mcp.tool()
def list_files(
    project: str,
    directory: str = ".",
) -> dict[str, object]:
    """List immediate children of a project-relative directory."""
    target = resolve_project_path(project, directory)

    if not target.is_dir():
        raise ValueError("Requested path is not a directory")

    entries = []

    for child in sorted(
        target.iterdir(),
        key=lambda item: item.name.casefold(),
    ):
        # Omit links whose destinations leave the project.
        try:
            resolved = resolve_project_path(
                project,
                str(Path(directory) / child.name),
            )
        except (ValueError, OSError, RuntimeError):
            continue

        entries.append(
            {
                "name": child.name,
                "type": ("directory" if resolved.is_dir() else "file"),
            }
        )

    return {
        "project": project,
        "directory": directory,
        "entries": entries,
    }


@mcp.tool()
def read_file(
    project: str,
    path: str,
    start_line: int = 1,
    end_line: int = 200,
) -> dict[str, object]:
    """Read an inclusive range of lines from a UTF-8 project file."""
    if start_line < 1 or end_line < start_line:
        raise ValueError("Provide a valid line range starting at 1")

    if end_line - start_line + 1 > 300:
        raise ValueError("Read at most 300 lines per request")

    target = resolve_project_path(project, path)

    if not target.is_file():
        raise ValueError("Requested path is not a file")

    # Bound memory use, including files that contain very long lines.
    max_bytes = 1_000_000

    with target.open("rb") as source:
        data = source.read(max_bytes + 1)

    if len(data) > max_bytes:
        raise ValueError("File exceeds the 1 MB reading limit")

    if b"\x00" in data:
        raise ValueError("File appears to contain binary data")

    try:
        lines = data.decode("utf-8-sig").splitlines()
    except UnicodeDecodeError as exc:
        raise ValueError("File is not valid UTF-8 text") from exc

    selected = lines[start_line - 1 : end_line]
    content = "\n".join(
        f"{number}: {line}"
        for number, line in enumerate(selected, start=start_line)
    )

    if len(content) > 30_000:
        raise ValueError("Output is too large; request fewer lines")

    return {
        "project": project,
        "path": path,
        "total_lines": len(lines),
        "start_line": start_line,
        "end_line": (start_line + len(selected) - 1 if selected else None),
        "has_more": end_line < len(lines),
        "content": content,
    }


EXCLUDED_DIRECTORIES = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    "build",
    "dist",
}

SOURCE_EXTENSIONS = {
    ".py",
    ".toml",
    ".md",
    ".json",
    ".yaml",
    ".yml",
    ".txt",
    ".glsl",
    ".vert",
    ".frag",
}


def is_searchable(path: Path) -> bool:
    """Select source and documentation files for searching."""
    name = path.name.casefold()

    if name.startswith(".env"):
        return False

    return path.suffix.casefold() in SOURCE_EXTENSIONS


@mcp.tool()
def search_code(
    project: str,
    query: str,
    directory: str = ".",
    case_sensitive: bool = False,
) -> dict[str, object]:
    """Find literal text in project source and documentation files."""
    if not query.strip():
        raise ValueError("Search query must not be empty")

    if len(query) > 500:
        raise ValueError("Search query must not exceed 500 characters")

    root = resolve_project_path(project)
    target = resolve_project_path(project, directory)

    if not target.is_dir():
        raise ValueError("Requested path is not a directory")

    needle = query if case_sensitive else query.casefold()
    matches = []
    scanned_files = 0
    skipped_files = 0
    truncated = False

    def walk_error(error: OSError) -> None:
        raise ValueError("Cannot traverse a project directory") from error

    for current, directories, filenames in os.walk(
        target,
        followlinks=False,
        onerror=walk_error,
    ):
        directories[:] = sorted(
            name
            for name in directories
            if name.casefold() not in BLOCKED_DIRECTORIES
            and not (Path(current) / name).is_symlink()
        )

        for filename in sorted(filenames):
            candidate = Path(current) / filename

            if candidate.is_symlink() or not is_searchable(candidate):
                continue

            if scanned_files >= 2_000:
                truncated = True
                break

            scanned_files += 1

            try:
                relative = candidate.relative_to(root)
                candidate = resolve_project_path(
                    project,
                    str(relative),
                )

                with candidate.open("rb") as source:
                    data = source.read(1_000_001)

                if len(data) > 1_000_000 or b"\x00" in data:
                    skipped_files += 1
                    continue

                text = data.decode("utf-8-sig")
            except (OSError, ValueError, UnicodeError):
                skipped_files += 1
                continue

            for number, line in enumerate(text.splitlines(), start=1):
                searchable = line if case_sensitive else line.casefold()

                if needle in searchable:
                    if len(matches) >= 50:
                        truncated = True
                        break

                    matches.append(
                        {
                            "path": relative.as_posix(),
                            "line": number,
                            "text": line[:500],
                            "line_truncated": len(line) > 500,
                        }
                    )

            if truncated:
                break

        if truncated:
            break

    return {
        "project": project,
        "query": query,
        "matches": matches,
        "scanned_files": scanned_files,
        "skipped_files": skipped_files,
        "truncated": truncated,
    }


@mcp.tool()
def create_tatuy_target(
    kind: TargetKind,
    name: str,
    description: str = "",
    tags: list[str] | None = None,
    tatuy_source: ProjectTatuySource | None = None,
    tatuy_version: str | None = None,
) -> dict[str, object]:
    """
    Create a Tatuy experiment, reference game, or standalone project.

    Experiments are created under examples/experiments and always use
    the current Tatuy workspace.

    Games are created under examples/games and always use the current
    Tatuy workspace.

    Standalone projects are created inside TATUY_PROJECTS_PATH and may
    use either the local Tatuy repository or a PyPI release.
    """

    refresh_projects()

    expected_key = f"{kind}:{name}"

    if expected_key in PROJECTS:
        raise ValueError(f"Target is already registered: {expected_key}")

    if kind in {"experiment", "game"}:
        tatuy_source = "workspace"
        tatuy_version = None

    request = CreateTargetRequest(
        kind=kind,
        name=name,
        description=description,
        tags=tuple(tags or ()),
        tatuy_source=tatuy_source,
        tatuy_version=tatuy_version,
    )

    result = TargetScaffolder(
        engine_root=ENGINE_ROOT.resolve(strict=True),
        projects_root=PROJECTS_ROOT,
        restrict_projects_to_root=True,
    ).create(request)

    refresh_projects()

    key = f"{result.kind}:{result.name}"

    return {
        "created": True,
        "key": key,
        "kind": result.kind,
        "name": result.name,
        "path": str(result.path),
        "manifest": str(result.manifest_path),
        "run_command": result.run_command,
    }


@mcp.tool()
def server_info() -> dict[str, str]:
    """Describe this local game development server."""
    return {
        "name": "Game Development",
        "status": "ready",
    }


if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="127.0.0.1",
        port=8000,
    )
