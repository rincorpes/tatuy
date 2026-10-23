"""Engine configuration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class EngineConfig:
    """Configure core engine execution."""

    start_scene: str = "main"
    fps: int = 60
    debug_overlay: bool = False

    @classmethod
    def from_dict(cls, config: dict[str, Any]) -> EngineConfig:
        """Build engine configuration from a dictionary."""
        return cls(**config)
