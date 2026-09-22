from dataclasses import dataclass, field
from typing import Any

REPLAY_MAGIC = "tatuy-replay"
REPLAY_VERSION = 1


@dataclass(frozen=True)
class ReplayHeader:
    magic: str = REPLAY_MAGIC
    version: int = REPLAY_VERSION

    game_id: str = "unknown"
    initial_scene: str = "unknown"
    seed: int = 0
    fps: int = 60

    virtual_w: int = 0
    virtual_h: int = 0

    options: dict[str, Any] = field(default_factory=dict)
