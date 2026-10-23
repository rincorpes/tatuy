from dataclasses import dataclass

import pytest

from tatuy.ecs.entity import EntityId
from tatuy.ecs.world import IntersectionQueryStrategy, World


@dataclass
class Position:
    x: float


@dataclass
class Velocity:
    x: float


def test_create_entity_assigns_monotonic_ids_and_tracks_entities():
    world = World()

    first = world.create_entity()
    second = world.create_entity()

    assert first == EntityId(1)
    assert second == EntityId(2)
    assert world.entities == {first, second}


def test_destroy_entity_removes_entity_and_all_components():
    world = World()
    entity = world.create_entity()
    world.add_component(entity, Position(1.0))
    world.add_component(entity, Velocity(2.0))

    world.destroy_entity(entity)

    assert entity not in world.entities
    assert not world.has_component(entity, Position)
    assert not world.has_component(entity, Velocity)


def test_add_component_requires_known_entity():
    world = World()

    with pytest.raises(KeyError, match="Unknown entity"):
        world.add_component(EntityId(99), Position(1.0))


def test_component_lifecycle_round_trip():
    world = World()
    entity = world.create_entity()
    position = Position(1.0)

    assert world.add_component(entity, position) is position
    assert world.has_component(entity, Position)
    assert world.get_component(entity, Position) is position
    assert world.remove_component(entity, Position) is position
    assert not world.has_component(entity, Position)
    assert Position not in world.components


def test_get_missing_component_raises_descriptive_key_error():
    world = World()
    entity = world.create_entity()

    with pytest.raises(KeyError, match="has no Position"):
        world.get_component(entity, Position)


def test_remove_component_requires_known_entity():
    world = World()

    with pytest.raises(KeyError, match="Unknown entity"):
        world.remove_component(EntityId(99), Position)


def test_remove_missing_component_raises_descriptive_key_error():
    world = World()
    entity = world.create_entity()

    with pytest.raises(KeyError, match="has no Position"):
        world.remove_component(entity, Position)


def test_resource_lifecycle_is_independent_from_entities():
    world = World()
    entity = world.create_entity()
    resource = Position(5.0)

    assert world.add_resource(resource) is resource
    world.destroy_entity(entity)

    assert world.has_resource(Position)
    assert world.get_resource(Position) is resource
    assert world.remove_resource(Position) is resource
    assert not world.has_resource(Position)


def test_query_single_component_preserves_component_insertion_order():
    world = World()
    first = world.create_entity()
    second = world.create_entity()
    first_position = world.add_component(first, Position(1.0))
    second_position = world.add_component(second, Position(2.0))

    assert list(world.query(Position)) == [
        (first, first_position),
        (second, second_position),
    ]


def test_query_multiple_components_returns_only_matching_entities():
    world = World()
    first = world.create_entity()
    second = world.create_entity()
    third = world.create_entity()

    first_position = world.add_component(first, Position(1.0))
    first_velocity = world.add_component(first, Velocity(10.0))
    world.add_component(second, Position(2.0))
    third_position = world.add_component(third, Position(3.0))
    third_velocity = world.add_component(third, Velocity(30.0))

    assert list(world.query(Position, Velocity)) == [
        (first, first_position, first_velocity),
        (third, third_position, third_velocity),
    ]


def test_intersection_query_strategy_matches_default_query_results():
    default_world = World()
    intersection_world = World(query_strategy=IntersectionQueryStrategy())

    for world in (default_world, intersection_world):
        first = world.create_entity()
        second = world.create_entity()
        world.add_component(first, Position(1.0))
        world.add_component(first, Velocity(10.0))
        world.add_component(second, Position(2.0))

    assert list(default_world.query(Position, Velocity)) == list(
        intersection_world.query(Position, Velocity)
    )


def test_query_with_no_component_types_is_empty():
    world = World()

    assert list(world.query()) == []
