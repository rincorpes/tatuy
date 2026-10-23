from unittest.mock import Mock

import pytest

from tatuy.engine.runtime.builtins import RenderActivation, UiRenderActivation
from tatuy.features.spatial.components import Transform
from tatuy.features.visual.components import Circle, Polygon, Rect, Text
from tatuy.ui.components import UiNode
from tatuy.ui.resources import UIFrame


def _context_with_world(world):
    ctx = Mock()
    ctx.world = world
    return ctx


def test_visual_render_activation_ignores_ui_only_world():
    world = Mock()

    def query(*components):
        if components == (UiNode,):
            return iter(((1, Mock()),))
        return iter(())

    world.query.side_effect = query

    assert RenderActivation().matches(_context_with_world(world)) is False

    visual_queries = {
        (Transform, Rect),
        (Transform, Circle),
        (Transform, Polygon),
        (Transform, Text),
    }
    assert {call.args for call in world.query.call_args_list} == visual_queries


def test_ui_render_activation_requires_ui_frame():
    world = Mock()
    world.query.return_value = iter(((1, Mock()),))
    world.has_resource.return_value = False

    with pytest.raises(ValueError, match="UI rendering requires UIFrame"):
        UiRenderActivation().matches(_context_with_world(world))

    world.has_resource.assert_called_once_with(UIFrame)


def test_ui_render_activation_accepts_ui_with_frame():
    world = Mock()
    world.query.return_value = iter(((1, Mock()),))
    world.has_resource.return_value = True

    assert UiRenderActivation().matches(_context_with_world(world)) is True


def test_ui_render_activation_is_inactive_without_ui_nodes():
    world = Mock()
    world.query.return_value = iter(())

    assert UiRenderActivation().matches(_context_with_world(world)) is False
    world.has_resource.assert_not_called()
