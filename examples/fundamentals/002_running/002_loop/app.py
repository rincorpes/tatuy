from __future__ import annotations

from tatuy.backend.pygame.config import PygameBackendConfig
from tatuy.backend.pygame.pygame_backend import PygameBackend
from tatuy.engine.engine import Engine
from tatuy.engine.loop.python_loop import PythonLoop


def main():
    backend = PygameBackend(PygameBackendConfig())
    engine = Engine(backend)

    loop = PythonLoop()
    loop.run(engine)


if __name__ == "__main__":
    main()
