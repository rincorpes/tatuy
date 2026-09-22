from __future__ import annotations

from tatuy.ecs.component import Text
from tatuy.ecs.world import TWorld
from tatuy.ui.layout import ButtonAppearanceResolver, PanelGeometry
from tatuy.ui.model import (
    Button,
    ButtonAppearance,
    ButtonState,
    Panel,
    PanelShape,
    UIFrame,
    UiNode,
)


class UiRenderer:
    def __init__(self):
        self._geometry = PanelGeometry()
        self._appearances = ButtonAppearanceResolver()

    def submit(self, world: TWorld, queue):
        if next(world.query(UiNode), None) is None:
            return

        frame = world.get_resource(UIFrame)

        ordered = sorted(
            frame.nodes.items(),
            key=lambda item: (item[1].z, item[0]),
        )

        for entity, box in ordered:
            if entity not in world.entities or not box.visible:
                continue

            appearance = self._appearance(world, entity, box)

            if world.has_component(entity, Panel):
                self._submit_panel(
                    queue,
                    box,
                    world.get_component(entity, Panel),
                    appearance,
                )

            if world.has_component(entity, Text):
                self._submit_text(
                    queue,
                    box,
                    world.get_component(entity, Text),
                    appearance,
                )

    def _appearance(self, world: TWorld, entity, box):
        if not world.has_component(entity, Button):
            return ButtonAppearance()

        return self._appearances.resolve(
            world.get_component(entity, Button),
            world.get_component(entity, ButtonState),
            box.enabled,
        )

    def _submit_panel(self, queue, box, panel, appearance):
        color = (
            appearance.background
            if appearance.background is not None
            else panel.color
        )

        if panel.shape == PanelShape.CIRCLE:
            queue.circle(
                center=box.center,
                radius=min(box.size.width, box.size.height) / 2,
                color=color,
                layer="ui",
                z=box.z,
            )
        else:
            queue.rect(
                center=box.center,
                size=box.size,
                color=color,
                radius=self._geometry.radius(panel, box.size),
                layer="ui",
                z=box.z,
            )

    def _submit_text(self, queue, box, text, appearance):
        if not text.visible:
            return

        queue.text(
            x=box.center.x,
            y=box.center.y,
            text=(
                appearance.content
                if appearance.content is not None
                else text.content
            ),
            color=(
                appearance.foreground
                if appearance.foreground is not None
                else text.color
            ),
            font_size=text.font_size,
            align=text.align,
            valign=text.valign,
            layer="ui",
            z=box.z,
        )
