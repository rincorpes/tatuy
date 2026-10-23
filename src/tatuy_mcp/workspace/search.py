from __future__ import annotations

import os
from pathlib import Path

from tatuy_mcp.access.paths import ProjectPathResolver
from tatuy_mcp.access.policy import AccessPolicy


class WorkspaceSearch:
    def __init__(
        self,
        paths: ProjectPathResolver,
        policy: AccessPolicy,
        *,
        max_file_bytes: int,
    ) -> None:
        self._paths = paths
        self._policy = policy
        self._max_file_bytes = max_file_bytes

    def search_text(
        self,
        project: str,
        query: str,
        *,
        directory: str = ".",
        case_sensitive: bool = False,
        max_matches: int = 50,
        max_files: int = 2_000,
    ) -> dict[str, object]:
        if not query.strip():
            raise ValueError("Search query must not be empty")
        if len(query) > 500:
            raise ValueError("Search query must not exceed 500 characters")

        root = self._paths.resolve_existing(project)
        target = self._paths.resolve_existing(project, directory)
        if not target.is_dir():
            raise ValueError("Requested path is not a directory")

        needle = query if case_sensitive else query.casefold()
        matches: list[dict[str, object]] = []
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
                if name.casefold() not in self._policy.blocked_directories
                and not (Path(current) / name).is_symlink()
            )

            for filename in sorted(filenames):
                candidate = Path(current) / filename
                if candidate.is_symlink() or not self._policy.is_searchable(
                    candidate
                ):
                    continue
                if scanned_files >= max_files:
                    truncated = True
                    break

                scanned_files += 1
                try:
                    relative = candidate.relative_to(root)
                    candidate = self._paths.resolve_existing(
                        project,
                        str(relative),
                    )
                    with candidate.open("rb") as source:
                        data = source.read(self._max_file_bytes + 1)
                    if len(data) > self._max_file_bytes or b"\x00" in data:
                        skipped_files += 1
                        continue
                    text = data.decode("utf-8-sig")
                except (OSError, ValueError, UnicodeError):
                    skipped_files += 1
                    continue

                for number, line in enumerate(text.splitlines(), start=1):
                    searchable = line if case_sensitive else line.casefold()
                    if needle not in searchable:
                        continue
                    if len(matches) >= max_matches:
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
