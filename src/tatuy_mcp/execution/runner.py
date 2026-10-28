from __future__ import annotations

import os
import subprocess
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

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


@dataclass(frozen=True, slots=True)
class CommandResult:
    completed: bool
    timed_out: bool
    exit_code: int | None
    stdout: str
    stderr: str
    stdout_truncated: bool
    stderr_truncated: bool

    def as_dict(self) -> dict[str, object]:
        return {
            "completed": self.completed,
            "timed_out": self.timed_out,
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "stdout_truncated": self.stdout_truncated,
            "stderr_truncated": self.stderr_truncated,
        }


class CommandRunner:
    def __init__(
        self,
        *,
        timeout_seconds: int,
        max_output: int,
    ) -> None:
        self._timeout_seconds = timeout_seconds
        self._max_output = max_output

    def run(
        self,
        command: Sequence[str],
        *,
        cwd: Path,
    ) -> CommandResult:
        try:
            completed = subprocess.run(
                list(command),
                cwd=cwd,
                env=build_subprocess_environment(),
                capture_output=True,
                text=True,
                timeout=self._timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return CommandResult(
                completed=False,
                timed_out=True,
                exit_code=None,
                stdout="",
                stderr=(
                    "Command exceeded the "
                    f"{self._timeout_seconds}-second timeout."
                ),
                stdout_truncated=False,
                stderr_truncated=False,
            )

        stdout, stdout_truncated = truncate_output(
            completed.stdout,
            self._max_output,
        )
        stderr, stderr_truncated = truncate_output(
            completed.stderr,
            self._max_output,
        )
        return CommandResult(
            completed=True,
            timed_out=False,
            exit_code=completed.returncode,
            stdout=stdout,
            stderr=stderr,
            stdout_truncated=stdout_truncated,
            stderr_truncated=stderr_truncated,
        )


def build_subprocess_environment() -> dict[str, str]:
    environment = {
        key: value
        for key, value in os.environ.items()
        if key.upper() in SAFE_SUBPROCESS_ENVIRONMENT
    }
    environment["PYTHONUTF8"] = "1"
    return environment


def truncate_output(value: str | None, limit: int) -> tuple[str, bool]:
    normalized = value or ""
    if len(normalized) <= limit:
        return normalized, False
    return normalized[:limit], True
