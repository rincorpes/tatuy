from dataclasses import dataclass

import pytest

from tatuy.ecs.python_store import PythonECSStore


@dataclass
class Position:
    x: float


@dataclass
class Velocity:
    x: float


def test_query_single_component_preserves_insertion_order():
    store = PythonECSStore()
    first = store.create_entity()
    second = store.create_entity()
    first_position = store.add_component(first, Position(1.0))
    second_position = store.add_component(second, Position(2.0))

    assert list(store.query((Position,), "smallest")) == [
        (first, first_position),
        (second, second_position),
    ]


def test_smallest_query_returns_only_matching_entities():
    store = PythonECSStore()
    first = store.create_entity()
    second = store.create_entity()
    third = store.create_entity()

    first_position = store.add_component(first, Position(1.0))
    first_velocity = store.add_component(first, Velocity(10.0))
    store.add_component(second, Position(2.0))
    third_position = store.add_component(third, Position(3.0))
    third_velocity = store.add_component(third, Velocity(30.0))

    assert list(store.query((Position, Velocity), "smallest")) == [
        (first, first_position, first_velocity),
        (third, third_position, third_velocity),
    ]


def test_intersection_query_matches_smallest_query():
    store = PythonECSStore()
    first = store.create_entity()
    second = store.create_entity()
    store.add_component(first, Position(1.0))
    store.add_component(first, Velocity(10.0))
    store.add_component(second, Position(2.0))

    assert list(store.query((Position, Velocity), "intersection")) == list(
        store.query((Position, Velocity), "smallest")
    )


def test_query_with_missing_component_store_is_empty():
    store = PythonECSStore()
    entity = store.create_entity()
    store.add_component(entity, Position(1.0))

    assert list(store.query((Position, Velocity), "smallest")) == []


def test_query_rejects_unknown_strategy():
    store = PythonECSStore()
    entity = store.create_entity()
    store.add_component(entity, Position(1.0))
    store.add_component(entity, Velocity(2.0))

    with pytest.raises(ValueError, match="Unknown query strategy"):
        list(store.query((Position, Velocity), "unknown"))
