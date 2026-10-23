"""Default runtime composition for scene systems."""

from unittest.mock import Mock

from tatuy.ecs.system import SystemPhase
from tatuy.engine.runtime.bootstrap import (
    create_default_system_pipeline_factory,
)
from tatuy.engine.system import SystemPipeline


def test_default_bootstrap_builds_system_pipeline():
    scene = Mock()
    scene.builtin_overrides.return_value = {}
    scene.systems = ()
    scene.game_systems.return_value = ()
    scene.structural_commands = Mock()
    scene.factory = Mock()
    tick_context = Mock()
    tick_context.world.has_resource.return_value = False

    pipeline = create_default_system_pipeline_factory().create(scene, Mock())

    assert isinstance(pipeline, SystemPipeline)

    pipeline.run_phase(SystemPhase.PRE_SIM_COMMIT, tick_context)
    scene.structural_commands.commit.assert_called_once_with(tick_context)
