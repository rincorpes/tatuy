from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterator
from typing import Any, TypeVar, overload

from tatuy.ecs.component import TComponent
from tatuy.ecs.entity import EntityId

TWorld = TypeVar("TWorld", bound="World")
TResource = TypeVar("TResource")

C1 = TypeVar("C1")
C2 = TypeVar("C2")
C3 = TypeVar("C3")
C4 = TypeVar("C4")
C5 = TypeVar("C5")
C6 = TypeVar("C6")
C7 = TypeVar("C7")
C8 = TypeVar("C8")
C9 = TypeVar("C9")
C10 = TypeVar("C10")
C11 = TypeVar("C11")
C12 = TypeVar("C12")
C13 = TypeVar("C13")
C14 = TypeVar("C14")
C15 = TypeVar("C15")
C16 = TypeVar("C16")
C17 = TypeVar("C17")
C18 = TypeVar("C18")
C19 = TypeVar("C19")
C20 = TypeVar("C20")


class World:
    def __init__(self) -> None:
        self._next_entity_id = 1

        self._entities: set[EntityId] = set()

        self._resources: dict[type, Any] = {}
        self._components: dict[
            type,
            dict[EntityId, Any],
        ] = defaultdict(dict)

    @property
    def entities(self) -> set[EntityId]:
        return self._entities

    @property
    def components(self) -> dict[type, dict[EntityId, Any]]:
        return self._components

    def create_entity(self) -> EntityId:
        entity = EntityId(self._next_entity_id)
        self._next_entity_id += 1

        self._entities.add(entity)

        return entity

    def destroy_entity(self, entity: EntityId) -> None:
        """Remove the entity and all of its components."""
        self._entities.discard(entity)

        for store in self._components.values():
            store.pop(entity, None)

    def add_resource(self, resource: TResource) -> TResource:
        self._resources[type(resource)] = resource

        return resource

    def get_resource(
        self,
        resource_type: type[TResource],
    ) -> TResource:
        try:
            return self._resources[resource_type]
        except KeyError as exc:
            raise KeyError(
                f"Resource {resource_type.__name__} does not exists"
            ) from exc

    def has_resource(
        self,
        resource_type: type,
    ) -> bool:
        return resource_type in self._resources

    def remove_resource(
        self,
        resource_type: type[TResource],
    ) -> TResource:
        try:
            return self._resources.pop(resource_type)
        except KeyError as exc:
            raise KeyError(
                f"Resource {resource_type.__name__} does not exist"
            ) from exc

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
        return entity in self._components.get(
            component_type,
            {},
        )

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

        # Avoid retaining empty component stores.
        if not store:
            del self._components[component_type]

        return component

    @overload
    def query(
        self,
        first: type[C1],
        /,
    ) -> Iterator[tuple[EntityId, C1]]: ...

    @overload
    def query(
        self,
        first: type[C1],
        second: type[C2],
        /,
    ) -> Iterator[tuple[EntityId, C1, C2]]: ...

    @overload
    def query(
        self,
        first: type[C1],
        second: type[C2],
        third: type[C3],
        /,
    ) -> Iterator[tuple[EntityId, C1, C2, C3]]: ...

    @overload
    def query(
        self,
        first: type[C1],
        second: type[C2],
        third: type[C3],
        fourth: type[C4],
        /,
    ) -> Iterator[tuple[EntityId, C1, C2, C3, C4]]: ...

    @overload
    def query(
        self,
        first: type[C1],
        second: type[C2],
        third: type[C3],
        fourth: type[C4],
        fifth: type[C5],
        /,
    ) -> Iterator[tuple[EntityId, C1, C2, C3, C4, C5]]: ...

    @overload
    def query(
        self,
        first: type[C1],
        second: type[C2],
        third: type[C3],
        fourth: type[C4],
        fifth: type[C5],
        sixth: type[C6],
        /,
    ) -> Iterator[tuple[EntityId, C1, C2, C3, C4, C5, C6]]: ...

    @overload
    def query(
        self,
        first: type[C1],
        second: type[C2],
        third: type[C3],
        fourth: type[C4],
        fifth: type[C5],
        sixth: type[C6],
        seventh: type[C7],
        /,
    ) -> Iterator[tuple[EntityId, C1, C2, C3, C4, C5, C6, C7]]: ...

    @overload
    def query(
        self,
        first: type[C1],
        second: type[C2],
        third: type[C3],
        fourth: type[C4],
        fifth: type[C5],
        sixth: type[C6],
        seventh: type[C7],
        eighth: type[C8],
        /,
    ) -> Iterator[tuple[EntityId, C1, C2, C3, C4, C5, C6, C7, C8]]: ...

    @overload
    def query(
        self,
        first: type[C1],
        second: type[C2],
        third: type[C3],
        fourth: type[C4],
        fifth: type[C5],
        sixth: type[C6],
        seventh: type[C7],
        eighth: type[C8],
        ninth: type[C9],
        /,
    ) -> Iterator[tuple[EntityId, C1, C2, C3, C4, C5, C6, C7, C8, C9]]: ...

    @overload
    def query(
        self,
        first: type[C1],
        second: type[C2],
        third: type[C3],
        fourth: type[C4],
        fifth: type[C5],
        sixth: type[C6],
        seventh: type[C7],
        eighth: type[C8],
        ninth: type[C9],
        tenth: type[C10],
        /,
    ) -> Iterator[
        tuple[
            EntityId,
            C1,
            C2,
            C3,
            C4,
            C5,
            C6,
            C7,
            C8,
            C9,
            C10,
        ]
    ]: ...

    @overload
    def query(
        self,
        first: type[C1],
        second: type[C2],
        third: type[C3],
        fourth: type[C4],
        fifth: type[C5],
        sixth: type[C6],
        seventh: type[C7],
        eighth: type[C8],
        ninth: type[C9],
        tenth: type[C10],
        eleventh: type[C11],
        /,
    ) -> Iterator[
        tuple[
            EntityId,
            C1,
            C2,
            C3,
            C4,
            C5,
            C6,
            C7,
            C8,
            C9,
            C10,
            C11,
        ]
    ]: ...

    @overload
    def query(
        self,
        first: type[C1],
        second: type[C2],
        third: type[C3],
        fourth: type[C4],
        fifth: type[C5],
        sixth: type[C6],
        seventh: type[C7],
        eighth: type[C8],
        ninth: type[C9],
        tenth: type[C10],
        eleventh: type[C11],
        twelfth: type[C12],
        /,
    ) -> Iterator[
        tuple[
            EntityId,
            C1,
            C2,
            C3,
            C4,
            C5,
            C6,
            C7,
            C8,
            C9,
            C10,
            C11,
            C12,
        ]
    ]: ...

    @overload
    def query(
        self,
        first: type[C1],
        second: type[C2],
        third: type[C3],
        fourth: type[C4],
        fifth: type[C5],
        sixth: type[C6],
        seventh: type[C7],
        eighth: type[C8],
        ninth: type[C9],
        tenth: type[C10],
        eleventh: type[C11],
        twelfth: type[C12],
        thirteenth: type[C13],
        /,
    ) -> Iterator[
        tuple[
            EntityId,
            C1,
            C2,
            C3,
            C4,
            C5,
            C6,
            C7,
            C8,
            C9,
            C10,
            C11,
            C12,
            C13,
        ]
    ]: ...

    @overload
    def query(
        self,
        first: type[C1],
        second: type[C2],
        third: type[C3],
        fourth: type[C4],
        fifth: type[C5],
        sixth: type[C6],
        seventh: type[C7],
        eighth: type[C8],
        ninth: type[C9],
        tenth: type[C10],
        eleventh: type[C11],
        twelfth: type[C12],
        thirteenth: type[C13],
        fourteenth: type[C14],
        /,
    ) -> Iterator[
        tuple[
            EntityId,
            C1,
            C2,
            C3,
            C4,
            C5,
            C6,
            C7,
            C8,
            C9,
            C10,
            C11,
            C12,
            C13,
            C14,
        ]
    ]: ...

    @overload
    def query(
        self,
        first: type[C1],
        second: type[C2],
        third: type[C3],
        fourth: type[C4],
        fifth: type[C5],
        sixth: type[C6],
        seventh: type[C7],
        eighth: type[C8],
        ninth: type[C9],
        tenth: type[C10],
        eleventh: type[C11],
        twelfth: type[C12],
        thirteenth: type[C13],
        fourteenth: type[C14],
        fifteenth: type[C15],
        /,
    ) -> Iterator[
        tuple[
            EntityId,
            C1,
            C2,
            C3,
            C4,
            C5,
            C6,
            C7,
            C8,
            C9,
            C10,
            C11,
            C12,
            C13,
            C14,
            C15,
        ]
    ]: ...

    @overload
    def query(
        self,
        first: type[C1],
        second: type[C2],
        third: type[C3],
        fourth: type[C4],
        fifth: type[C5],
        sixth: type[C6],
        seventh: type[C7],
        eighth: type[C8],
        ninth: type[C9],
        tenth: type[C10],
        eleventh: type[C11],
        twelfth: type[C12],
        thirteenth: type[C13],
        fourteenth: type[C14],
        fifteenth: type[C15],
        sixteenth: type[C16],
        /,
    ) -> Iterator[
        tuple[
            EntityId,
            C1,
            C2,
            C3,
            C4,
            C5,
            C6,
            C7,
            C8,
            C9,
            C10,
            C11,
            C12,
            C13,
            C14,
            C15,
            C16,
        ]
    ]: ...

    @overload
    def query(
        self,
        first: type[C1],
        second: type[C2],
        third: type[C3],
        fourth: type[C4],
        fifth: type[C5],
        sixth: type[C6],
        seventh: type[C7],
        eighth: type[C8],
        ninth: type[C9],
        tenth: type[C10],
        eleventh: type[C11],
        twelfth: type[C12],
        thirteenth: type[C13],
        fourteenth: type[C14],
        fifteenth: type[C15],
        sixteenth: type[C16],
        seventeenth: type[C17],
        /,
    ) -> Iterator[
        tuple[
            EntityId,
            C1,
            C2,
            C3,
            C4,
            C5,
            C6,
            C7,
            C8,
            C9,
            C10,
            C11,
            C12,
            C13,
            C14,
            C15,
            C16,
            C17,
        ]
    ]: ...

    @overload
    def query(
        self,
        first: type[C1],
        second: type[C2],
        third: type[C3],
        fourth: type[C4],
        fifth: type[C5],
        sixth: type[C6],
        seventh: type[C7],
        eighth: type[C8],
        ninth: type[C9],
        tenth: type[C10],
        eleventh: type[C11],
        twelfth: type[C12],
        thirteenth: type[C13],
        fourteenth: type[C14],
        fifteenth: type[C15],
        sixteenth: type[C16],
        seventeenth: type[C17],
        eighteenth: type[C18],
        /,
    ) -> Iterator[
        tuple[
            EntityId,
            C1,
            C2,
            C3,
            C4,
            C5,
            C6,
            C7,
            C8,
            C9,
            C10,
            C11,
            C12,
            C13,
            C14,
            C15,
            C16,
            C17,
            C18,
        ]
    ]: ...

    @overload
    def query(
        self,
        first: type[C1],
        second: type[C2],
        third: type[C3],
        fourth: type[C4],
        fifth: type[C5],
        sixth: type[C6],
        seventh: type[C7],
        eighth: type[C8],
        ninth: type[C9],
        tenth: type[C10],
        eleventh: type[C11],
        twelfth: type[C12],
        thirteenth: type[C13],
        fourteenth: type[C14],
        fifteenth: type[C15],
        sixteenth: type[C16],
        seventeenth: type[C17],
        eighteenth: type[C18],
        nineteenth: type[C19],
        /,
    ) -> Iterator[
        tuple[
            EntityId,
            C1,
            C2,
            C3,
            C4,
            C5,
            C6,
            C7,
            C8,
            C9,
            C10,
            C11,
            C12,
            C13,
            C14,
            C15,
            C16,
            C17,
            C18,
            C19,
        ]
    ]: ...

    @overload
    def query(
        self,
        first: type[C1],
        second: type[C2],
        third: type[C3],
        fourth: type[C4],
        fifth: type[C5],
        sixth: type[C6],
        seventh: type[C7],
        eighth: type[C8],
        ninth: type[C9],
        tenth: type[C10],
        eleventh: type[C11],
        twelfth: type[C12],
        thirteenth: type[C13],
        fourteenth: type[C14],
        fifteenth: type[C15],
        sixteenth: type[C16],
        seventeenth: type[C17],
        eighteenth: type[C18],
        nineteenth: type[C19],
        twentieth: type[C20],
        /,
    ) -> Iterator[
        tuple[
            EntityId,
            C1,
            C2,
            C3,
            C4,
            C5,
            C6,
            C7,
            C8,
            C9,
            C10,
            C11,
            C12,
            C13,
            C14,
            C15,
            C16,
            C17,
            C18,
            C19,
            C20,
        ]
    ]: ...

    @overload
    def query(self, *component_types: type) -> Iterator[tuple[Any, ...]]: ...

    def query(self, *component_types: type) -> Iterator[tuple[Any, ...]]:
        if not component_types:
            return

        stores = [
            self._components.get(component_type, {})
            for component_type in component_types
        ]

        entity_ids = set(stores[0])
        for store in stores[1:]:
            entity_ids.intersection_update(store)

        for entity in entity_ids:
            yield entity, *(store[entity] for store in stores)
