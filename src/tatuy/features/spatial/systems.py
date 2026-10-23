from __future__ import annotations

from tatuy.ecs.system import BaseSystem
from tatuy.ecs.world import TWorld
from tatuy.features.spatial.kernels import (
    AttachmentKernel,
    PythonAttachmentKernel,
)
from tatuy.scenes.context import SceneTickContext, TContext, TIntent


class AttachmentSystem(BaseSystem[TContext]):
    def __init__(
        self,
        kernel: AttachmentKernel | None = None,
    ) -> None:
        self._kernel = kernel or PythonAttachmentKernel()

    def step(self, ctx: SceneTickContext[TWorld, TIntent]) -> None:
        self._kernel.update(ctx.world)
