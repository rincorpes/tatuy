from dataclasses import dataclass

import pytest

from tatuy.ecs.entity.blueprint import EntityBlueprint, TypedEntityBlueprint
from tatuy.ecs.entity.factory import EntityFactory
from tatuy.ecs.world import World


@dataclass
class Marker:
    value: int = 1


@dataclass(frozen=True)
class DemoAttrs:
    value: int


class DemoFactory(EntityFactory):
    pass


@DemoFactory.blueprint("demo")
class DemoBlueprint(TypedEntityBlueprint[World, DemoAttrs]):
    attrs_type = DemoAttrs
    identity = Marker

    def build_attrs(self, world, entity, attrs: DemoAttrs) -> None:
        world.add_component(entity, attrs)


def test_factory_creates_registered_blueprint_entity():
    world = World()
    factory = DemoFactory(world)

    entity = factory.create("demo", value=7)

    assert world.get_component(entity, DemoAttrs) == DemoAttrs(7)
    assert world.has_component(entity, Marker)


def test_factory_reuses_blueprint_instance():
    world = World()
    factory = DemoFactory(world)

    first = factory.create("demo", value=1)
    second = factory.create("demo", value=2)

    assert first != second
    assert len(factory._blueprint_instances) == 1


def test_factory_rejects_unknown_blueprint():
    with pytest.raises(ValueError, match="Unknown entity blueprint"):
        EntityFactory(World()).create("missing")


def test_factory_module_stays_generic():
    assert EntityFactory.__module__ == "tatuy.ecs.entity.factory"
    assert EntityBlueprint.__module__ == "tatuy.ecs.entity.blueprint"
