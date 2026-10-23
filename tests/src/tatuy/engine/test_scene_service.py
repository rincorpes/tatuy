"""Scene-service composition boundaries."""

from unittest.mock import Mock

from tatuy.engine.scene import ScenePolicy, SceneService


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


def test_scene_service_uses_initializer_before_on_enter():
    pipeline_factory = Mock()
    pipeline_factory.create.return_value = Mock()
    initializer = Mock()
    scene = Mock()
    scene_context = Mock()

    service = SceneService(pipeline_factory, initializer)
    service.register_factory("main", lambda: scene)

    service.push("main", scene_context)

    initializer.assert_called_once_with(scene, scene_context)
    scene.enter.assert_not_called()
    scene.on_enter.assert_called_once_with(scene_context)


def test_scene_service_visible_entries_respect_highest_opaque_scene():
    pipeline_factory = Mock()
    pipeline_factory.create.return_value = Mock()
    scene_context = Mock()
    service = SceneService(pipeline_factory)
    bottom = Mock()
    middle = Mock()
    top = Mock()
    service.register_factory("bottom", lambda: bottom)
    service.register_factory("middle", lambda: middle)
    service.register_factory("top", lambda: top)

    service.push("bottom", scene_context)
    service.push(
        "middle",
        scene_context,
        policy=ScenePolicy(is_opaque=True),
    )
    service.push("top", scene_context, is_overlay=True)

    assert [entry.scene_id for entry in service.visible_entries()] == [
        "middle",
        "top",
    ]


def test_scene_service_pop_calls_exit_hook_and_returns_entry():
    pipeline_factory = Mock()
    pipeline_factory.create.return_value = Mock()
    scene = Mock()
    service = SceneService(pipeline_factory)
    service.register_factory("main", lambda: scene)
    service.push("main", Mock())

    entry = service.pop()

    assert entry is not None
    assert entry.scene_id == "main"
    scene.on_exit.assert_called_once_with()
    assert service.pop() is None
