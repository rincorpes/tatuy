"""Integration checks for the Shatterphase migration, without a display."""

from importlib import import_module
from math import sqrt
from random import Random
from types import SimpleNamespace

import pytest

from tatuy.engine.pipelines import SystemPipelineFactory
from tatuy.features.bounds.resources import WorldBounds, WorldBoundsBorder
from tatuy.features.collision.components import (
    BoxCollider,
    CircleCollider,
    PolygonCollider,
)
from tatuy.features.collision.resources import CollisionContact, CollisionFrame
from tatuy.features.lifecycle.components import DespawnReason
from tatuy.features.lifecycle.resources import LifecycleQueue
from tatuy.features.movement.components import Velocity
from tatuy.features.spatial.components import AttachedTo, Transform
from tatuy.features.visual.components import Polygon, Rect
from tatuy.graphics.render.queue import RenderQueue
from tatuy.graphics.viewport.state import ViewportMode, ViewportState
from tatuy.input.frame import ButtonState, InputFrame
from tatuy.input.keys import Key
from tatuy.math.vec2 import Vec2
from tatuy.resources import ResourceStore
from tatuy.scenes.context import SceneContext

PACKAGE = "examples.experiments.002_entities"
game = import_module(PACKAGE + ".app")


def make_game(**options):
    settings = game.ShatterphaseSettings.from_dict(options)
    resources = ResourceStore()
    resources.add(settings)
    viewport = ViewportState(
        1280, 720, 1280, 720, ViewportMode.FIT, 1, 1280, 720, 0, 0
    )
    context = SceneContext(
        viewport=viewport, audio=SimpleNamespace(), resources=resources
    )
    scene = game.EScene()
    scene.enter(context)
    scene.system_pipeline = SystemPipelineFactory().create(scene, context)
    tick = scene.create_tick_context(
        1 / 120, RenderQueue(), context, SimpleNamespace()
    )
    step(scene, tick)
    return scene, tick


def step(scene, tick, count=1):
    for _ in range(count):
        scene.system_pipeline.update(tick)
        tick.render_queue.clear()
        scene.system_pipeline.present(tick)
        scene.on_present(tick)


def one(world, component):
    return next(world.query(component))[0]


def test_boot_uses_polygon_enemies_and_two_player_entities():
    scene, tick = make_game()
    world = scene.world
    assert len(list(world.query(game.Player))) == 1
    assert len(list(world.query(game.PlayerShield))) == 1
    assert len(list(world.query(game.Ball))) == 1
    assert len(list(world.query(game.Enemy))) == 9
    for entity, _ in world.query(game.Enemy):
        assert len(world.get_component(entity, PolygonCollider).vertices) == 6
        assert world.has_component(entity, Polygon)
        assert not world.has_component(entity, BoxCollider)
    shield = one(world, game.PlayerShield)
    ball = one(world, game.Ball)
    assert world.get_component(shield, AttachedTo).entity == one(
        world, game.Player
    )
    assert world.get_component(ball, AttachedTo).entity == shield
    assert world.get_resource(game.Waves).current == 1
    assert tick.render_queue._ops


def test_circle_and_rect_move_and_clamp_together_with_wide_buff():
    scene, tick = make_game()
    world = scene.world
    player = one(world, game.Player)
    shield = one(world, game.PlayerShield)
    old = world.get_component(player, Transform).position
    start = Vec2(old.x, old.y)
    scene.intent.move_up = True
    scene.intent.move_left = True
    step(scene, tick, 10)
    position = world.get_component(player, Transform).position
    assert position.x < start.x and position.y < start.y
    state = world.get_resource(game.PowerUpState)
    state.remaining[game.PowerUpKind.WIDE] = 1
    step(scene, tick, 400)
    box = world.get_component(shield, BoxCollider)
    bounds = world.get_resource(WorldBounds).bounds
    center = world.get_component(shield, Transform).position
    assert center.x - box.size.width / 2 >= bounds.left
    assert center.y - box.size.height / 2 >= bounds.top
    assert world.get_component(shield, Rect).size == box.size
    assert box.size == state.base_paddle_size


def test_aim_and_launch_release_ball_from_shield():
    scene, tick = make_game()
    world = scene.world
    scene.intent.update_from(
        InputFrame(
            keys_down=frozenset({Key.W, Key.A}),
            buttons={"mouse_3": ButtonState(True, True, False)},
            mouse_pos=(710, 200),
            mouse_inside=True,
        )
    )
    step(scene, tick)
    guide = next(world.query(game.AimGuide))[1]
    assert guide.visible and guide.paths and guide.launch_velocities
    ball = one(world, game.Ball)
    predicted = guide.launch_velocities[ball]
    scene.intent.launch = True
    step(scene, tick)
    velocity = world.get_component(ball, Velocity).value
    assert velocity.x > 0 and velocity.y < 0
    assert predicted.normalized().dot(velocity.normalized()) > 0.99
    assert not world.has_component(ball, AttachedTo)
    assert not world.has_component(ball, game.WaitingForLaunch)
    assert not guide.visible


def test_aim_sweep_hits_hex_faces_and_corners_in_both_windings():
    vertices = game.hex_vertices(20)
    for polygon in (vertices, tuple(reversed(vertices))):
        hit = game.ray_polygon_distance(
            Vec2(0, 40), Vec2(0, -1), polygon, 5, 100
        )
        assert hit == pytest.approx(40 - sqrt(3) * 10 - 5)
        # A ray near the side vertex travels past the hex bounding box first.
        hit = game.ray_polygon_distance(
            Vec2(19, 40), Vec2(0, -1), polygon, 0, 100
        )
        assert hit == pytest.approx(40 - sqrt(3))
        assert (
            game.ray_polygon_distance(
                Vec2(26, 40), Vec2(0, -1), polygon, 5, 100
            )
            is None
        )
        assert (
            game.ray_polygon_distance(Vec2(0, 0), Vec2(0, -1), polygon, 5, 100)
            == 0
        )


def test_ball_damages_hex_and_bounces_through_real_pipeline():
    scene, tick = make_game(
        bricks={"transformations_enabled": False}, powerups={"drop_chance": 0}
    )
    world = scene.world
    enemy = one(world, game.Enemy)
    ball = one(world, game.Ball)
    collider = world.get_component(enemy, PolygonCollider)
    world.get_component(enemy, Transform).position = Vec2(640, 250)
    radius = world.get_component(ball, CircleCollider).radius
    bottom = max(vertex.y for vertex in collider.vertices)
    world.get_component(ball, Transform).position = Vec2(
        640, 250 + bottom + radius - 0.5
    )
    world.get_component(ball, Velocity).value = Vec2(0, -450)
    world.remove_component(ball, game.WaitingForLaunch)
    world.remove_component(ball, AttachedTo)
    step(scene, tick)
    assert enemy not in world.entities
    assert world.get_resource(game.Score).points == 50
    assert world.get_component(ball, Velocity).value.y > 0
    assert world.get_component(ball, game.Ball).combo == 2


def test_multi_hit_contacts_damage_only_on_entry_and_transform_polygon():
    scene, tick = make_game(
        bricks={"transform_chance": 1, "explosions_enabled": False},
        powerups={"drop_chance": 0},
    )
    world = scene.world
    enemy = one(world, game.Enemy)
    ball = one(world, game.Ball)
    properties = world.get_component(enemy, game.Enemy)
    properties.hits_remaining = properties.max_hits = 3
    frame = world.get_resource(CollisionFrame)
    frame.contacts[:] = [CollisionContact(ball, enemy, Vec2(0, -1), 1)]
    system = game.EnemySystem(
        scene.particles, scene.screen_fx, scene.camera_fx, Random(0)
    )
    system.on_post_simulation(tick)
    assert properties.hits_remaining == 2
    assert world.has_component(enemy, game.GhostEnemy)
    assert world.get_component(enemy, Polygon).color == (65, 75, 100)
    system.on_post_simulation(tick)
    assert properties.hits_remaining == 2
    # A ghost returns to its polygon color only after balls leave it.
    world.get_component(enemy, game.GhostEnemy).remaining = 0
    frame.contacts.clear()
    game.CollisionSystem().on_post_simulation(tick)
    assert not world.has_component(enemy, game.GhostEnemy)


@pytest.mark.parametrize("kind", list(game.PowerUpKind))
def test_each_pickup_applies_and_is_removed(kind):
    scene, tick = make_game(persistent_balls=False)
    world = scene.world
    shield = one(world, game.PlayerShield)
    position = world.get_component(shield, Transform).position
    pickup = scene.factory.create(
        "power_up",
        position=Vec2(position.x, position.y),
        radius=12,
        color=game.POWERUP_STYLE[kind][1],
        kind=kind,
    )
    step(scene, tick)
    assert pickup not in world.entities
    if kind == game.PowerUpKind.MULTIBALL:
        assert len(list(world.query(game.Ball))) == 3
    elif kind == game.PowerUpKind.EXTRA_LIFE:
        assert world.get_resource(game.Lives).count == 6
    else:
        assert world.get_resource(game.PowerUpState).active(kind)
        step(scene, tick)
        if kind == game.PowerUpKind.SHIELD:
            assert world.get_resource(WorldBoundsBorder).sides.value & 8


def test_wave_transitions_cancel_delayed_balls_and_complete_all_twenty():
    scene, tick = make_game()
    world = scene.world
    queue = world.get_resource(LifecycleQueue)
    waves = world.get_resource(game.Waves)
    for index in range(1, 21):
        assert waves.current == index
        assert len(list(world.query(game.Ball))) == 1
        ball = one(world, game.Ball)
        assert world.has_component(ball, AttachedTo)
        queue.request_spawn("e_ball", delay=10)
        for entity, _ in list(world.query(game.Enemy)):
            queue.request_despawn(
                entity, DespawnReason.DEFEATED, allow_respawn=False
            )
        # First commit removes enemies; next tick advances the wave.
        step(scene, tick, 2)
        if index < 20:
            assert not queue.spawns
    assert waves.completed and waves.current == 20
    assert not queue.spawns
    assert not list(world.query(game.Ball))


def test_losing_last_ball_costs_one_life_and_respawns_at_moved_shield():
    scene, tick = make_game(persistent_balls=False, respawn_delay=0.1)
    world = scene.world
    ball = one(world, game.Ball)
    world.remove_component(ball, game.WaitingForLaunch)
    world.remove_component(ball, AttachedTo)
    world.get_component(ball, Transform).position = Vec2(640, 800)
    step(scene, tick)
    assert world.get_resource(game.Lives).count == 4
    assert not list(world.query(game.Ball))
    scene.intent.move_left = True
    step(scene, tick, 15)
    ball = one(world, game.Ball)
    shield = one(world, game.PlayerShield)
    attachment = world.get_component(ball, AttachedTo)
    assert attachment.entity == shield
    assert world.get_component(ball, Transform).position == (
        world.get_component(shield, Transform).position + attachment.offset
    )


def test_descent_handles_polygon_extents_and_preserves_clearance():
    scene, tick = make_game()
    world = scene.world
    scene.intent.launch = True
    step(scene, tick)
    scene.intent.launch = False
    world.get_resource(game.WaveMotion).speed = 10000
    before = world.get_component(one(world, game.Enemy), Transform).position.y
    step(scene, tick)
    after = world.get_component(one(world, game.Enemy), Transform).position.y
    assert after > before
    shield = one(world, game.PlayerShield)
    shield_top = (
        world.get_component(shield, Transform).position.y
        - world.get_component(shield, BoxCollider).size.height / 2
    )
    lowest = max(
        transform.position.y + max(vertex.y for vertex in collider.vertices)
        for _, _, transform, collider in world.query(
            game.Enemy, Transform, PolygonCollider
        )
    )
    assert lowest <= shield_top - world.get_resource(game.WaveMotion).clearance


def test_test_pickup_survives_initial_wave_setup():
    scene, _ = make_game(powerups={"test_powerup": "multiball"})
    assert len(list(scene.world.query(game.PowerUp))) == 1


def test_ball_bounces_off_the_circle_body_and_resets_combo():
    scene, tick = make_game()
    world = scene.world
    player = one(world, game.Player)
    ball = one(world, game.Ball)
    center = world.get_component(player, Transform).position
    radius = world.get_component(player, CircleCollider).radius
    ball_radius = world.get_component(ball, CircleCollider).radius
    world.remove_component(ball, game.WaitingForLaunch)
    world.remove_component(ball, AttachedTo)
    world.get_component(ball, Transform).position = Vec2(
        center.x + radius + ball_radius - 0.5, center.y
    )
    world.get_component(ball, Velocity).value = Vec2(-450, 0)
    world.get_component(ball, game.Ball).combo = 5
    step(scene, tick)
    assert world.get_component(ball, Velocity).value.x > 0
    assert world.get_component(ball, game.Ball).combo == 1


def test_gameplay_collision_pairs_match_the_engine_solver():
    from tatuy.features.collision.systems import CollisionDetectionSystem

    scene, tick = make_game()
    world = scene.world
    random = Random(4)
    enemy_positions = [
        transform.position
        for _, _, transform in world.query(game.Enemy, Transform)
    ]
    for index in range(15):
        position = enemy_positions[index % len(enemy_positions)]
        ball = scene.factory.create(
            "e_ball",
            position=position
            + Vec2(random.uniform(-18, 18), random.uniform(-18, 18)),
            radius=7.5,
        )
        world.remove_component(ball, game.WaitingForLaunch)
    frame = world.get_resource(CollisionFrame)
    CollisionDetectionSystem().step(tick)
    game.CollisionSystem().on_post_simulation(tick)
    expected = {
        (contact.entity_a, contact.entity_b): contact
        for contact in frame.contacts
    }
    game.CollisionSystem().on_simulation(tick)
    game.CollisionSystem().on_post_simulation(tick)
    actual = {
        (contact.entity_a, contact.entity_b): contact
        for contact in frame.contacts
    }
    assert actual.keys() == expected.keys()
    for pair, contact in actual.items():
        assert contact.normal.x == pytest.approx(expected[pair].normal.x)
        assert contact.normal.y == pytest.approx(expected[pair].normal.y)
        assert contact.penetration == pytest.approx(expected[pair].penetration)


def test_explosive_hex_damages_neighbors_and_scores_each_defeat():
    scene, tick = make_game(powerups={"drop_chance": 0})
    world = scene.world
    ball = one(world, game.Ball)
    center = next(
        entity
        for entity, enemy in world.query(game.Enemy)
        if enemy.row == 1 and enemy.column == 1
    )
    world.add_component(center, game.ExplodingEnemy())
    frame = world.get_resource(CollisionFrame)
    frame.contacts[:] = [CollisionContact(ball, center, Vec2(0, -1), 1)]
    game.EnemySystem(
        scene.particles, scene.screen_fx, scene.camera_fx
    ).on_post_simulation(tick)
    assert len(world.get_resource(LifecycleQueue).despawns) == 9
    assert world.get_resource(game.Score).points == 50 * sum(range(1, 10))


def test_wrap_teleports_ball_clears_trail_and_expires():
    from tatuy.features.fx.components import Trail
    from tatuy.geometry.bounds import BoundsSide

    scene, tick = make_game()
    world = scene.world
    ball = one(world, game.Ball)
    world.remove_component(ball, game.WaitingForLaunch)
    world.remove_component(ball, AttachedTo)
    world.get_resource(game.WrapMode).remaining = 1
    bounds = world.get_resource(WorldBounds).bounds
    world.get_component(ball, Transform).position = Vec2(
        bounds.right + 20, 400
    )
    world.get_component(ball, Velocity).value = Vec2(400, -200)
    step(scene, tick)
    assert world.get_component(ball, Transform).position.x < bounds.center.x
    assert len(world.get_component(ball, Trail).points) <= 1
    assert (
        not world.get_resource(WorldBoundsBorder).sides & BoundsSide.HORIZONTAL
    )
    step(scene, tick, 130)
    assert world.get_resource(WorldBoundsBorder).sides & BoundsSide.HORIZONTAL


def test_curved_shield_and_disabled_optional_features_still_run():
    scene, tick = make_game(
        paddle={"curved": True},
        enable_aiming=False,
        hud={"enabled": False},
        powerups={"enabled": False},
        wrap={"enabled": False},
        fx={"particles": {"enabled": False}, "trails": {"enabled": False}},
    )
    scene.intent.launch = True
    step(scene, tick, 100)
    world = scene.world
    assert not list(world.query(game.AimGuide))
    assert not list(world.query(game.UIDisplay))
    assert not world.get_component(one(world, game.PlayerShield), Rect).visible
    assert any(
        operation.kind == "draw_poly" for operation in tick.render_queue._ops
    )


def test_sticky_player_catches_ball_before_collision_response():
    scene, tick = make_game()
    world = scene.world
    ball = one(world, game.Ball)
    shield = one(world, game.PlayerShield)
    position = world.get_component(shield, Transform).position
    box = world.get_component(shield, BoxCollider)
    radius = world.get_component(ball, CircleCollider).radius
    world.remove_component(ball, game.WaitingForLaunch)
    world.remove_component(ball, AttachedTo)
    world.get_component(ball, Transform).position = Vec2(
        position.x, position.y - box.size.height / 2 - radius + 0.5
    )
    world.get_component(ball, Velocity).value = Vec2(0, 450)
    world.get_resource(game.PowerUpState).remaining[
        game.PowerUpKind.STICKY
    ] = 1
    step(scene, tick)
    assert world.has_component(ball, game.WaitingForLaunch)
    assert world.get_component(ball, AttachedTo).entity == shield
    assert world.get_component(ball, Velocity).value == Vec2.zero()
    assert not world.get_resource(game.PowerUpState).active(
        game.PowerUpKind.STICKY
    )


def test_powered_ball_pierces_defeated_hex_before_collision_response():
    scene, tick = make_game(
        bricks={"transformations_enabled": False},
        powerups={"drop_chance": 0, "allowed": ["fast"]},
    )
    world = scene.world
    ball = one(world, game.Ball)
    enemy = one(world, game.Enemy)
    world.get_component(enemy, Transform).position = Vec2(640, 250)
    bottom = max(
        vertex.y
        for vertex in world.get_component(enemy, PolygonCollider).vertices
    )
    radius = world.get_component(ball, CircleCollider).radius
    world.remove_component(ball, game.WaitingForLaunch)
    world.remove_component(ball, AttachedTo)
    world.get_component(ball, Transform).position = Vec2(
        640, 250 + bottom + radius - 0.5
    )
    world.get_component(ball, Velocity).value = Vec2(0, -450)
    properties = world.get_component(ball, game.Ball)
    properties.power = 2
    properties.pierce_time = 1
    step(scene, tick)
    assert enemy not in world.entities
    assert world.get_component(ball, Velocity).value.y < 0
    assert world.get_resource(game.Score).points == 50


def test_profiling_mode_starts_with_a_full_dense_enemy_field():
    scene, tick = make_game(profiling_max_enemies=True)
    world = scene.world
    enemies = list(world.query(game.Enemy, Transform, PolygonCollider))
    assert len(enemies) == 962
    assert world.get_resource(game.Waves).max == 1
    area = world.get_resource(game.Bounds)
    for _, _, transform, collider in enemies:
        for vertex in collider.vertices:
            position = transform.position + vertex
            assert area.left <= position.x <= area.right
            assert area.top <= position.y <= area.bottom
    # Exercise detection and ball flight with the full field present.
    scene.intent.launch = True
    step(scene, tick, 3)
    ball = one(world, game.Ball)
    assert not world.has_component(ball, game.WaitingForLaunch)
    assert world.get_component(ball, Velocity).value.y < 0


def test_disabling_profiling_mode_restores_the_normal_start():
    scene, _ = make_game(profiling_max_enemies=False)
    assert len(list(scene.world.query(game.Enemy))) == 9
    assert scene.world.get_resource(game.Waves).max == 20
