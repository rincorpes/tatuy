from __future__ import annotations

from time import sleep

from tatuy.engine.engine import Engine
from tatuy.engine.timing import FrameClock


class PythonLoop:

    def __init__(self, target_fps: int = 60):
        self._target_dt = 1.0 / target_fps if target_fps > 0 else 0.0

    def run(self, engine: Engine) -> None:
        engine.start()

        clock = FrameClock()

        try:
            while engine.running:
                clock.step_time()
                engine.step(clock.dt, clock.frame_index)
                self._wait(clock.dt)
                clock.frame_index += 1
        finally:
            engine.stop()

    def _wait(self, elapsed: float) -> None:
        if self._target_dt <= 0:
            return

        remaining = self._target_dt - elapsed

        if remaining > 0:
            sleep(remaining)
