from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ProfilerEvent:
    name: str

    start_time: float
    end_time: float | None = None

    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def duration(self) -> float | None:
        if self.end_time is None:
            return None

        return self.end_time - self.start_time
