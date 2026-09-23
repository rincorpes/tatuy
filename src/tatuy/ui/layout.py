from __future__ import annotations

from tatuy.ecs.world import TWorld
from tatuy.geometry.size import Size
from tatuy.graphics.viewport.state import ViewportState
from tatuy.math.vec2 import Vec2
from tatuy.ui.components import (
    Button,
    ButtonAppearance,
    ButtonState,
    Panel,
    PanelShape,
    UiNode,
)
from tatuy.ui.model import ResolvedNode
from tatuy.ui.resources import UIFrame


class UiLayoutResolver:
    def __init__(self, world: TWorld, viewport: ViewportState):
        self._world = world
        self._viewport = viewport
        self._supported = True

        try:
            self._frame = world.get_resource(UIFrame)
            self._nodes = dict(world.query(UiNode))
        except KeyError:
            print("No UI Support")
            self._supported = False

        self._visiting: set = set()

    def layout(self) -> None:
        if not self._supported:
            return
        self._frame.nodes.clear()
        self._visiting.clear()

        for entity in self._nodes:
            self._resolve(entity)

    def _resolve(self, entity) -> ResolvedNode:
        if entity in self._frame.nodes:
            return self._frame.nodes[entity]

        self._validate_entity(entity)

        self._visiting.add(entity)

        node = self._nodes[entity]
        self._validate_node(node)

        parent = self._resolve_parent(node)

        resolved = ResolvedNode(
            center=self._resolve_center(node, parent),
            size=node.size,
            z=parent.z + node.z,
            visible=parent.visible and node.visible,
            enabled=parent.enabled and node.enabled,
        )

        self._frame.nodes[entity] = resolved
        self._visiting.remove(entity)

        return resolved

    def _resolve_parent(self, node: UiNode) -> ResolvedNode:
        if node.parent is not None:
            return self._resolve(node.parent)

        return ResolvedNode(
            center=Vec2(
                self._viewport.window_w / 2,
                self._viewport.window_h / 2,
            ),
            size=type(node.size)(
                self._viewport.window_w,
                self._viewport.window_h,
            ),
            z=0,
            visible=True,
            enabled=True,
        )

    def _resolve_center(
        self,
        node: UiNode,
        parent: ResolvedNode,
    ) -> Vec2:
        return Vec2(
            parent.center.x
            + (node.anchor[0] - 0.5) * parent.size.width
            + node.offset.x,
            parent.center.y
            + (node.anchor[1] - 0.5) * parent.size.height
            + node.offset.y,
        )

    def _validate_entity(self, entity) -> None:
        if entity in self._visiting:
            raise ValueError("Cycle in UI parent relationships")

        if entity not in self._nodes:
            raise ValueError(f"UI parent {entity} is missing its UiNode")

    @staticmethod
    def _validate_node(node: UiNode) -> None:
        if node.size.width < 0 or node.size.height < 0:
            raise ValueError("UI dimensions cannot be negative")


class PanelGeometry:
    def radius(self, panel: Panel, size: Size) -> float:
        maximum = min(size.width, size.height) / 2

        if panel.shape == PanelShape.RECT:
            return 0.0

        if panel.shape == PanelShape.PILL:
            return maximum

        return max(
            0.0,
            min(panel.radius, maximum),
        )

    def contains(
        self,
        box: ResolvedNode,
        panel: Panel,
        position,
    ) -> bool:
        dx = abs(position[0] - box.center.x)
        dy = abs(position[1] - box.center.y)

        half_width = box.size.width / 2
        half_height = box.size.height / 2

        if panel.shape == PanelShape.CIRCLE:
            return self._contains_circle(
                dx,
                dy,
                half_width,
                half_height,
            )

        if dx > half_width or dy > half_height:
            return False

        radius = self.radius(panel, box.size)

        if radius == 0:
            return True

        return self._contains_rounded_corner(
            dx,
            dy,
            half_width,
            half_height,
            radius,
        )

    @staticmethod
    def _contains_circle(
        dx: float,
        dy: float,
        half_width: float,
        half_height: float,
    ) -> bool:
        radius = min(half_width, half_height)

        return dx * dx + dy * dy <= radius * radius

    @staticmethod
    def _contains_rounded_corner(
        dx: float,
        dy: float,
        half_width: float,
        half_height: float,
        radius: float,
    ) -> bool:
        corner_x = max(
            dx - (half_width - radius),
            0.0,
        )
        corner_y = max(
            dy - (half_height - radius),
            0.0,
        )

        return corner_x * corner_x + corner_y * corner_y <= radius * radius


class ButtonAppearanceResolver:
    def resolve(
        self,
        button: Button,
        state: ButtonState,
        enabled: bool,
    ) -> ButtonAppearance:
        if not enabled:
            return button.disabled

        if state.pressed:
            return button.pressed

        if state.hovered:
            return button.hover

        return button.normal
