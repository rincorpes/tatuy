from tatuy.features.bounds.render import BoundsBorderRenderer
from tatuy.features.bounds.resources import WorldBoundsBorder
from tatuy.geometry.bounds import Bounds, BoundsSide
from tatuy.geometry.size import Size
from tatuy.graphics.render.commands import RectCommand
from tatuy.graphics.render.queue import RenderQueue
from tatuy.math.vec2 import Vec2


def test_bounds_border_renderer_submits_all_enabled_sides() -> None:
    queue = RenderQueue()
    renderer = BoundsBorderRenderer()

    renderer.submit(
        Bounds(left=10, top=20, right=110, bottom=70),
        WorldBoundsBorder(
            color=(1, 2, 3),
            thickness=4,
            sides=BoundsSide.ALL,
            z=7,
        ),
        queue,
    )

    ops = queue.iter_sorted()

    assert [op.kind for op in ops] == ["draw_rect"] * 4
    assert [op.layer for op in ops] == ["world"] * 4
    assert [op.z for op in ops] == [7] * 4
    assert [op.payload for op in ops] == [
        RectCommand(Vec2(8, 45), Size(4, 50), (1, 2, 3)),
        RectCommand(Vec2(112, 45), Size(4, 50), (1, 2, 3)),
        RectCommand(Vec2(60, 18), Size(108, 4), (1, 2, 3)),
        RectCommand(Vec2(60, 72), Size(108, 4), (1, 2, 3)),
    ]


def test_bounds_border_renderer_respects_side_mask() -> None:
    queue = RenderQueue()
    renderer = BoundsBorderRenderer()

    renderer.submit(
        Bounds(left=0, top=0, right=100, bottom=50),
        WorldBoundsBorder(
            thickness=6,
            sides=BoundsSide.LEFT | BoundsSide.TOP,
        ),
        queue,
    )

    ops = queue.iter_sorted()

    assert [op.payload for op in ops] == [
        RectCommand(Vec2(-3, 25), Size(6, 50), (220, 220, 220)),
        RectCommand(Vec2(47, -3), Size(106, 6), (220, 220, 220)),
    ]


def test_bounds_border_renderer_submits_nothing_when_disabled() -> None:
    queue = RenderQueue()
    renderer = BoundsBorderRenderer()

    renderer.submit(
        Bounds(left=0, top=0, right=100, bottom=50),
        WorldBoundsBorder(enabled=False),
        queue,
    )

    assert queue.iter_sorted() == []
