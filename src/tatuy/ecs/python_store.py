from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterator, Mapping, Sequence, Set
from typing import Any

from tatuy.ecs.component import TComponent
from tatuy.ecs.entity import EntityId
from tatuy.ecs.store import ComponentStore


class PythonECSStore:
    """Reference ECS storage implemented with Python containers."""

    def __init__(self) -> None:
        self._next_entity_id = 1
        self._entities: set[EntityId] = set()
        self._components: dict[type, dict[EntityId, Any]] = defaultdict(dict)

    @property
    def entities(self) -> Set[EntityId]:
        return self._entities

    @property
    def components(self) -> Mapping[type, ComponentStore]:
        return self._components

    def create_entity(self) -> EntityId:
        entity = EntityId(self._next_entity_id)
        self._next_entity_id += 1
        self._entities.add(entity)
        return entity

    def destroy_entity(self, entity: EntityId) -> None:
        self._entities.discard(entity)

        for store in self._components.values():
            store.pop(entity, None)

    def add_component(
        self,
        entity: EntityId,
        component: TComponent,
    ) -> TComponent:
        if entity not in self._entities:
            raise KeyError(f"Unknown entity: {entity}")

        self._components[type(component)][entity] = component
        return component

    def get_component(
        self,
        entity: EntityId,
        component_type: type[TComponent],
    ) -> TComponent:
        try:
            return self._components[component_type][entity]
        except KeyError as exc:
            raise KeyError(
                f"Entity {entity} has no {component_type.__name__}"
            ) from exc

    def has_component(
        self,
        entity: EntityId,
        component_type: type,
    ) -> bool:
        return entity in self._components.get(component_type, {})

    def remove_component(
        self,
        entity: EntityId,
        component_type: type[TComponent],
    ) -> TComponent:
        if entity not in self._entities:
            raise KeyError(f"Unknown entity: {entity}")

        store = self._components.get(component_type)

        if store is None or entity not in store:
            raise KeyError(f"Entity {entity} has no {component_type.__name__}")

        component = store.pop(entity)

        if not store:
            del self._components[component_type]

        return component

    def query(
        self,
        component_types: Sequence[type],
        strategy_name: str,
    ) -> Iterator[tuple[Any, ...]]:
        if not component_types:
            return

        stores = self.component_stores(component_types)

        if len(stores) == 1:
            store = stores[0]
            if not store:
                return
            yield from store.items()
            return

        if any(not store for store in stores):
            return

        if strategy_name == "smallest":
            yield from self._query_smallest(stores)
            return

        if strategy_name == "intersection":
            yield from self._query_intersection(stores)
            return

        raise ValueError(f"Unknown query strategy: {strategy_name}")

    def component_stores(
        self,
        component_types: Sequence[type],
    ) -> list[ComponentStore]:
        return [
            self._components.get(component_type, {})
            for component_type in component_types
        ]

    @staticmethod
    def _base_store_index(stores: Sequence[ComponentStore]) -> int:
        return min(range(len(stores)), key=lambda index: len(stores[index]))

    @classmethod
    def _query_smallest(
        cls,
        stores: Sequence[ComponentStore],
    ) -> Iterator[tuple[Any, ...]]:
        base_index = cls._base_store_index(stores)
        base_store = stores[base_index]

        for entity in base_store:
            if all(
                entity in store
                for index, store in enumerate(stores)
                if index != base_index
            ):
                yield entity, *(store[entity] for store in stores)

    @classmethod
    def _query_intersection(
        cls,
        stores: Sequence[ComponentStore],
    ) -> Iterator[tuple[Any, ...]]:
        base_index = cls._base_store_index(stores)
        base_store = stores[base_index]
        entity_ids = set(base_store)

        for index, store in enumerate(stores):
            if index == base_index:
                continue

            entity_ids.intersection_update(store)
            if not entity_ids:
                return

        for entity in base_store:
            if entity not in entity_ids:
                continue
            yield entity, *(store[entity] for store in stores)
