"""Scene-service composition boundaries."""

from unittest.mock import Mock

from tatuy.engine.scene import SceneService


def test_scene_service_uses_injected_system_pipeline_factory():
    pipeline_factory = Mock()
    pipeline = Mock()
    pipeline_factory.create.return_value = pipeline

    scene = Mock()
    scene_context = Mock()

    service = SceneService(pipeline_factory)
    service.register_factory("main", lambda: scene)

    service.push("main", scene_context)

    scene.enter.assert_called_once_with(scene_context)
    pipeline_factory.create.assert_called_once_with(scene, scene_context)
    assert scene.system_pipeline is pipeline
