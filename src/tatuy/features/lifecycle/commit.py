"""Lifecycle structural-commit orchestration."""

from __future__ import annotations

from typing import Generic

from tatuy.ecs.entity.factory import EntityFactory
from tatuy.ecs.world import TWorld
from tatuy.features.lifecycle.kernels import (
    LifecycleCommitKernel,
    PythonLifecycleCommitKernel,
)
from tatuy.scenes.context import SceneTickContext, TContext, TIntent


class LifecycleCommitter(Generic[TContext]):
    """Delegate lifecycle mutation at a structural commit barrier."""

    def __init__(
        self,
        factory: EntityFactory,
        kernel: LifecycleCommitKernel | None = None,
    ) -> None:
        self._factory = factory
        self._kernel = kernel or PythonLifecycleCommitKernel()

    def commit(self, ctx: SceneTickContext[TWorld, TIntent]) -> None:
        """Apply the ready lifecycle batch for the current world."""
        self._kernel.commit(ctx.world, self._factory)
