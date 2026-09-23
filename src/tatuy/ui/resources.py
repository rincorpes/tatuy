from __future__ import annotations

from dataclasses import dataclass, field

from tatuy.ecs.entity import EntityId
from tatuy.ui.model import ResolvedNode


@dataclass
class UIFrame:
    nodes: dict[EntityId, ResolvedNode] = field(default_factory=dict)


@dataclass
class UIInteraction:
    captured: EntityId | None = None

    # Cleared each update. Game systems can consume these
    # when behavior needs more than a fixed command binding.
    activated: list[EntityId] = field(default_factory=list)
