from __future__ import annotations

from tatuy.ecs.world import TWorld
from tatuy.engine.system import SystemRegistration
from tatuy.features.spatial.components import Transform
from tatuy.features.visual.components import Circle, Rect, Text
from tatuy.features.visual.systems import RenderSystem
from tatuy.scenes.context import SceneTickContext, TIntent
from tatuy.ui.components import UiNode
from tatuy.ui.resources import UIFrame


class RenderActivation:
    def matches(self, ctx: SceneTickContext[TWorld, TIntent]) -> bool:
        world = ctx.world

        ui = next(world.query(UiNode), None) is not None

        if ui and not world.has_resource(UIFrame):
            raise ValueError("UI rendering requires UIFrame")

        drawable = any(
            next(world.query(Transform, visual), None) is not None
            for visual in (Rect, Circle, Text)
        )

        return drawable or ui


# pylint: disable=unused-argument
class BuiltinSystemCatalog:
    def create(
        self,
        scene,
        ctx,
    ) -> dict[str, SystemRegistration]:
        activation = RenderActivation()

        return {
            "render": SystemRegistration(
                system=RenderSystem(),
                active=activation.matches,
            ),
        }
