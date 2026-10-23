from unittest.mock import Mock

from tatuy.ecs.world import World
from tatuy.features.spatial.components import Transform
from tatuy.features.visual.components import Circle, Polygon, Rect, Text
from tatuy.features.visual.systems import RenderSystem
from tatuy.geometry.size import Size
from tatuy.graphics.render.queue import RenderQueue
from tatuy.math.vec2 import Vec2


def test_render_system_submits_visuals_without_ui_responsibility():
    world = Mock()
    transform = Mock()
    transform.position = Mock()
    rect = Mock(visible=True, size=Mock(), color=(1, 2, 3), layer="world", z=2)

    def query(*components):
        if components == (Transform, Rect):
            return iter(((1, transform, rect),))
        if components in {
            (Transform, Text),
            (Transform, Circle),
            (Transform, Polygon),
        }:
            return iter(())
        raise AssertionError(f"Unexpected visual query: {components}")

    world.query.side_effect = query
    ctx = Mock()
    ctx.world = world
    ctx.render_queue = Mock()

    RenderSystem().step(ctx)

    ctx.render_queue.rect.assert_called_once_with(
        center=transform.position,
        size=rect.size,
        color=rect.color,
        layer=rect.layer,
        z=rect.z,
    )


def test_render_system_submits_all_visual_types_with_transform_layer_and_z():
    world = World()
    queue = RenderQueue()

    rect_entity = world.create_entity()
    world.add_component(rect_entity, Transform(Vec2(10.0, 20.0)))
    world.add_component(
        rect_entity, Rect(Size(4, 6), (1, 2, 3), layer="world", z=2)
    )

    text_entity = world.create_entity()
    world.add_component(text_entity, Transform(Vec2(30.0, 40.0)))
    world.add_component(
        text_entity, Text((4, 5, 6), content="hi", layer="ui", z=3)
    )

    circle_entity = world.create_entity()
    world.add_component(circle_entity, Transform(Vec2(50.0, 60.0)))
    world.add_component(
        circle_entity, Circle(7.0, (7, 8, 9), layer="world", z=4)
    )

    polygon_entity = world.create_entity()
    world.add_component(polygon_entity, Transform(Vec2(5.0, 6.0)))
    world.add_component(
        polygon_entity,
        Polygon(
            (Vec2(0.0, 0.0), Vec2(2.0, 0.0), Vec2(0.0, 3.0)),
            (10, 11, 12),
            layer="world",
            z=5,
        ),
    )

    RenderSystem().step(Mock(world=world, render_queue=queue))

    ops = queue.iter_sorted()
    assert len(ops) == 4
    assert {(op.layer, op.z) for op in ops} == {
        ("world", 2),
        ("ui", 3),
        ("world", 4),
        ("world", 5),
    }
    polygon = next(op for op in ops if op.z == 5)
    assert polygon.payload.points == (
        Vec2(5.0, 6.0),
        Vec2(7.0, 6.0),
        Vec2(5.0, 9.0),
    )


def test_render_system_filters_invisible_visuals():
    world = World()
    queue = RenderQueue()
    entity = world.create_entity()
    world.add_component(entity, Transform(Vec2.zero()))
    world.add_component(entity, Rect(Size(10, 10), (1, 2, 3), visible=False))

    RenderSystem().step(Mock(world=world, render_queue=queue))

    assert queue.iter_sorted() == []
