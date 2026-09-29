from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field
from typing import Any, Callable, ClassVar, Generic, Iterable, TypeVar, cast

from onomasticon import ImplementationRegistry

from tatuy.ecs.component import TComponent
from tatuy.ecs.entity import EntityId
from tatuy.ecs.world import TWorld, World
from tatuy.features.spatial.components import Transform
from tatuy.features.visual.components import (
    Circle,
    Rect,
    Text,
    TextAlign,
    TextVAlign,
)
from tatuy.geometry.size import Size
from tatuy.graphics.color import Color
from tatuy.math.vec2 import Vec2


class EntityBlueprint(
    ABC,
    Generic[TWorld],
):
    identity: ClassVar[type[Any] | None] = None

    def create(
        self,
        world: TWorld,
        **kwargs,
    ) -> EntityId:
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

        for component in self.compose(attrs):
            world.add_component(entity, component)

    def build_attrs(
        self,
        world: TWorld,
        entity: EntityId,
        attrs: TAttrs,
    ) -> None:
        raise NotImplementedError

    def compose(self, attrs: TAttrs) -> Iterable[TComponent]:
        return ()


@dataclass(frozen=True, kw_only=True)
class RectBlueprintAttrs:
    position: Vec2 = field(default_factory=Vec2.zero)
    size: Size = field(default_factory=Size.zero)
    color: Color = (255, 255, 255)


TRectAttrs = TypeVar(
    "TRectAttrs",
    bound=RectBlueprintAttrs,
)


class RectBlueprintBase(
    TypedEntityBlueprint[TWorld, TRectAttrs], Generic[TWorld, TRectAttrs]
):

    def build_attrs(
        self,
        world: TWorld,
        entity: EntityId,
        attrs: TRectAttrs,
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


class RectBlueprint(
    RectBlueprintBase[
        TWorld,
        RectBlueprintAttrs,
    ],
    Generic[TWorld],
):
    attrs_type = RectBlueprintAttrs


@dataclass(frozen=True, kw_only=True)
class CircleBlueprintAttrs:
    position: Vec2 = field(default_factory=Vec2.zero)
    radius: int = 0
    color: Color = (255, 255, 255)


TCircleAttrs = TypeVar(
    "TCircleAttrs",
    bound=CircleBlueprintAttrs,
)


class CircleBlueprintBase(
    TypedEntityBlueprint[TWorld, TCircleAttrs], Generic[TWorld, TCircleAttrs]
):

    def build_attrs(
        self,
        world: TWorld,
        entity: EntityId,
        attrs: TCircleAttrs,
    ) -> None:
        world.add_component(
            entity,
            Transform(attrs.position),
        )
        world.add_component(
            entity,
            Circle(attrs.radius, attrs.color),
        )


class CircleBlueprint(
    CircleBlueprintBase[
        TWorld,
        CircleBlueprintAttrs,
    ],
    Generic[TWorld],
):
    attrs_type = CircleBlueprintAttrs


@dataclass(frozen=True, kw_only=True)
class TextBlueprintAttrs:
    position: Vec2 = field(default_factory=Vec2.zero)
    color: Color = (255, 255, 255)
    content: str = ""
    font_size: int = 16
    align: TextAlign = "left"
    valign: TextVAlign = "top"


TTextAttrs = TypeVar(
    "TTextAttrs",
    bound=TextBlueprintAttrs,
)


class TextBlueprintBase(
    TypedEntityBlueprint[TWorld, TTextAttrs], Generic[TWorld, TTextAttrs]
):

    def build_attrs(
        self,
        world: TWorld,
        entity: EntityId,
        attrs: TTextAttrs,
    ) -> None:
        world.add_component(
            entity,
            Transform(attrs.position),
        )
        world.add_component(
            entity,
            Text(
                attrs.color,
                attrs.content,
                attrs.font_size,
                attrs.align,
                attrs.valign,
            ),
        )


class TextBlueprint(
    TextBlueprintBase[
        TWorld,
        TextBlueprintAttrs,
    ],
    Generic[TWorld],
):
    attrs_type = TextBlueprintAttrs


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

        return blueprint.create(
            self._world,
            **kwargs,
        )
