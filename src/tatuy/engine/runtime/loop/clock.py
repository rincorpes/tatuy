"""Frame timing state for runtime loops."""

from __future__ import annotations

from dataclasses import dataclass, field
from time import perf_counter


@dataclass
class FrameClock:
    """Track elapsed time and frame position for a runtime loop."""

    frame_index: int = 0
    last_time: float = field(default_factory=perf_counter)
    time_s: float = 0.0
    dt: float = 0.0

    def step_time(self) -> None:
        """Advance the clock and update the frame delta."""
        now = perf_counter()
        self.dt = now - self.last_time
        self.last_time = now
        self.time_s += self.dt
