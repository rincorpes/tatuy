"""Built-in visual entity blueprints and their feature composition."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Generic, TypeVar

from tatuy.ecs.entity import EntityId
from tatuy.ecs.entity.blueprint import TypedEntityBlueprint
from tatuy.ecs.world import TWorld
from tatuy.features.collision.blueprints import (
    CollisionBlueprintAttrs,
    add_collision_components,
)
from tatuy.features.collision.components import (
    BoxCollider,
    CircleCollider,
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


@dataclass(frozen=True)
class SharedAttrs(CollisionBlueprintAttrs):
    """Common attributes for built-in visual entity blueprints."""

    position: Vec2 = field(default_factory=Vec2.zero)
    color: Color = (255, 255, 255)


@dataclass(frozen=True, kw_only=True)
class RectBlueprintAttrs(SharedAttrs):
    size: Size = field(default_factory=Size.zero)


TRectAttrs = TypeVar("TRectAttrs", bound=RectBlueprintAttrs)


class RectBlueprintBase(
    TypedEntityBlueprint[TWorld, TRectAttrs],
    Generic[TWorld, TRectAttrs],
):
    """Base blueprint for rectangle visuals."""

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
        world.add_component(entity, Transform(attrs.position))
        world.add_component(entity, Rect(attrs.size, attrs.color))
        add_collision_components(
            world, entity, self.get_collider(attrs), attrs
        )


class RectBlueprint(
    RectBlueprintBase[TWorld, RectBlueprintAttrs],
    Generic[TWorld],
):
    attrs_type = RectBlueprintAttrs


@dataclass(frozen=True, kw_only=True)
class CircleBlueprintAttrs(SharedAttrs):
    radius: int = 0


TCircleAttrs = TypeVar("TCircleAttrs", bound=CircleBlueprintAttrs)


class CircleBlueprintBase(
    TypedEntityBlueprint[TWorld, TCircleAttrs],
    Generic[TWorld, TCircleAttrs],
):
    """Base blueprint for circle visuals."""

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
        world.add_component(entity, Transform(attrs.position))
        world.add_component(entity, Circle(attrs.radius, attrs.color))
        add_collision_components(
            world, entity, self.get_collider(attrs), attrs
        )


class CircleBlueprint(
    CircleBlueprintBase[TWorld, CircleBlueprintAttrs],
    Generic[TWorld],
):
    attrs_type = CircleBlueprintAttrs


@dataclass(frozen=True, kw_only=True)
class PolygonBlueprintAttrs(SharedAttrs):
    vertices: tuple[Vec2, ...]


TPolygonAttrs = TypeVar("TPolygonAttrs", bound=PolygonBlueprintAttrs)


class PolygonBlueprintBase(
    TypedEntityBlueprint[TWorld, TPolygonAttrs],
    Generic[TWorld, TPolygonAttrs],
):
    """Base blueprint for polygon visuals."""

    def get_collider(self, attrs: TPolygonAttrs) -> PolygonCollider | None:
        if not attrs.with_collider:
            return None
        return PolygonCollider(vertices=attrs.vertices)

    def build_attrs(
        self,
        world: TWorld,
        entity: EntityId,
        attrs: TPolygonAttrs,
    ) -> None:
        world.add_component(entity, Transform(attrs.position))
        world.add_component(
            entity,
            Polygon(vertices=attrs.vertices, color=attrs.color),
        )
        add_collision_components(
            world, entity, self.get_collider(attrs), attrs
        )


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


TTextAttrs = TypeVar("TTextAttrs", bound=TextBlueprintAttrs)


class TextBlueprintBase(
    TypedEntityBlueprint[TWorld, TTextAttrs],
    Generic[TWorld, TTextAttrs],
):
    """Base blueprint for text visuals."""

    def build_attrs(
        self,
        world: TWorld,
        entity: EntityId,
        attrs: TTextAttrs,
    ) -> None:
        world.add_component(entity, Transform(attrs.position))
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
    TextBlueprintBase[TWorld, TextBlueprintAttrs],
    Generic[TWorld],
):
    attrs_type = TextBlueprintAttrs
