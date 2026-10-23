from types import SimpleNamespace

import pytest

from tatuy.commands import EngineCommandQueue
from tatuy.ecs.world import World
from tatuy.geometry.size import Size
from tatuy.graphics.viewport.state import ViewportMode, ViewportState
from tatuy.math.vec2 import Vec2
from tatuy.scenes.context import Intent
from tatuy.ui.components import Button, ButtonState, Panel, UiNode
from tatuy.ui.intent import UiIntent
from tatuy.ui.layout import UiLayoutResolver
from tatuy.ui.resources import UIFrame, UIInteraction
from tatuy.ui.systems import UiPointerSystem


def _viewport() -> ViewportState:
    return ViewportState(
        virtual_w=200,
        virtual_h=100,
        window_w=200,
        window_h=100,
        mode=ViewportMode.FIT,
        scale=1.0,
        viewport_w=200,
        viewport_h=100,
        offset_x=0,
        offset_y=0,
    )


def test_ui_layout_resolves_parent_anchor_offset_and_inherited_state():
    world = World()
    frame = world.add_resource(UIFrame())
    parent = world.create_entity()
    child = world.create_entity()
    world.add_component(
        parent,
        UiNode(
            size=Size(100, 40),
            anchor=(0.5, 0.5),
            offset=Vec2(10.0, 5.0),
            z=2,
            enabled=False,
        ),
    )
    world.add_component(
        child,
        UiNode(
            size=Size(20, 10),
            parent=parent,
            anchor=(1.0, 0.5),
            offset=Vec2(3.0, 0.0),
            z=4,
        ),
    )

    UiLayoutResolver(world, _viewport()).layout()

    assert frame.nodes[parent].center == Vec2(110.0, 55.0)
    assert frame.nodes[parent].z == 2
    assert frame.nodes[child].center == Vec2(163.0, 55.0)
    assert frame.nodes[child].z == 6
    assert frame.nodes[child].enabled is False


def test_ui_layout_rejects_parent_cycles():
    world = World()
    world.add_resource(UIFrame())
    first = world.create_entity()
    second = world.create_entity()
    world.add_component(first, UiNode(Size(10, 10), parent=second))
    world.add_component(second, UiNode(Size(10, 10), parent=first))

    with pytest.raises(ValueError, match="Cycle in UI parent relationships"):
        UiLayoutResolver(world, _viewport()).layout()


def test_ui_pointer_system_requires_ui_intent():
    system = UiPointerSystem()
    ctx = SimpleNamespace(
        world=World(),
        intent=Intent(),
        scene_context=SimpleNamespace(commands=EngineCommandQueue()),
    )

    with pytest.raises(
        TypeError, match="requires an intent derived from UiIntent"
    ):
        system.step(ctx)


def test_ui_pointer_press_release_updates_button_state_and_activation():
    world = World()
    frame = world.add_resource(UIFrame())
    interaction = world.add_resource(UIInteraction())
    entity = world.create_entity()
    world.add_component(entity, UiNode(Size(40, 20)))
    world.add_component(entity, Panel((1, 2, 3)))
    world.add_component(entity, Button())
    state = world.add_component(entity, ButtonState())
    UiLayoutResolver(world, _viewport()).layout()
    commands = EngineCommandQueue()
    system = UiPointerSystem()

    pressed = UiIntent(
        pointer_position=(100, 50),
        pointer_inside=True,
        activate_down=True,
        activate_pressed=True,
    )
    system.step(
        SimpleNamespace(
            world=world,
            intent=pressed,
            scene_context=SimpleNamespace(commands=commands),
        )
    )

    assert interaction.captured == entity
    assert state.hovered is True
    assert state.pressed is True

    released = UiIntent(
        pointer_position=(100, 50),
        pointer_inside=True,
        activate_released=True,
    )
    system.step(
        SimpleNamespace(
            world=world,
            intent=released,
            scene_context=SimpleNamespace(commands=commands),
        )
    )

    assert interaction.captured is None
    assert interaction.activated == [entity]
    assert state.hovered is True
    assert state.pressed is False
