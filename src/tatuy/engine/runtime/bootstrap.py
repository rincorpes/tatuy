"""Tatuy's default runtime composition for scene systems."""

from __future__ import annotations

from typing import Generic

from tatuy.ecs.structural import StructuralCommandBuffer
from tatuy.engine.pipelines import SystemPipelineFactory
from tatuy.engine.runtime.builtins import BuiltinSystemCatalog
from tatuy.engine.system import StructuralCommitter
from tatuy.features.lifecycle.commit import LifecycleCommitter
from tatuy.scenes.context import SceneContext, TContext
from tatuy.scenes.scene import Scene


class SceneStructuralCommitter(Generic[TContext]):
    """Commit ECS structural changes and lifecycle changes at barriers."""

    def __init__(
        self,
        components: StructuralCommandBuffer[TContext],
        lifecycle: LifecycleCommitter[TContext],
    ) -> None:
        self._components = components
        self._lifecycle = lifecycle

    def commit(self, ctx: TContext) -> None:
        """Commit all default structural mutation channels."""
        self._components.commit(ctx)
        self._lifecycle.commit(ctx)


class DefaultStructuralCommitterFactory(Generic[TContext]):
    """Create Tatuy's default structural committer for a scene."""

    def create(
        self,
        scene: Scene,
        _ctx: SceneContext,
    ) -> StructuralCommitter[TContext]:
        """Compose generic ECS and lifecycle committers for the scene."""
        return SceneStructuralCommitter[TContext](
            components=scene.structural_commands,
            lifecycle=LifecycleCommitter[TContext](scene.factory),
        )


def create_default_system_pipeline_factory() -> SystemPipelineFactory:
    """Create the default feature-aware scene-system pipeline factory."""
    return SystemPipelineFactory(
        catalog=BuiltinSystemCatalog(),
        committer_factory=DefaultStructuralCommitterFactory().create,
    )
