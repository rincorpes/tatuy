import pytest

from tatuy.geometry.aabb import AABB
from tatuy.geometry.collision import CollisionGeometry
from tatuy.geometry.disk import Disk
from tatuy.geometry.shapes import PolygonGeometry
from tatuy.geometry.size import Size
from tatuy.math.vec2 import Vec2


def test_collision_geometry_circle_circle_contact_is_symmetric_in_depth():
    geometry = CollisionGeometry()

    normal, penetration = geometry.find(
        Disk(Vec2(0.0, 0.0), 5.0),
        Disk(Vec2(8.0, 0.0), 5.0),
    )

    assert normal == Vec2(1.0, 0.0)
    assert penetration == 2.0


def test_collision_geometry_circle_box_reverses_normal_when_arguments_reverse():
    geometry = CollisionGeometry()
    circle = Disk(Vec2(-1.0, 0.0), 2.0)
    box = AABB(Vec2(1.0, 0.0), Size(2, 2))

    forward = geometry.find(circle, box)
    reverse = geometry.find(box, circle)

    assert forward is not None
    assert reverse is not None
    assert reverse[0] == forward[0] * -1
    assert reverse[1] == pytest.approx(forward[1])


def test_collision_geometry_polygon_reports_separation_without_ecs():
    geometry = CollisionGeometry()
    polygon = PolygonGeometry(
        world_vertices=(
            Vec2(0.0, 0.0),
            Vec2(2.0, 0.0),
            Vec2(1.0, 2.0),
        )
    )
    far_box = AABB(Vec2(20.0, 20.0), Size(2, 2))

    assert geometry.find(polygon, far_box) is None
