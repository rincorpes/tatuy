from __future__ import annotations

from tatuy.ecs.system import BaseSystem
from tatuy.ecs.world import TWorld
from tatuy.features.spatial.components import AttachedTo, Transform
from tatuy.scenes.context import SceneTickContext, TContext, TIntent


class AttatchmentSystem(BaseSystem[TContext]):
    def step(self, ctx: SceneTickContext[TWorld, TIntent]):
        for (
            _,
            transform,
            attatchment,
        ) in ctx.world.query(Transform, AttachedTo):
            parent_transform = ctx.world.get_component(
                attatchment.entity, Transform
            )
            transform.position = parent_transform.position + attatchment.offset
