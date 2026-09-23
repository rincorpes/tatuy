from __future__ import annotations

from tatuy.ecs.system import BaseSystem, SystemPhase
from tatuy.ecs.world import TWorld
from tatuy.features.spatial.components import Transform
from tatuy.graphics.components.shape import Circle, Rect
from tatuy.graphics.components.text import Text
from tatuy.scenes.context import SceneTickContext, TContext, TIntent
from tatuy.ui.render import UiRenderer


class RenderSystem(BaseSystem[TContext]):
    phase = SystemPhase.PRESENTATION

    def __init__(self) -> None:
        self._ui_renderer = UiRenderer()

    def step(self, ctx: SceneTickContext[TWorld, TIntent]):
        for _, transform, rect in ctx.world.query(Transform, Rect):
            if not rect.visible:
                continue
            z = rect.z
            ctx.render_queue.rect(
                center=transform.position,
                size=rect.size,
                color=rect.color,
                layer=rect.layer,
                z=z,
            )
        for _, transform, text in ctx.world.query(Transform, Text):
            if not text.visible:
                continue

            ctx.render_queue.text(
                x=transform.position.x,
                y=transform.position.y,
                text=text.content,
                color=text.color,
                font_size=text.font_size,
                align=text.align,
                valign=text.valign,
                layer=text.layer,
                z=text.z,
            )
        for _, transform, circle in ctx.world.query(Transform, Circle):
            if not circle.visible:
                continue

            ctx.render_queue.circle(
                center=transform.position,
                radius=circle.radius,
                color=circle.color,
                layer=circle.layer,
                z=circle.z,
            )

        self._ui_renderer.submit(ctx.world, ctx.render_queue)
