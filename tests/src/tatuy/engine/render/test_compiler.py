"""Render-queue compilation ownership and fallback behavior."""

from tatuy.engine.render.compiler import compile_queue
from tatuy.geometry.size import Size
from tatuy.graphics.render.commands import RectCommand
from tatuy.graphics.render.fallback import CustomCommand
from tatuy.graphics.render.queue import PythonRenderOperation, RenderQueue
from tatuy.math.vec2 import Vec2


def test_compile_queue_snapshots_typed_command_values():
    center = Vec2(10, 20)
    size = Size(30, 40)
    queue = RenderQueue()
    queue.rect(center=center, size=size, color=(1, 2, 3))

    packet = compile_queue(queue)
    center.x = 99
    size.width = 99

    command = packet.operations[0].payload
    assert isinstance(command, RectCommand)
    assert command.center == Vec2(10, 20)
    assert command.size == Size(30, 40)


def test_compile_queue_preserves_custom_callback_identity():
    def draw(_backend):
        return None

    queue = RenderQueue()
    queue.custom(op=draw)

    packet = compile_queue(queue)

    operation = packet.operations[0]
    assert isinstance(operation, PythonRenderOperation)
    command = operation.payload
    assert isinstance(command, CustomCommand)
    assert command.op is draw
