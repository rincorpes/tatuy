"""Prepared render command execution and callback fallback."""

from unittest.mock import Mock

from tatuy.geometry.size import Size
from tatuy.graphics.render.commands import CustomCommand, RectCommand
from tatuy.graphics.render.executor import PythonRenderExecutor
from tatuy.graphics.render.queue import DrawOperation
from tatuy.math.vec2 import Vec2


def test_python_executor_draws_typed_rectangle():
    backend = Mock()
    operation = DrawOperation(
        kind="draw_rect",
        layer="world",
        payload=RectCommand(
            center=Vec2(20, 30),
            size=Size(10, 12),
            color=(1, 2, 3),
            radius=4,
        ),
    )

    PythonRenderExecutor().execute(backend, (operation,))

    backend.renderer.shape.rect.assert_called_once_with(
        Vec2(15, 24),
        Size(10, 12),
        (1, 2, 3),
        radius=4,
    )


def test_custom_command_uses_explicit_fallback_executor():
    backend = Mock()
    fallback = Mock()
    command = CustomCommand(lambda _backend: None)
    operation = DrawOperation(
        kind="custom",
        layer="debug",
        payload=command,
    )

    PythonRenderExecutor(fallback=fallback).execute(backend, (operation,))

    fallback.execute.assert_called_once_with(backend, command)
