"""Render queue ordering and native/fallback separation."""

from tatuy.geometry.size import Size
from tatuy.graphics.render.commands import CircleCommand, RectCommand
from tatuy.graphics.render.fallback import CustomCommand
from tatuy.graphics.render.queue import (
    DrawOperation,
    PythonRenderOperation,
    RenderQueue,
)
from tatuy.math.vec2 import Vec2


def test_iter_sorted_orders_by_layer_then_z_then_sequence():
    queue = RenderQueue()
    queue.rect(
        center=Vec2(1, 1), size=Size(2, 2), color=(1, 1, 1), layer="ui", z=0
    )
    queue.circle(
        center=Vec2(2, 2), radius=1, color=(2, 2, 2), layer="world", z=5
    )
    queue.rect(
        center=Vec2(3, 3), size=Size(2, 2), color=(3, 3, 3), layer="world", z=1
    )

    operations = queue.iter_sorted()

    assert [operation.layer for operation in operations] == [
        "world",
        "world",
        "ui",
    ]
    assert [operation.z for operation in operations] == [1, 5, 0]


def test_iter_sorted_preserves_sequence_for_equal_layer_and_z():
    queue = RenderQueue()
    queue.rect(center=Vec2(1, 1), size=Size(2, 2), color=(1, 1, 1), z=3)
    queue.custom(op=lambda _ctx: None, layer="world", z=3)
    queue.circle(center=Vec2(2, 2), radius=1, color=(2, 2, 2), z=3)

    operations = queue.iter_sorted()

    assert [operation.seq for operation in operations] == [0, 1, 2]
    assert isinstance(operations[0], DrawOperation)
    assert isinstance(operations[0].payload, RectCommand)
    assert isinstance(operations[1], PythonRenderOperation)
    assert isinstance(operations[1].payload, CustomCommand)
    assert isinstance(operations[2], DrawOperation)
    assert isinstance(operations[2].payload, CircleCommand)


def test_iter_sorted_filters_layers_without_changing_relative_order():
    queue = RenderQueue()
    queue.rect(
        center=Vec2(1, 1), size=Size(2, 2), color=(1, 1, 1), layer="world"
    )
    queue.circle(center=Vec2(2, 2), radius=1, color=(2, 2, 2), layer="ui")
    queue.custom(op=lambda _ctx: None, layer="debug")

    operations = queue.iter_sorted(("world", "debug"))

    assert [operation.layer for operation in operations] == ["world", "debug"]
    assert [operation.seq for operation in operations] == [0, 2]
