from __future__ import annotations

from abc import ABC, abstractmethod
from typing import (
    Generic,
)

from tatuy.ecs.entity import EntityId
from tatuy.ecs.world import BaseWorld, TWorld


class EntityBlueprint(
    ABC,
    Generic[TWorld],
):
    @abstractmethod
    def create(self, world: TWorld, **kwargs) -> EntityId: ...


class EntityFactory:

    registry: dict[
        str,
        type[EntityBlueprint],
    ] = {}

    def __init__(
        self,
        world: BaseWorld,
    ) -> None:
        self._world = world

    def create(self, name: str, **kwargs) -> EntityId:

        blueprint_type = self.registry.get(name)

        if blueprint_type is None:
            raise ValueError(f"Unknown entity blueprint: {name}")

        blueprint = blueprint_type()

        return blueprint.create(self._world, **kwargs)
