from unittest.mock import Mock

import pytest

from tatuy.ecs.system import SystemPhase
from tatuy.engine.runtime.builtins import (
    BoundsConstraintActivation,
    BoundsDirectionActivation,
    BuiltinSystemCatalog,
    CollisionDirectionActivation,
    CollisionResponseActivation,
    RenderActivation,
    UiRenderActivation,
)
from tatuy.features.bounds.components import BoundsConstraint
from tatuy.features.bounds.resources import BoundsFrame, WorldBounds
from tatuy.features.collision.resources import CollisionFrame
from tatuy.features.spatial.components import Transform
from tatuy.features.visual.components import Circle, Polygon, Rect, Text
from tatuy.ui.components import UiNode
from tatuy.ui.resources import UIFrame


def _context_with_world(world):
    ctx = Mock()
    ctx.world = world
    return ctx


def test_bounds_activation_checks_resources_and_one_matching_entity():
    world = Mock()
    world.has_resource.side_effect = lambda resource: resource in {
        WorldBounds,
        BoundsFrame,
    }
    world.query.return_value = iter(((1, Mock(), Mock()),))

    assert (
        BoundsConstraintActivation().matches(_context_with_world(world))
        is True
    )
    world.query.assert_called_once_with(BoundsConstraint, Transform)


def test_bounds_activation_short_circuits_without_required_resources():
    world = Mock()
    world.has_resource.return_value = False

    assert (
        BoundsConstraintActivation().matches(_context_with_world(world))
        is False
    )
    world.query.assert_not_called()


def test_collision_response_activation_uses_current_frame_contacts():
    world = Mock()
    world.has_resource.return_value = True
    frame = CollisionFrame()
    world.get_resource.return_value = frame

    activation = CollisionResponseActivation()
    assert activation.matches(_context_with_world(world)) is False

    frame.contacts.append(Mock())
    assert activation.matches(_context_with_world(world)) is True
    world.query.assert_not_called()


def test_collision_response_activation_requires_collision_frame():
    world = Mock()
    world.has_resource.return_value = False

    assert (
        CollisionResponseActivation().matches(_context_with_world(world))
        is False
    )
    world.get_resource.assert_not_called()
    world.query.assert_not_called()


def test_direction_activations_use_event_frames_without_world_queries():
    world = Mock()
    bounds_frame = BoundsFrame()
    collision_frame = CollisionFrame()

    def has_resource(resource):
        return resource in {BoundsFrame, CollisionFrame}

    def get_resource(resource):
        if resource is BoundsFrame:
            return bounds_frame
        if resource is CollisionFrame:
            return collision_frame
        raise AssertionError(resource)

    world.has_resource.side_effect = has_resource
    world.get_resource.side_effect = get_resource
    ctx = _context_with_world(world)

    assert BoundsDirectionActivation().matches(ctx) is False
    assert CollisionDirectionActivation().matches(ctx) is False

    bounds_frame.bounces.append(Mock())
    collision_frame.contacts.append(Mock())

    assert BoundsDirectionActivation().matches(ctx) is True
    assert CollisionDirectionActivation().matches(ctx) is True
    world.query.assert_not_called()


def test_builtin_catalog_has_explicit_phase_and_order_contract():
    catalog = BuiltinSystemCatalog().create(scene=None, ctx=None)

    expected = {
        "movement_control": (SystemPhase.CONTROL, 0),
        "spawn_delay": (SystemPhase.PRE_SIMULATION, -1000),
        "motion_snapshot": (SystemPhase.PRE_SIMULATION, 100),
        "movement": (SystemPhase.PRE_SIMULATION, 200),
        "velocity": (SystemPhase.SIMULATION, 100),
        "bounds_constraints": (SystemPhase.SIMULATION, 200),
        "attachment": (SystemPhase.SIMULATION, 300),
        "collision_detection": (SystemPhase.SIMULATION, 400),
        "collision_response": (SystemPhase.SIMULATION, 500),
        "bounds_direction": (SystemPhase.POST_SIMULATION, 0),
        "collision_direction": (SystemPhase.POST_SIMULATION, 0),
        "lifetime": (SystemPhase.POST_SIMULATION, 1000),
        "render": (SystemPhase.PRESENTATION, 0),
        "ui_render": (SystemPhase.PRESENTATION, 0),
        "bounds_border": (SystemPhase.PRESENTATION, 0),
    }

    actual = {}
    for name, registration in catalog.items():
        steps = list(registration.build_steps(sequence=0))
        assert len(steps) == 1
        phase, step = steps[0]
        actual[name] = (phase, step.order)

    assert actual == expected


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
