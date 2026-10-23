"""Guarded Git operations for Tatuy development projects."""

from __future__ import annotations

import difflib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from tatuy_mcp.access.paths import ProjectPathResolver
from tatuy_mcp.execution.runner import CommandResult, CommandRunner
from tatuy_mcp.projects.registry import ProjectRegistry

_CONVENTIONAL_COMMIT = re.compile(
    r"^(feat|fix|docs|chore|refactor|test|perf|build|ci|style|revert): "
    r"[^\r\n]+$"
)


@dataclass(frozen=True, slots=True)
class GitFileChange:
    """One changed path reported by Git status."""

    path: str
    status: str
    staged: bool

    def as_dict(self) -> dict[str, object]:
        """Serialize the change for MCP responses."""
        return {
            "path": self.path,
            "status": self.status,
            "staged": self.staged,
        }


class GitWorkspace:
    """Expose guarded Git operations for one configured project."""

    def __init__(
        self,
        projects: ProjectRegistry,
        paths: ProjectPathResolver,
        commands: CommandRunner,
        *,
        max_paths: int,
    ) -> None:
        self._projects = projects
        self._paths = paths
        self._commands = commands
        self._max_paths = max_paths

    def status(self, project: str) -> dict[str, object]:
        """Return the current branch and working-tree changes."""
        root = self._git_root(project)
        result = self._run(
            root,
            "status",
            "--porcelain=v1",
            "--branch",
            "--untracked-files=all",
        )
        self._require_success(result, "git status")
        branch = ""
        changes: list[GitFileChange] = []
        for line in result.stdout.splitlines():
            if line.startswith("## "):
                branch = line[3:].split("...", 1)[0]
                continue
            if len(line) < 4:
                continue
            index_status = line[0]
            path = line[3:]
            if " -> " in path:
                path = path.split(" -> ", 1)[1]
            status = "untracked" if line.startswith("??") else line[:2].strip()
            changes.append(
                GitFileChange(
                    path=path,
                    status=status,
                    staged=index_status not in {" ", "?"},
                )
            )
        return {
            "branch": branch,
            "clean": not changes,
            "files": [change.as_dict() for change in changes],
        }

    def snapshot(self, project: str) -> dict[str, object]:
        """Return compact per-file change counts for review UIs."""
        status = self.status(project)
        root = self._git_root(project)
        stats = self._numstat(root)

        files: list[dict[str, object]] = []
        total_additions = 0
        total_deletions = 0
        status_files = cast(list[dict[str, object]], status["files"])
        for item in status_files:
            path = str(item["path"])
            additions, deletions = stats.get(path, (0, 0))
            if item["status"] == "untracked":
                additions = self._count_file_lines(root / path)
            total_additions += additions
            total_deletions += deletions
            files.append(
                {
                    **item,
                    "additions": additions,
                    "deletions": deletions,
                }
            )
        return {
            "branch": status["branch"],
            "clean": status["clean"],
            "files": files,
            "totals": {
                "files": len(files),
                "additions": total_additions,
                "deletions": total_deletions,
            },
        }

    def diff(
        self,
        project: str,
        *,
        path: str | None = None,
        staged: bool = False,
        context: int = 3,
    ) -> dict[str, object]:
        """Return a tracked or synthesized untracked unified diff."""
        if context < 0 or context > 20:
            raise ValueError("Diff context must be between 0 and 20 lines")
        root = self._git_root(project)
        args = ["diff", f"--unified={context}"]
        if staged:
            args.append("--cached")
        if path is not None:
            target = self._paths.resolve_existing(project, path)
            relative = target.relative_to(root).as_posix()
            if not staged and self._is_untracked(root, relative):
                return {
                    "path": relative,
                    "staged": False,
                    "diff": self._untracked_diff(target, relative, context),
                }
            args.extend(["--", relative])
        result = self._run(root, *args)
        self._require_success(result, "git diff")
        diff_text = result.stdout
        if path is None and not staged:
            status_files = cast(
                list[dict[str, object]],
                self.status(project)["files"],
            )
            for item in status_files:
                if item["status"] != "untracked":
                    continue
                relative = str(item["path"])
                target = self._paths.resolve_existing(project, relative)
                diff_text += self._untracked_diff(target, relative, context)
        return {
            "path": path,
            "staged": staged,
            "diff": diff_text,
            "truncated": result.stdout_truncated,
        }

    def stage(self, project: str, paths: list[str]) -> dict[str, object]:
        """Stage selected validated project-relative paths."""
        root = self._git_root(project)
        resolved = self._resolve_paths(project, paths, root)
        result = self._run(root, "add", "--", *resolved)
        self._require_success(result, "git add")
        return {"staged": resolved}

    def commit(self, project: str, message: str) -> dict[str, object]:
        """Commit staged changes using a validated Conventional Commit subject."""
        normalized = message.strip()
        if len(normalized) > 72:
            raise ValueError("Commit message must be 72 characters or fewer")
        if not _CONVENTIONAL_COMMIT.fullmatch(normalized):
            raise ValueError(
                "Commit message must be short and use a conventional prefix "
                "such as feat:, fix:, docs:, chore:, refactor:, or test:."
            )
        root = self._git_root(project)
        result = self._run(root, "commit", "-m", normalized)
        self._require_success(result, "git commit")
        head = self._run(root, "rev-parse", "--short", "HEAD")
        self._require_success(head, "git rev-parse")
        return {
            "message": normalized,
            "commit": head.stdout.strip(),
            "output": result.stdout.strip(),
        }

    def log(self, project: str, *, limit: int = 10) -> dict[str, object]:
        """Return recent commit hashes and subjects."""
        if limit < 1 or limit > 50:
            raise ValueError("Git log limit must be between 1 and 50")
        root = self._git_root(project)
        result = self._run(
            root,
            "log",
            f"-{limit}",
            "--pretty=format:%h%x09%s",
        )
        self._require_success(result, "git log")
        entries = []
        for line in result.stdout.splitlines():
            commit, _, subject = line.partition("\t")
            entries.append({"commit": commit, "message": subject})
        return {"entries": entries}

    def _git_root(self, project: str) -> Path:
        root = self._projects.root(project)
        result = self._run(root, "rev-parse", "--show-toplevel")
        self._require_success(result, "git rev-parse")
        git_root = Path(result.stdout.strip()).resolve(strict=True)
        if git_root != root:
            raise ValueError(
                "Selected project must be the Git repository root"
            )
        return root

    def _resolve_paths(
        self,
        project: str,
        paths: list[str],
        root: Path,
    ) -> list[str]:
        if not paths:
            raise ValueError("Provide at least one project-relative path")
        if len(paths) > self._max_paths:
            raise ValueError(f"Provide at most {self._max_paths} paths")
        resolved: list[str] = []
        for path in paths:
            try:
                target = self._paths.resolve_existing(project, path)
            except FileNotFoundError:
                target = self._paths.resolve_new(project, path)
            resolved.append(target.relative_to(root).as_posix())
        return resolved

    def _is_untracked(self, root: Path, path: str) -> bool:
        result = self._run(
            root, "ls-files", "--others", "--exclude-standard", "--", path
        )
        self._require_success(result, "git ls-files")
        return bool(result.stdout.strip())

    def _numstat(self, root: Path) -> dict[str, tuple[int, int]]:
        result = self._run(root, "diff", "--numstat", "HEAD")
        self._require_success(result, "git diff --numstat")
        stats: dict[str, tuple[int, int]] = {}
        for line in result.stdout.splitlines():
            parts = line.split("\t", 2)
            if len(parts) != 3:
                continue
            additions = int(parts[0]) if parts[0].isdigit() else 0
            deletions = int(parts[1]) if parts[1].isdigit() else 0
            stats[parts[2]] = (additions, deletions)
        return stats

    @staticmethod
    def _count_file_lines(path: Path) -> int:
        try:
            return len(path.read_text(encoding="utf-8").splitlines())
        except (OSError, UnicodeDecodeError):
            return 0

    @staticmethod
    def _untracked_diff(path: Path, relative: str, context: int) -> str:
        try:
            lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
        except UnicodeDecodeError:
            return f"Binary or non-UTF-8 untracked file: {relative}"
        return "".join(
            difflib.unified_diff(
                [],
                lines,
                fromfile="/dev/null",
                tofile=f"b/{relative}",
                n=context,
            )
        )

    def _run(self, root: Path, *args: str) -> CommandResult:
        return self._commands.run(["git", *args], cwd=root)

    @staticmethod
    def _require_success(result: CommandResult, operation: str) -> None:
        if result.completed and result.exit_code == 0:
            return
        detail = (
            result.stderr.strip() or result.stdout.strip() or "unknown error"
        )
        raise RuntimeError(f"{operation} failed: {detail}")
