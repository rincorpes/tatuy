from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field
from typing import Any, Callable, ClassVar, Generic, Iterable, TypeVar, cast

from onomasticon import ImplementationRegistry

from tatuy.ecs.component import TComponent
from tatuy.ecs.entity import EntityId
from tatuy.ecs.world import TWorld, World
from tatuy.features.collision.components import (
    BoxCollider,
    CircleCollider,
    CollisionBody,
    PolygonCollider,
)
from tatuy.features.spatial.components import Transform
from tatuy.features.visual.components import (
    Circle,
    Polygon,
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


TAttrs = TypeVar("TAttrs", bound="SharedAttrs")


class TypedEntityBlueprint(
    EntityBlueprint[TWorld],
    Generic[TWorld, TAttrs],
):
    attrs_type: ClassVar[type[Any]]

    def get_collider(self, attrs: TAttrs) -> Any:
        return None

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

        for component in self.compose(attrs):  # type: ignore
            world.add_component(entity, component)

        # pylint: disable=assignment-from-none
        collider = self.get_collider(attrs)
        if collider:
            if not world.has_component(entity, type(collider)):
                world.add_component(entity, collider)
            if not world.has_component(entity, CollisionBody):
                world.add_component(
                    entity,
                    CollisionBody(
                        inverse_mass=attrs.collision_body_inverse_mass,
                        restitution=attrs.collision_body_restitution,
                    ),
                )

    def build_attrs(
        self,
        world: TWorld,
        entity: EntityId,
        attrs: TAttrs,
    ) -> None:
        raise NotImplementedError

    def compose(self, attrs: TAttrs) -> Iterable[TComponent]:
        return ()


@dataclass(frozen=True)
class SharedAttrs:
    position: Vec2 = field(default_factory=Vec2.zero)
    color: Color = (255, 255, 255)
    with_collider: bool = False
    collision_body_inverse_mass: float = 1
    collision_body_restitution: float = 1


@dataclass(frozen=True, kw_only=True)
class RectBlueprintAttrs(SharedAttrs):
    size: Size = field(default_factory=Size.zero)


TRectAttrs = TypeVar(
    "TRectAttrs",
    bound=RectBlueprintAttrs,
)


class RectBlueprintBase(
    TypedEntityBlueprint[TWorld, TRectAttrs], Generic[TWorld, TRectAttrs]
):

    def get_collider(self, attrs: TRectAttrs) -> BoxCollider | None:
        if not attrs.with_collider:
            return None

        return BoxCollider(attrs.size)

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
class CircleBlueprintAttrs(SharedAttrs):
    radius: int = 0


TCircleAttrs = TypeVar(
    "TCircleAttrs",
    bound=CircleBlueprintAttrs,
)


class CircleBlueprintBase(
    TypedEntityBlueprint[TWorld, TCircleAttrs], Generic[TWorld, TCircleAttrs]
):
    def get_collider(self, attrs: TCircleAttrs) -> CircleCollider | None:
        if not attrs.with_collider:
            return None

        return CircleCollider(attrs.radius)

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
class PolygonBlueprintAttrs(SharedAttrs):
    vertices: tuple[Vec2, ...]


TPolygonAttrs = TypeVar(
    "TPolygonAttrs",
    bound=PolygonBlueprintAttrs,
)


class PolygonBlueprintBase(
    TypedEntityBlueprint[TWorld, TPolygonAttrs],
    Generic[TWorld, TPolygonAttrs],
):
    def get_collider(
        self,
        attrs: TPolygonAttrs,
    ) -> PolygonCollider | None:
        if not attrs.with_collider:
            return None

        return PolygonCollider(vertices=attrs.vertices)

    def build_attrs(
        self,
        world: TWorld,
        entity: EntityId,
        attrs: TPolygonAttrs,
    ) -> None:
        polygon = Polygon(
            vertices=attrs.vertices,
            color=attrs.color,
        )

        world.add_component(entity, Transform(attrs.position))
        world.add_component(entity, polygon)


class PolygonBlueprint(
    PolygonBlueprintBase[TWorld, PolygonBlueprintAttrs],
    Generic[TWorld],
):
    attrs_type = PolygonBlueprintAttrs


@dataclass(frozen=True, kw_only=True)
class TextBlueprintAttrs(SharedAttrs):
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
