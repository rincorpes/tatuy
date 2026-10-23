from unittest.mock import Mock

from tatuy.features.spatial.components import Transform
from tatuy.features.visual.components import Circle, Polygon, Rect, Text
from tatuy.features.visual.systems import RenderSystem


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
