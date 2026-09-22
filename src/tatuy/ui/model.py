from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from tatuy.ecs.entity import EntityId
from tatuy.commands import EngineCommand
from tatuy.geometry.size import Size
from tatuy.graphics.color import Color
from tatuy.input.pointer import Cursor
from tatuy.math.vec2 import Vec2


class PanelShape(str, Enum):
    RECT = "rect"
    ROUNDED = "rounded"
    PILL = "pill"
    CIRCLE = "circle"


@dataclass
class UiNode:
    size: Size

    # None means positioned relative to the window.
    parent: EntityId | None = None

    # Location inside the parent: (0, 0) = top-left;
    # (0.5, 0.5) = center; (1, 1) = bottom-right.
    anchor: tuple[float, float] = (0.5, 0.5)

    # Offset of this node's center from its anchor.
    offset: Vec2 = field(default_factory=Vec2.zero)

    # Relative to the parent's z.
    z: int = 0

    visible: bool = True
    enabled: bool = True

    # Panels can block clicks even without being buttons.
    blocks_pointer: bool = True


@dataclass
class Panel:
    color: Color
    shape: PanelShape = PanelShape.RECT
    radius: float = 12.0


@dataclass(frozen=True)
class ButtonAppearance:
    background: Color | None = None
    foreground: Color | None = None
    content: str | None = None
    cursor: Cursor = Cursor.HAND


@dataclass
class Button:
    commands: tuple[EngineCommand, ...] = ()

    normal: ButtonAppearance = field(default_factory=ButtonAppearance)
    hover: ButtonAppearance = field(default_factory=ButtonAppearance)
    pressed: ButtonAppearance = field(default_factory=ButtonAppearance)
    disabled: ButtonAppearance = field(
        default_factory=lambda: ButtonAppearance(cursor=Cursor.ARROW)
    )


@dataclass
class ButtonState:
    hovered: bool = False
    pressed: bool = False


@dataclass
class ResolvedNode:
    center: Vec2
    size: Size
    z: int
    visible: bool
    enabled: bool


@dataclass
class UIFrame:
    nodes: dict[EntityId, ResolvedNode] = field(default_factory=dict)


@dataclass
class UIInteraction:
    captured: EntityId | None = None

    # Cleared each update. Game systems can consume these
    # when behavior needs more than a fixed command binding.
    activated: list[EntityId] = field(default_factory=list)
