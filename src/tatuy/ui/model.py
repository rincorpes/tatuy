from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from tatuy.ecs.entity import EntityId
from tatuy.commands import EngineCommand
from tatuy.geometry.size import Size
from tatuy.graphics.color import Color
from tatuy.input.pointer import Cursor
from tatuy.math.vec2 import Vec2


@dataclass
class ResolvedNode:
    center: Vec2
    size: Size
    z: int
    visible: bool
    enabled: bool
