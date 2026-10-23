"""Entity factory registry and blueprint instantiation."""

from __future__ import annotations

from typing import Callable, ClassVar

from onomasticon import ImplementationRegistry

from tatuy.ecs.entity import EntityId
from tatuy.ecs.entity.blueprint import EntityBlueprint, TypedEntityBlueprint
from tatuy.ecs.world import World


class _BlueprintRegistry(ImplementationRegistry[EntityBlueprint]):
    implementation_base = EntityBlueprint


class EntityFactory:
    """Create entities from registered generic blueprint types."""

    registry: dict[str, type[EntityBlueprint]] = {}
    _blueprints: ClassVar[type[_BlueprintRegistry]] = _BlueprintRegistry
    _blueprint_instances: dict[str, EntityBlueprint]

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)

        class BlueprintRegistry(_BlueprintRegistry):
            """Per-factory blueprint registry."""

        cls._blueprints = BlueprintRegistry

    def __init__(self, world: World) -> None:
        self._world = world
        self._blueprint_instances = {}

    @classmethod
    def blueprint(
        cls,
        name: str,
        replace: bool = False,
    ) -> Callable[[type[EntityBlueprint]], type[EntityBlueprint]]:
        """Register a blueprint implementation for this factory type."""
        return cls._blueprints.implementation(
            name,
            replace=replace,
        )

    @classmethod
    def get_blueprint(
        cls,
        name: str,
    ) -> type[EntityBlueprint] | None:
        blueprint_type = cls.registry.get(name)

        if blueprint_type is not None:
            return blueprint_type

        return cls._blueprints.try_get(name)

    def create(self, name: str, **kwargs) -> EntityId:
        blueprint = self._blueprint_instances.get(name)

        if blueprint is None:
            blueprint_type = self.get_blueprint(name)

            if blueprint_type is None:
                raise ValueError(f"Unknown entity blueprint: {name}")

            blueprint = blueprint_type()
            self._blueprint_instances[name] = blueprint

        return blueprint.create(self._world, **kwargs)


__all__ = [
    "EntityBlueprint",
    "EntityFactory",
    "TypedEntityBlueprint",
]
