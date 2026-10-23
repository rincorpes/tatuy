from __future__ import annotations

import hashlib

from tatuy_mcp.access.paths import ProjectPathResolver
from tatuy_mcp.access.policy import AccessPolicy


class WorkspaceFiles:
    def __init__(
        self,
        paths: ProjectPathResolver,
        policy: AccessPolicy,
        *,
        max_file_bytes: int,
        max_read_output: int,
    ) -> None:
        self._paths = paths
        self._policy = policy
        self._max_file_bytes = max_file_bytes
        self._max_read_output = max_read_output

    def list_directory(
        self,
        project: str,
        directory: str = ".",
    ) -> dict[str, object]:
        target = self._paths.resolve_existing(project, directory)
        if not target.is_dir():
            raise ValueError("Requested path is not a directory")

        entries = []
        for child in sorted(
            target.iterdir(),
            key=lambda item: item.name.casefold(),
        ):
            try:
                resolved = self._paths.resolve_existing(
                    project,
                    str(
                        child.relative_to(
                            self._paths.resolve_existing(project)
                        )
                    ),
                )
            except (ValueError, OSError, RuntimeError):
                continue
            entries.append(
                {
                    "name": child.name,
                    "type": "directory" if resolved.is_dir() else "file",
                }
            )

        return {
            "project": project,
            "directory": directory,
            "entries": entries,
        }

    def read(
        self,
        project: str,
        path: str,
        *,
        start_line: int = 1,
        end_line: int = 200,
    ) -> dict[str, object]:
        if start_line < 1 or end_line < start_line:
            raise ValueError("Provide a valid line range starting at 1")
        if end_line - start_line + 1 > 300:
            raise ValueError("Read at most 300 lines per request")

        target = self._paths.resolve_existing(project, path)
        if not target.is_file():
            raise ValueError("Requested path is not a file")

        data = self._read_bytes(target)
        lines = self._decode(data).splitlines()
        selected = lines[start_line - 1 : end_line]
        content = "\n".join(
            f"{number}: {line}"
            for number, line in enumerate(selected, start=start_line)
        )
        if len(content) > self._max_read_output:
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

    def create_file(
        self,
        project: str,
        path: str,
        content: str,
    ) -> dict[str, object]:
        target = self._paths.resolve_new(project, path)
        self._policy.check_writable_file(target)
        encoded = content.encode("utf-8")
        self._validate_size(encoded, "File")
        target.write_bytes(encoded)
        data = target.read_bytes()
        return {
            "created": True,
            "project": project,
            "path": path,
            "sha256": hashlib.sha256(data).hexdigest(),
            "bytes": len(data),
        }

    def edit_file(
        self,
        project: str,
        path: str,
        *,
        old_text: str,
        new_text: str,
        expected_sha256: str,
    ) -> dict[str, object]:
        if not old_text:
            raise ValueError("old_text must not be empty")

        target = self._paths.resolve_existing(project, path)
        if not target.is_file():
            raise ValueError("Requested path is not a file")
        self._policy.check_writable_file(target)

        data = self._read_bytes(target)
        actual_sha256 = hashlib.sha256(data).hexdigest()
        if actual_sha256 != expected_sha256:
            raise ValueError(
                "File changed since it was inspected. "
                "Read the file again before editing."
            )

        content = self._decode(data)
        occurrences = content.count(old_text)
        if occurrences == 0:
            raise ValueError("old_text was not found in the file")
        if occurrences > 1:
            raise ValueError(
                "old_text occurs more than once. "
                "Provide a more specific text region."
            )

        encoded = content.replace(old_text, new_text, 1).encode("utf-8")
        self._validate_size(encoded, "Updated file")
        target.write_bytes(encoded)
        written = target.read_bytes()
        return {
            "updated": True,
            "project": project,
            "path": path,
            "previous_sha256": actual_sha256,
            "sha256": hashlib.sha256(written).hexdigest(),
            "bytes": len(written),
        }

    def create_directory(
        self,
        project: str,
        path: str,
    ) -> dict[str, object]:
        target = self._paths.resolve_new(project, path)
        target.mkdir()
        return {"created": True, "project": project, "path": path}

    def delete(
        self,
        project: str,
        path: str,
        *,
        expected_sha256: str | None = None,
    ) -> dict[str, object]:
        target = self._paths.resolve_deletion(project, path)
        if target.is_file():
            self._policy.check_writable_file(target)
            if expected_sha256 is None:
                raise ValueError(
                    "File deletion requires expected_sha256 from read_file"
                )
            data = target.read_bytes()
            actual_sha256 = hashlib.sha256(data).hexdigest()
            if actual_sha256 != expected_sha256:
                raise ValueError(
                    "File changed since it was inspected. "
                    "Read the file again before deleting it."
                )
            target.unlink()
            return {
                "deleted": True,
                "project": project,
                "path": path,
                "type": "file",
                "previous_sha256": actual_sha256,
            }

        if target.is_dir():
            try:
                target.rmdir()
            except OSError as exc:
                raise ValueError(
                    "Directory is not empty or cannot be deleted. "
                    "Delete its contents explicitly first."
                ) from exc
            return {
                "deleted": True,
                "project": project,
                "path": path,
                "type": "directory",
            }

        raise ValueError("Requested path is not a file or directory")

    def _read_bytes(self, target) -> bytes:
        with target.open("rb") as source:
            data = source.read(self._max_file_bytes + 1)
        self._validate_size(data, "File")
        if b"\x00" in data:
            raise ValueError("File appears to contain binary data")
        return data

    @staticmethod
    def _decode(data: bytes) -> str:
        try:
            return data.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise ValueError("File is not valid UTF-8 text") from exc

    def _validate_size(self, data: bytes, label: str) -> None:
        if len(data) > self._max_file_bytes:
            raise ValueError(
                f"{label} exceeds the {self._max_file_bytes // 1_000_000} MB writing limit"
            )
