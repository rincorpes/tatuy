from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

THIS_FILE = Path(__file__).resolve()
EXAMPLES_ROOT = THIS_FILE.parent.parent.parent.parent.parent / "examples"


@dataclass
class RunTargetInput:
    name: str
    category: str
    examples_path: Path = field(default_factory=lambda: EXAMPLES_ROOT)
