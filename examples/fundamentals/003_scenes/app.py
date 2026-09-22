from __future__ import annotations

from tatuy.backend.pygame import PygameBackend, PygameBackendConfig
from tatuy.ecs.world import World
from tatuy.engine.engine import Engine
from tatuy.engine.loop.python_loop import PythonLoop
from tatuy.input.frame import InputFrame
from tatuy.scenes.context import Intent, SceneTickContext
from tatuy.scenes.registry import SceneRegistry
from tatuy.scenes.scene import Scene


class MainWorld(World): ...


class MainIntent(Intent):
    def update_from(self, input_frame: InputFrame) -> None:
        pass


class MainTickContext(SceneTickContext[MainWorld, MainIntent]): ...


@SceneRegistry.implementation("main")
class MainScene(Scene[MainWorld, MainIntent, MainTickContext]):
    world_type = MainWorld
    intent_type = MainIntent
    tick_context_type = MainTickContext

    def on_enter(self, ctx):
        print("Main scene started")


def main():
    backend = PygameBackend(PygameBackendConfig())
    engine = Engine(backend=backend)

    loop = PythonLoop()
    loop.run(engine)


if __name__ == "__main__":
    main()
