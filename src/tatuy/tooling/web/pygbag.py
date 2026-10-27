"""Pygbag process adapter used by Tatuy web-target tooling."""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, Sequence


class BrowserPackager(Protocol):
    """Build one staged target into static browser output."""

    def build(self, staging: Path) -> None:
        """Build static browser output for ``staging``."""


@dataclass(frozen=True, slots=True)
class PygbagPackager:
    """Invoke Pygbag as an interchangeable browser-packaging backend.

    Attributes:
        command: Command prefix used to launch Pygbag.
        python_build: CPython runtime version requested from Pygbag.
        ume_block: Pygbag cooperative blocking mode value.
    """

    command: tuple[str, ...] = (sys.executable, "-m", "pygbag")
    python_build: str = "3.12"
    ume_block: int = 0

    def build(self, staging: Path) -> None:
        """Build one staged Tatuy target into static Pygbag output.

        Args:
            staging: Prepared Pygbag project directory.

        Returns:
            None.

        Raises:
            subprocess.CalledProcessError: Pygbag exits unsuccessfully.
        """
        subprocess.run(
            [
                *self.command,
                "--PYBUILD",
                self.python_build,
                "--ume_block",
                str(self.ume_block),
                "--build",
                str(staging),
            ],
            check=True,
        )


def command_tuple(command: Sequence[str]) -> tuple[str, ...]:
    """Normalize a command sequence for ``PygbagPackager`` construction."""
    return tuple(str(part) for part in command)
