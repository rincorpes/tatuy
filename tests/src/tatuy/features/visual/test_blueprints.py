from tatuy.ecs.world import World
from tatuy.features.collision.components import BoxCollider, CollisionBody
from tatuy.features.spatial.components import Transform
from tatuy.features.visual.blueprints import RectBlueprint
from tatuy.features.visual.components import Rect
from tatuy.geometry.size import Size
from tatuy.math.vec2 import Vec2


def test_rect_blueprint_builds_visual_and_transform_components():
    world = World()

    entity = RectBlueprint().create(
        world,
        position=Vec2(2, 3),
        size=Size(10, 20),
        color=(10, 20, 30),
    )

    assert world.get_component(entity, Transform).position == Vec2(2, 3)
    assert world.get_component(entity, Rect).size == Size(10, 20)
    assert not world.has_component(entity, BoxCollider)
    assert not world.has_component(entity, CollisionBody)


def test_rect_blueprint_optional_collision_is_owned_by_collision_feature():
    world = World()

    entity = RectBlueprint().create(
        world,
        size=Size(10, 20),
        with_collider=True,
        collision_body_inverse_mass=0.25,
        collision_body_restitution=0.5,
    )

    assert world.get_component(entity, BoxCollider).size == Size(10, 20)
    body = world.get_component(entity, CollisionBody)
    assert body.inverse_mass == 0.25
    assert body.restitution == 0.5
