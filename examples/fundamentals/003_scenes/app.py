from __future__ import annotations

from tatuy.backend.pygame import PygameBackend, PygameBackendConfig
from tatuy.engine.engine import Engine
from tatuy.engine.loop.python_loop import PythonLoop
from tatuy.scenes.registry import SceneRegistry
from tatuy.scenes.scene import Scene


# Define and register a scene
@SceneRegistry.implementation("main")
class MainScene(Scene):

    # Will be executed once the scene change
    def on_enter(self, ctx):
        print("Main scene started")


def main():
    backend = PygameBackend(PygameBackendConfig())
    engine = Engine(backend=backend)

    loop = PythonLoop()
    loop.run(engine)


if __name__ == "__main__":
    main()
