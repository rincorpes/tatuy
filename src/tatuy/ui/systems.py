from __future__ import annotations

from tatuy.ecs.system import BaseSystem, SystemPhase
from tatuy.ecs.world import TWorld
from tatuy.scenes.context import SceneTickContext, TContext, TIntent
from tatuy.ui.intent import UiIntent
from tatuy.ui.interaction import UiPointerController
from tatuy.ui.layout import UiLayoutResolver


class UiLayoutSystem(BaseSystem[TContext]):
    phase = SystemPhase.CONTROL

    def step(self, ctx: SceneTickContext[TWorld, TIntent]):
        UiLayoutResolver(ctx.world, ctx.scene_context.viewport).layout()


class UiPointerSystem(BaseSystem[TContext]):
    phase = SystemPhase.CONTROL

    def __init__(self) -> None:
        self._controller = UiPointerController()

    def step(self, ctx: SceneTickContext[TWorld, TIntent]):
        if not isinstance(ctx.intent, UiIntent):
            raise TypeError(
                "UiPointerSystem requires an intent derived from UiIntent"
            )

        self._controller.update(
            ctx.world,
            ctx.intent,
            ctx.scene_context.commands,
        )
