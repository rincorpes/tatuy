from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True, slots=True)
class MCPConfig:
    engine_root: Path
    projects_root: Path
    command_timeout_seconds: int = 120
    max_command_output: int = 30_000
    max_command_paths: int = 25
    max_file_bytes: int = 1_000_000
    max_read_output: int = 30_000


def load_config() -> MCPConfig:
    load_dotenv()
    engine_root = Path(os.getenv("TATUY_ENGINE_PATH", "path/to/engine"))
    projects_root = Path(
        os.getenv("TATUY_PROJECTS_PATH", str(engine_root.parent))
    )
    return MCPConfig(
        engine_root=engine_root,
        projects_root=projects_root,
    )
