from __future__ import annotations

import hashlib
import os
import subprocess
import sys
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from mcp.server import MCPServer

from tatuy_cli.scaffolding.model import CreateTargetRequest
from tatuy_cli.scaffolding.service import TargetScaffolder
from tatuy_mcp.projects import ProjectEntry, discover_projects

load_dotenv()

MCP_SERVER_NAME = "Tatuy Development"
mcp = MCPServer(MCP_SERVER_NAME)

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
        "sha256": hashlib.sha256(data).hexdigest(),
        "content": content,
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
        "name": MCP_SERVER_NAME,
        "status": "ready",
    }


def resolve_new_project_path(
    project: str,
    relative_path: str,
) -> Path:
    """Resolve a permitted new path inside a project."""

    refresh_projects()

    if project not in PROJECTS:
        raise ValueError(f"Unknown project: {project}")

    root = PROJECTS[project].resolve(strict=True)

    requested = Path(relative_path)

    if requested.is_absolute() or requested.drive or requested.root:
        raise ValueError("Provide a project-relative path")

    check_access(requested)

    target = (root / requested).resolve(strict=False)

    if not target.is_relative_to(root):
        raise ValueError("Path points outside the selected project")

    check_access(target.relative_to(root))

    parent = target.parent.resolve(strict=True)

    if not parent.is_relative_to(root):
        raise ValueError(
            "Parent directory points outside the selected project"
        )

    if target.exists():
        raise ValueError(f"Path already exists: {relative_path}")

    return target


WRITABLE_EXTENSIONS = {
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

WRITABLE_FILENAMES = {
    ".gitignore",
}


def check_writable_file(path: Path) -> None:
    if (
        path.suffix.casefold() not in WRITABLE_EXTENSIONS
        and path.name not in WRITABLE_FILENAMES
    ):
        raise ValueError(f"File type is not writable through MCP: {path.name}")


@mcp.tool()
def create_file(
    project: str,
    path: str,
    content: str,
) -> dict[str, object]:
    """
    Create a new UTF-8 text file inside a Tatuy development project.

    Use only when the user explicitly asks Tatuy Development to create,
    implement, save, or apply code or documentation changes.

    Refuses to overwrite existing files.
    """

    target = resolve_new_project_path(
        project,
        path,
    )

    check_writable_file(target)

    encoded = content.encode("utf-8")

    if len(encoded) > 1_000_000:
        raise ValueError("File exceeds the 1 MB writing limit")

    target.write_text(
        content,
        encoding="utf-8",
    )

    data = target.read_bytes()

    return {
        "created": True,
        "project": project,
        "path": path,
        "sha256": hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
    }


COMMAND_TIMEOUT_SECONDS = 120
MAX_COMMAND_OUTPUT = 30_000
MAX_COMMAND_PATHS = 25

SAFE_SUBPROCESS_ENVIRONMENT = {
    "APPDATA",
    "COMSPEC",
    "HOME",
    "LOCALAPPDATA",
    "PATH",
    "PATHEXT",
    "SYSTEMDRIVE",
    "SYSTEMROOT",
    "TEMP",
    "TMP",
    "USERPROFILE",
    "VIRTUAL_ENV",
    "WINDIR",
}


def build_subprocess_environment() -> dict[str, str]:
    environment = {
        key: value
        for key, value in os.environ.items()
        if key.upper() in SAFE_SUBPROCESS_ENVIRONMENT
    }

    environment["PYTHONUTF8"] = "1"

    return environment


def truncate_command_output(value: str) -> tuple[str, bool]:
    if len(value) <= MAX_COMMAND_OUTPUT:
        return value, False

    return value[:MAX_COMMAND_OUTPUT], True


def run_project_command(
    *,
    command: list[str],
    cwd: Path,
) -> dict[str, object]:
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            env=build_subprocess_environment(),
            capture_output=True,
            text=True,
            timeout=COMMAND_TIMEOUT_SECONDS,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {
            "completed": False,
            "timed_out": True,
            "exit_code": None,
            "stdout": "",
            "stderr": (
                "Command exceeded the "
                f"{COMMAND_TIMEOUT_SECONDS}-second timeout."
            ),
            "stdout_truncated": False,
            "stderr_truncated": False,
        }

    stdout, stdout_truncated = truncate_command_output(
        completed.stdout,
    )
    stderr, stderr_truncated = truncate_command_output(
        completed.stderr,
    )

    return {
        "completed": True,
        "timed_out": False,
        "exit_code": completed.returncode,
        "stdout": stdout,
        "stderr": stderr,
        "stdout_truncated": stdout_truncated,
        "stderr_truncated": stderr_truncated,
    }


def resolve_command_paths(
    project: str,
    paths: list[str],
) -> list[Path]:
    if not paths:
        raise ValueError("Provide at least one project-relative path")

    if len(paths) > MAX_COMMAND_PATHS:
        raise ValueError(f"Provide at most {MAX_COMMAND_PATHS} paths")

    resolved = []

    for path in paths:
        resolved.append(
            resolve_project_path(
                project,
                path,
            )
        )

    return resolved


@mcp.tool()
def format_python(
    project: str,
    paths: list[str],
) -> dict[str, object]:
    """
    Format selected Python files or directories using Tatuy's configured
    isort and Black tooling.

    Use only as part of a user-authorized implementation or when the user
    explicitly asks to format project code.

    Paths must remain inside the selected project.
    """

    root = resolve_project_path(project)
    targets = resolve_command_paths(
        project,
        paths,
    )

    for target in targets:
        if target.is_file() and target.suffix.casefold() != ".py":
            raise ValueError(
                "format_python accepts Python files or directories"
            )

    arguments = [str(target) for target in targets]

    isort_result = run_project_command(
        command=[
            sys.executable,
            "-m",
            "isort",
            *arguments,
        ],
        cwd=root,
    )

    if isort_result["exit_code"] != 0:
        return {
            "project": project,
            "paths": paths,
            "formatted": False,
            "isort": isort_result,
            "black": None,
        }

    black_result = run_project_command(
        command=[
            sys.executable,
            "-m",
            "black",
            *arguments,
        ],
        cwd=root,
    )

    return {
        "project": project,
        "paths": paths,
        "formatted": black_result["exit_code"] == 0,
        "isort": isort_result,
        "black": black_result,
    }


@mcp.tool()
def run_tests(
    project: str,
    paths: list[str] | None = None,
    keyword: str | None = None,
) -> dict[str, object]:
    """
    Run pytest for a selected Tatuy development project.

    Prefer the narrowest relevant test paths. If paths are omitted,
    tests/ is used when it exists; otherwise the project root is used.

    Tests execute project Python code in a sanitized environment that
    excludes MCP, tunnel, API, and unrelated server secrets.
    """

    root = resolve_project_path(project)

    if keyword is not None:
        keyword = keyword.strip()

        if not keyword:
            keyword = None
        elif len(keyword) > 200:
            raise ValueError("pytest keyword must not exceed 200 characters")

    if paths:
        targets = resolve_command_paths(
            project,
            paths,
        )
    else:
        tests = root / "tests"

        targets = [tests if tests.is_dir() else root]

    command = [
        sys.executable,
        "-m",
        "pytest",
        "-q",
        *(str(target) for target in targets),
    ]

    if keyword is not None:
        command.extend(
            [
                "-k",
                keyword,
            ]
        )

    result = run_project_command(
        command=command,
        cwd=root,
    )

    return {
        "project": project,
        "paths": paths,
        "keyword": keyword,
        "passed": (result["completed"] and result["exit_code"] == 0),
        "result": result,
    }


@mcp.tool()
def edit_file(
    project: str,
    path: str,
    old_text: str,
    new_text: str,
    expected_sha256: str,
) -> dict[str, object]:
    """
    Replace one exact text region in an existing UTF-8 project file.

    Use only when the user explicitly asks Tatuy Development to apply,
    implement, refactor, or otherwise modify project files.

    The expected SHA-256 must match the current file so edits cannot
    silently overwrite changes made since the file was inspected.
    """

    if not old_text:
        raise ValueError("old_text must not be empty")

    target = resolve_project_path(
        project,
        path,
    )

    if not target.is_file():
        raise ValueError("Requested path is not a file")

    check_writable_file(target)

    data = target.read_bytes()

    actual_sha256 = hashlib.sha256(data).hexdigest()

    if actual_sha256 != expected_sha256:
        raise ValueError(
            "File changed since it was inspected. "
            "Read the file again before editing."
        )

    if len(data) > 1_000_000:
        raise ValueError("File exceeds the 1 MB writing limit")

    if b"\x00" in data:
        raise ValueError("File appears to contain binary data")

    try:
        content = data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("File is not valid UTF-8 text") from exc

    occurrences = content.count(old_text)

    if occurrences == 0:
        raise ValueError("old_text was not found in the file")

    if occurrences > 1:
        raise ValueError(
            "old_text occurs more than once. "
            "Provide a more specific text region."
        )

    updated = content.replace(
        old_text,
        new_text,
        1,
    )

    encoded = updated.encode("utf-8")

    if len(encoded) > 1_000_000:
        raise ValueError("Updated file exceeds the 1 MB writing limit")

    target.write_text(
        updated,
        encoding="utf-8",
    )

    written = target.read_bytes()

    return {
        "updated": True,
        "project": project,
        "path": path,
        "previous_sha256": actual_sha256,
        "sha256": hashlib.sha256(written).hexdigest(),
        "bytes": len(written),
    }


def validate_python_analysis_targets(
    targets: list[Path],
    *,
    tool_name: str,
) -> None:
    """Require static-analysis targets to be Python files or directories."""

    for target in targets:
        if target.is_file() and target.suffix.casefold() != ".py":
            raise ValueError(
                f"{tool_name} accepts Python files or directories"
            )


@mcp.tool()
def run_mypy(
    project: str,
    paths: list[str] | None = None,
) -> dict[str, object]:
    """
    Run mypy static type analysis for a Tatuy development project.

    This is a diagnostic tool only. Findings should be inspected and
    explained before making non-trivial typing, API, suppression, or
    architectural changes.

    When paths are provided, analyze only those Python files or
    directories. When paths are omitted, allow mypy to use the targets
    configured by the selected project's configuration.

    The command executes in a sanitized environment that excludes MCP,
    tunnel, API, and unrelated server secrets.
    """

    root = resolve_project_path(project)

    command = [
        sys.executable,
        "-m",
        "mypy",
        "--show-error-codes",
    ]

    resolved_paths: list[str] | None = None

    if paths:
        targets = resolve_command_paths(
            project,
            paths,
        )

        validate_python_analysis_targets(
            targets,
            tool_name="run_mypy",
        )

        resolved_paths = [str(target.relative_to(root)) for target in targets]

        command.extend(resolved_paths)

    result = run_project_command(
        command=command,
        cwd=root,
    )

    return {
        "project": project,
        "paths": paths,
        "clean": (result["completed"] and result["exit_code"] == 0),
        "result": result,
    }


def pylint_status_categories(
    exit_code: object,
) -> list[str]:
    """
    Decode pylint's bit-encoded exit status.

    Pylint uses:
      1  fatal message
      2  error message
      4  warning message
      8  refactor message
      16 convention message
      32 usage error
    """

    if not isinstance(exit_code, int):
        return []

    categories = []

    flags = (
        (1, "fatal"),
        (2, "error"),
        (4, "warning"),
        (8, "refactor"),
        (16, "convention"),
        (32, "usage_error"),
    )

    for flag, name in flags:
        if exit_code & flag:
            categories.append(name)

    return categories


@mcp.tool()
def run_pylint(
    project: str,
    paths: list[str] | None = None,
) -> dict[str, object]:
    """
    Run pylint static analysis for a Tatuy development project.

    This is a diagnostic tool only. Findings should be inspected and
    explained before making non-trivial design, API, suppression,
    configuration, or architectural changes.

    When paths are provided, analyze only those Python files or
    directories.

    When paths are omitted, analyze src/ when it exists; otherwise
    analyze the selected project root.

    The command executes in a sanitized environment that excludes MCP,
    tunnel, API, and unrelated server secrets.
    """

    root = resolve_project_path(project)

    if paths:
        targets = resolve_command_paths(
            project,
            paths,
        )
    else:
        source_root = root / "src"

        targets = [source_root if source_root.is_dir() else root]

    validate_python_analysis_targets(
        targets,
        tool_name="run_pylint",
    )

    arguments = [
        ("." if target == root else str(target.relative_to(root)))
        for target in targets
    ]

    command = [
        sys.executable,
        "-m",
        "pylint",
        "--output-format=text",
        "--reports=no",
        "--score=no",
        *arguments,
    ]

    result = run_project_command(
        command=command,
        cwd=root,
    )

    return {
        "project": project,
        "paths": paths,
        "clean": (result["completed"] and result["exit_code"] == 0),
        "categories": pylint_status_categories(
            result["exit_code"],
        ),
        "result": result,
    }


if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="127.0.0.1",
        port=8000,
    )
