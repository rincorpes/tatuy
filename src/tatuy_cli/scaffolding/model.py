from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal


TargetKind = Literal["experiment", "game", "project"]
TatuySource = Literal["workspace", "local", "pypi"]


@dataclass(frozen=True, slots=True)
class CreateTargetRequest:
    kind: TargetKind
    name: str
    description: str = ""
    tags: tuple[str, ...] = ()
    destination: Path | None = None
    tatuy_source: TatuySource | None = None
    tatuy_version: str | None = None
    showcase: bool = False


@dataclass(frozen=True, slots=True)
class CreatedTarget:
    kind: TargetKind
    name: str
    path: Path
    manifest_path: Path
    run_command: str
