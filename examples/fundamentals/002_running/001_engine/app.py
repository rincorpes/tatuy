from __future__ import annotations

from time import perf_counter, sleep

from tatuy.backend.pygame.config import PygameBackendConfig
from tatuy.backend.pygame.pygame_backend import PygameBackend
from tatuy.engine.engine import Engine


def main():
    backend = PygameBackend(PygameBackendConfig())
    engine = Engine(backend)

    engine.start()

    target_dt = 1.0 / 60
    previous_frame_start = perf_counter()
    frame_index = 0

    try:
        while engine.running:
            frame_start = perf_counter()
            dt = frame_start - previous_frame_start
            previous_frame_start = frame_start

            engine.step(dt, frame_index)
            frame_index += 1

            elapsed = perf_counter() - frame_start
            if engine.running and elapsed < target_dt:
                sleep(target_dt - elapsed)
    finally:
        engine.stop()


if __name__ == "__main__":
    main()
