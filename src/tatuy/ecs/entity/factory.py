from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable, ClassVar, Generic

from onomasticon import ImplementationRegistry

from tatuy.ecs.entity import EntityId
from tatuy.ecs.world import TWorld, World
from tatuy.features.spatial.components import Transform
from tatuy.graphics.components.shape import Rect


class EntityBlueprint(
    ABC,
    Generic[TWorld],
):
    @abstractmethod
    def create(
        self, world: TWorld, entity: EntityId | None = None, **kwargs
    ) -> EntityId: ...


class RectBlueprint(EntityBlueprint[TWorld]):

    def create(self, world: TWorld, entity: EntityId | None = None, **kwargs):
        if entity is None:
            entity = world.create_entity()

        world.add_component(entity, Transform(kwargs.get("position")))
        world.add_component(
            entity, Rect(kwargs.get("size"), kwargs.get("color"))
        )

        return entity


class _BlueprintRegistry(ImplementationRegistry[EntityBlueprint]):
    implementation_base = EntityBlueprint


class EntityFactory:

    registry: dict[
        str,
        type[EntityBlueprint],
    ] = {}
    _blueprints: ClassVar[type[_BlueprintRegistry]] = _BlueprintRegistry

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)

        class BlueprintRegistry(_BlueprintRegistry):
            pass

        cls._blueprints = BlueprintRegistry

    def __init__(
        self,
        world: World,
    ) -> None:
        self._world = world

    @classmethod
    def blueprint(
        cls, name: str, replace: bool = False
    ) -> Callable[[type[EntityBlueprint]], type[EntityBlueprint]]:
        return cls._blueprints.implementation(
            name,
            replace=replace,
        )

    @classmethod
    def get_blueprint(
        cls,
        name: str,
    ) -> type[EntityBlueprint] | None:
        # Legacy/manual registry takes precedence.
        blueprint_type = cls.registry.get(name)

        if blueprint_type is not None:
            return blueprint_type

        return cls._blueprints.try_get(name)

    def create(
        self,
        name: str,
        **kwargs,
    ) -> EntityId:
        blueprint_type = self.get_blueprint(name)

        if blueprint_type is None:
            raise ValueError(f"Unknown entity blueprint: {name}")

        blueprint = blueprint_type()
        entity = self._world.create_entity()

        return blueprint.create(
            self._world,
            entity=entity,
            **kwargs,
        )
