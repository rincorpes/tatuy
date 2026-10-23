"""Contract tests for Tatuy's canonical Python import surface."""

from tatuy import TatuyApp
from tatuy.ecs import EntityFactory, GameSystem, World
from tatuy.engine import SystemRegistration
from tatuy.features.bounds import BoundsConstraint, WorldBounds
from tatuy.features.collision import ColliderAccess, CollisionFrame
from tatuy.features.fx import CameraFX, ScreenEffectStack
from tatuy.features.lifecycle import LifecycleQueue, SpawnDefinition
from tatuy.features.movement import Movement, Velocity
from tatuy.features.spatial import Transform
from tatuy.features.visual import Rect, RectBlueprint
from tatuy.scenes import Intent, Scene, SceneRegistry
from tatuy.ui import UiNode


def test_game_authoring_facades_export_expected_symbols():
    assert TatuyApp is not None
    assert World is not None
    assert EntityFactory is not None
    assert GameSystem is not None
    assert SystemRegistration is not None
    assert Scene is not None
    assert SceneRegistry is not None
    assert Intent is not None


def test_feature_facades_export_authoring_and_extension_symbols():
    symbols = (
        BoundsConstraint,
        WorldBounds,
        ColliderAccess,
        CollisionFrame,
        CameraFX,
        ScreenEffectStack,
        LifecycleQueue,
        SpawnDefinition,
        Movement,
        Velocity,
        Transform,
        Rect,
        RectBlueprint,
        UiNode,
    )

    assert all(symbol is not None for symbol in symbols)


def test_root_package_stays_intentionally_small():
    import tatuy

    assert tatuy.__all__ == ["TatuyApp", "TatuyConfigDict"]
    assert not hasattr(tatuy, "World")
    assert not hasattr(tatuy, "Rect")


def test_internal_implementations_are_not_exported_from_domain_facades():
    import tatuy.ecs as ecs
    import tatuy.features.collision as collision
    import tatuy.features.movement as movement

    assert not hasattr(ecs, "PythonECSStore")
    assert not hasattr(collision, "PythonCollisionDetectionKernel")
    assert not hasattr(movement, "PythonVelocityIntegrationKernel")
