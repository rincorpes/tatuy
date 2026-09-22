from __future__ import annotations

from tatuy.commands import EngineCommandQueue, SetCursor
from tatuy.ecs.world import World
from tatuy.ui.intent import UiIntent
from tatuy.ui.layout import ButtonAppearanceResolver, PanelGeometry
from tatuy.ui.model import (
    Button,
    ButtonState,
    Panel,
    UIFrame,
    UIInteraction,
    UiNode,
)


class UiPointerController:
    def __init__(self) -> None:
        self._geometry = PanelGeometry()
        self._appearances = ButtonAppearanceResolver()

    def update(
        self,
        world: World,
        intent: UiIntent,
        commands: EngineCommandQueue,
    ) -> None:
        frame = world.get_resource(UIFrame)
        interaction = world.get_resource(UIInteraction)

        interaction.activated.clear()
        self._reset_button_states(world)

        if not intent.pointer_inside:
            interaction.captured = None
            return

        target = self._pick_target(
            world,
            frame,
            intent.pointer_position,
        )

        hovered = (
            target if self._is_interactive(world, frame, target) else None
        )

        if not self._is_interactive(
            world,
            frame,
            interaction.captured,
        ):
            interaction.captured = None

        if intent.activate_pressed:
            interaction.captured = hovered

        if intent.activate_released:
            captured = interaction.captured

            if captured is not None and captured == hovered:
                self._activate(
                    world,
                    captured,
                    interaction,
                    commands,
                )

            interaction.captured = None

        elif not intent.activate_down and not intent.activate_pressed:
            interaction.captured = None

        if hovered is not None:
            state = world.get_component(hovered, ButtonState)
            state.hovered = True
            state.pressed = (
                interaction.captured == hovered and intent.activate_down
            )

        self._request_cursor(world, frame, target, commands)

    def _pick_target(self, world, frame, position):
        ordered = sorted(
            frame.nodes.items(),
            key=lambda item: (item[1].z, item[0]),
            reverse=True,
        )

        for entity, box in ordered:
            if not box.visible:
                continue

            if not world.has_component(entity, Panel):
                continue

            node = world.get_component(entity, UiNode)
            if not node.blocks_pointer:
                continue

            panel = world.get_component(entity, Panel)

            if self._geometry.contains(box, panel, position):
                return entity

        return None

    @staticmethod
    def _is_interactive(world, frame, entity) -> bool:
        if entity is None or entity not in frame.nodes:
            return False

        box = frame.nodes[entity]
        if not box.visible or not box.enabled:
            return False

        required = (UiNode, Panel, Button, ButtonState)
        if not all(
            world.has_component(entity, component) for component in required
        ):
            return False

        return world.get_component(entity, UiNode).blocks_pointer

    @staticmethod
    def _reset_button_states(world) -> None:
        for _, state in world.query(ButtonState):
            state.hovered = False
            state.pressed = False

    @staticmethod
    def _activate(world, entity, interaction, commands) -> None:
        button = world.get_component(entity, Button)

        interaction.activated.append(entity)

        for command in button.commands:
            commands.push(command)

    def _request_cursor(self, world, frame, target, commands) -> None:
        if target is None:
            return

        if not (
            world.has_component(target, Button)
            and world.has_component(target, ButtonState)
        ):
            return

        appearance = self._appearances.resolve(
            world.get_component(target, Button),
            world.get_component(target, ButtonState),
            frame.nodes[target].enabled,
        )

        commands.push(SetCursor(appearance.cursor))
