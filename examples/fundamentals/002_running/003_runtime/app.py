from __future__ import annotations

from tatuy.backend.pygame.config import PygameBackendConfig
from tatuy.backend.pygame.pygame_backend import PygameBackend
from tatuy.engine.engine import Engine
from tatuy.engine.loop.python_loop import PythonLoop
from tatuy.engine.runtime.runtime import Runtime


def main():
    runtime = Runtime(
        Engine(PygameBackend(PygameBackendConfig())), PythonLoop()
    )
    runtime.run()


if __name__ == "__main__":
    main()
