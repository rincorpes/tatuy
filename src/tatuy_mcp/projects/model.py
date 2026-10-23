from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

ProjectKind = Literal["engine", "experiment", "game", "project"]
TargetKind = Literal["experiment", "game", "project"]
ProjectTatuySource = Literal["local", "pypi"]


@dataclass(frozen=True, slots=True)
class ProjectEntry:
    key: str
    name: str
    kind: ProjectKind
    path: Path
