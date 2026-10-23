"""Generic entity blueprint lifecycle and typed composition helpers."""

from __future__ import annotations

from abc import ABC
from time import perf_counter_ns
from typing import Any, ClassVar, Generic, Iterable, TypeVar, cast

from tatuy.ecs.component import TComponent
from tatuy.ecs.entity import EntityId
from tatuy.ecs.world import TWorld
from tatuy.tooling.profiler import profiler


class EntityBlueprint(ABC, Generic[TWorld]):
    """Generic recipe for constructing one entity in a world."""

    identity: ClassVar[type[Any] | None] = None

    def create(self, world: TWorld, **kwargs: Any) -> EntityId:
        """Create an entity and apply this blueprint to it."""
        start = perf_counter_ns()
        entity = world.create_entity()
        profiler.increment(
            "factory.entity_create_ns",
            perf_counter_ns() - start,
        )

        start = perf_counter_ns()
        self.build(world, entity, **kwargs)
        profiler.increment(
            "factory.build_ns",
            perf_counter_ns() - start,
        )

        start = perf_counter_ns()
        self._build_identity(world, entity)
        profiler.increment(
            "factory.identity_ns",
            perf_counter_ns() - start,
        )

        return entity

    def _build_identity(self, world: TWorld, entity: EntityId) -> None:
        if self.identity is not None:
            world.add_component(entity, self.identity())

    def build(
        self,
        world: TWorld,
        entity: EntityId,
        **kwargs: Any,
    ) -> None:
        """Apply blueprint-specific construction to an existing entity."""
        raise NotImplementedError


TAttrs = TypeVar("TAttrs")


class TypedEntityBlueprint(
    EntityBlueprint[TWorld],
    Generic[TWorld, TAttrs],
):
    """Blueprint that validates keyword arguments through an attrs type."""

    attrs_type: ClassVar[type[Any]]

    def build(
        self,
        world: TWorld,
        entity: EntityId,
        **kwargs: Any,
    ) -> None:
        start = perf_counter_ns()
        attrs = cast(TAttrs, self.attrs_type(**kwargs))
        profiler.increment(
            "factory.attrs_ns",
            perf_counter_ns() - start,
        )

        start = perf_counter_ns()
        self.build_attrs(world, entity, attrs)
        profiler.increment(
            "factory.build_attrs_ns",
            perf_counter_ns() - start,
        )

        start = perf_counter_ns()
        components: Iterable[Any] = self.compose(attrs)
        for component in components:
            world.add_component(entity, component)
        profiler.increment(
            "factory.compose_ns",
            perf_counter_ns() - start,
        )

    def build_attrs(
        self,
        world: TWorld,
        entity: EntityId,
        attrs: TAttrs,
    ) -> None:
        """Build feature state from validated blueprint attributes."""
        raise NotImplementedError

    def compose(self, _attrs: TAttrs) -> Iterable[TComponent]:
        """Return extra components composed onto the built entity."""
        return ()
