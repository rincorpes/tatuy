from __future__ import annotations

from collections.abc import Iterator, Mapping, Sequence, Set
from typing import Any, Protocol

from tatuy.ecs.component import TComponent
from tatuy.ecs.entity import EntityId

ComponentStore = Mapping[EntityId, Any]


class ECSStore(Protocol):
    """Storage boundary used by :class:`World`.

    Implementations own entity identity and component persistence. Resources,
    scheduling, and gameplay policy remain outside the store.
    """

    @property
    def entities(self) -> Set[EntityId]: ...

    @property
    def components(self) -> Mapping[type, ComponentStore]: ...

    def create_entity(self) -> EntityId: ...

    def destroy_entity(self, entity: EntityId) -> None: ...

    def add_component(
        self,
        entity: EntityId,
        component: TComponent,
    ) -> TComponent: ...

    def get_component(
        self,
        entity: EntityId,
        component_type: type[TComponent],
    ) -> TComponent: ...

    def has_component(
        self,
        entity: EntityId,
        component_type: type,
    ) -> bool: ...

    def remove_component(
        self,
        entity: EntityId,
        component_type: type[TComponent],
    ) -> TComponent: ...

    def query(
        self,
        component_types: Sequence[type],
        strategy_name: str,
    ) -> Iterator[tuple[Any, ...]]: ...

    def component_stores(
        self,
        component_types: Sequence[type],
    ) -> list[ComponentStore]: ...
