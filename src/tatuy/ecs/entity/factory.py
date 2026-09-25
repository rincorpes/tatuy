from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import Any, Callable, ClassVar, Generic, TypeVar, cast

from onomasticon import ImplementationRegistry

from tatuy.ecs.entity import EntityId
from tatuy.ecs.world import TWorld, World
from tatuy.features.spatial.components import Transform
from tatuy.geometry.size import Size
from tatuy.graphics.color import Color
from tatuy.graphics.components.shape import Rect
from tatuy.math.vec2 import Vec2


class EntityBlueprint(
    ABC,
    Generic[TWorld],
):
    identity: ClassVar[type[Any] | None] = None

    def create(
        self,
        world: TWorld,
        entity: EntityId | None = None,
        **kwargs,
    ) -> EntityId:
        if entity is None:
            entity = world.create_entity()

        self.build(world, entity, **kwargs)
        self._build_identity(world, entity)

        return entity

    def _build_identity(
        self,
        world: TWorld,
        entity: EntityId,
    ) -> None:
        if self.identity is not None:
            world.add_component(
                entity,
                self.identity(),
            )

    def build(
        self,
        world: TWorld,
        entity: EntityId,
        **kwargs,
    ):
        raise NotImplementedError


TAttrs = TypeVar("TAttrs")


class TypedEntityBlueprint(
    EntityBlueprint[TWorld],
    Generic[TWorld, TAttrs],
):
    attrs_type: ClassVar[type[Any]]

    def build(
        self,
        world: TWorld,
        entity: EntityId,
        **kwargs: Any,
    ) -> None:
        attrs = cast(
            TAttrs,
            self.attrs_type(**kwargs),
        )

        self.build_attrs(
            world,
            entity,
            attrs,
        )

    def build_attrs(
        self,
        world: TWorld,
        entity: EntityId,
        attrs: TAttrs,
    ) -> None:
        raise NotImplementedError


@dataclass(frozen=True, kw_only=True)
class RectBlueprintAttrs:
    position: Vec2
    size: Size
    color: Color


class RectBlueprint(TypedEntityBlueprint[TWorld, RectBlueprintAttrs]):

    attrs_type = RectBlueprintAttrs

    def build_attrs(
        self,
        world: TWorld,
        entity: EntityId,
        attrs: RectBlueprintAttrs,
    ) -> None:
        world.add_component(
            entity,
            Transform(attrs.position),
        )
        world.add_component(
            entity,
            Rect(
                attrs.size,
                attrs.color,
            ),
        )


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
