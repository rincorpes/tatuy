from types import SimpleNamespace

from tatuy.ecs.world import World
from tatuy.features.spatial.components import AttachedTo, Transform
from tatuy.features.spatial.kernels import PythonAttachmentKernel
from tatuy.features.spatial.systems import AttachmentSystem
from tatuy.math.vec2 import Vec2


def test_python_kernel_resolves_child_position_from_parent_and_offset():
    world = World()
    parent = world.create_entity()
    child = world.create_entity()
    world.add_component(parent, Transform(Vec2(10.0, 20.0)))
    child_transform = world.add_component(child, Transform(Vec2.zero()))
    world.add_component(child, AttachedTo(parent, Vec2(3.0, -2.0)))

    PythonAttachmentKernel().update(world)

    assert child_transform.position == Vec2(13.0, 18.0)


def test_python_kernel_updates_all_matching_children():
    world = World()
    parent = world.create_entity()
    first = world.create_entity()
    second = world.create_entity()
    world.add_component(parent, Transform(Vec2(5.0, 7.0)))
    first_transform = world.add_component(first, Transform(Vec2.zero()))
    second_transform = world.add_component(second, Transform(Vec2.zero()))
    world.add_component(first, AttachedTo(parent, Vec2(1.0, 2.0)))
    world.add_component(second, AttachedTo(parent, Vec2(-3.0, 4.0)))

    PythonAttachmentKernel().update(world)

    assert first_transform.position == Vec2(6.0, 9.0)
    assert second_transform.position == Vec2(2.0, 11.0)


def test_python_kernel_raises_when_attachment_parent_has_no_transform():
    world = World()
    parent = world.create_entity()
    child = world.create_entity()
    world.add_component(child, Transform(Vec2.zero()))
    world.add_component(child, AttachedTo(parent, Vec2(1.0, 2.0)))

    import pytest

    with pytest.raises(KeyError):
        PythonAttachmentKernel().update(world)


def test_system_delegates_one_batch_call_to_injected_kernel():
    world = World()
    calls = []

    class RecordingKernel:
        def update(self, kernel_world):
            calls.append(kernel_world)

    system = AttachmentSystem(kernel=RecordingKernel())
    system.step(SimpleNamespace(world=world))

    assert calls == [world]
