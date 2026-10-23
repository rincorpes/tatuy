"""Default runtime-owned scene feature composition."""

from unittest.mock import Mock

from tatuy.ecs.structural import StructuralCommandBuffer
from tatuy.ecs.world import World
from tatuy.engine.runtime.scene_composition import DefaultSceneInitializer
from tatuy.features.bounds.resources import (
    BoundsFrame,
    WorldBounds,
    WorldBoundsBorder,
)
from tatuy.features.fx.camera import CameraFX
from tatuy.features.fx.screen import ScreenEffectStack
from tatuy.features.lifecycle.resources import (
    LifecycleQueue,
    SpawnDefinition,
    SpawnRegistry,
)
from tatuy.geometry.bounds import Bounds
from tatuy.scenes.scene import EntitySpawn


def _scene() -> Mock:
    scene = Mock()
    scene.world = World()
    scene.shared_resource_types = ()
    scene.resources.return_value = ()
    scene.spawn_definitions.return_value = {
        "enemy": SpawnDefinition(blueprint="enemy")
    }
    scene.entities.return_value = (
        EntitySpawn("enemy", kwargs={"hp": 3}, delay=0.25),
    )
    scene.bounds.return_value = Bounds(0, 0, 320, 180)
    scene.bounds_border.return_value = WorldBoundsBorder(thickness=4)
    return scene


def test_default_scene_initializer_provisions_feature_resources():
    scene = _scene()

    DefaultSceneInitializer().initialize(scene, Mock())

    assert isinstance(scene.structural_commands, StructuralCommandBuffer)
    assert scene.world.has_resource(StructuralCommandBuffer)
    assert scene.world.has_resource(LifecycleQueue)
    assert scene.world.has_resource(SpawnRegistry)
    assert scene.world.has_resource(WorldBounds)
    assert scene.world.has_resource(BoundsFrame)
    assert scene.world.has_resource(WorldBoundsBorder)
    assert isinstance(scene.screen_fx, ScreenEffectStack)
    assert isinstance(scene.camera_fx, CameraFX)


def test_default_scene_initializer_processes_spawn_declarations():
    scene = _scene()

    DefaultSceneInitializer().initialize(scene, Mock())

    registry = scene.world.get_resource(SpawnRegistry)
    queue = scene.world.get_resource(LifecycleQueue)

    assert set(registry.definitions) == {"enemy"}
    assert len(queue.spawns) == 1
    assert queue.spawns[0].definition == "enemy"
    assert queue.spawns[0].remaining == 0.25
    assert queue.spawns[0].kwargs == {"hp": 3}


def test_default_scene_initializer_adds_shared_and_declared_resources():
    class SharedResource:
        pass

    class DeclaredResource:
        pass

    shared = SharedResource()
    declared = DeclaredResource()
    scene = _scene()
    scene.shared_resource_types = (SharedResource,)
    scene.resources.return_value = (declared,)
    ctx = Mock()
    ctx.resources.get.return_value = shared

    DefaultSceneInitializer().initialize(scene, ctx)

    ctx.resources.get.assert_called_once_with(SharedResource)
    assert scene.world.get_resource(SharedResource) is shared
    assert scene.world.get_resource(DeclaredResource) is declared


def test_default_scene_initializer_rejects_duplicate_spawn_definitions():
    import pytest

    scene = _scene()
    scene.world.add_resource(
        SpawnRegistry({"enemy": SpawnDefinition(blueprint="old")})
    )

    with pytest.raises(ValueError, match="Duplicate spawn definitions"):
        DefaultSceneInitializer().initialize(scene, Mock())


def test_default_scene_initializer_rejects_unknown_initial_entity_definition():
    import pytest

    scene = _scene()
    scene.spawn_definitions.return_value = {}

    with pytest.raises(ValueError, match="Unknown spawn definition: enemy"):
        DefaultSceneInitializer().initialize(scene, Mock())
