"""Offscreen rendering checks, including known rendering defects."""

from unittest.mock import Mock

import pygame
import pytest

from tatuy.backend.config import FontConfig, TextConfig
from tatuy.backend.pygame.components import renderer as module
from tatuy.geometry.size import Size
from tatuy.math.vec2 import Vec2


def test_rect_uses_viewport_and_clip(render_target):
    target = render_target
    target.transform.set(3, 4, 2)
    target.renderer.clip.set(Vec2(1, 1), Size(2, 2))
    target.renderer.shape.rect(Vec2(0, 0), Size(10, 10), (255, 0, 0))
    assert target.screen.get_at((5, 6))[:3] == (255, 0, 0)
    assert target.screen.get_at((4, 6))[:3] == (0, 0, 0)
    target.renderer.clip.clear()
    assert target.screen.get_clip() == target.screen.get_rect()


def test_translucent_rect_blends_without_filling_bounds(render_target):
    target = render_target
    target.renderer.shape.rect(Vec2(2, 2), Size(5, 5), (200, 0, 0, 128))
    assert 99 <= target.screen.get_at((3, 3)).r <= 101
    assert target.screen.get_at((1, 1)).r == 0


def test_polygon_with_too_few_points_is_noop(render_target):
    before = pygame.image.tostring(render_target.screen, "RGBA")
    render_target.renderer.shape.polygon([(1, 1), (2, 2)], (255, 0, 0))
    assert pygame.image.tostring(render_target.screen, "RGBA") == before


def test_begin_and_end_frame(monkeypatch, render_target):
    flip = Mock()
    monkeypatch.setattr(module.pygame.display, "flip", flip)
    render_target.renderer.set_clear_color(4, 5, 6)
    render_target.renderer.begin_frame()
    assert render_target.screen.get_at((20, 20))[:3] == (4, 5, 6)
    render_target.renderer.end_frame()
    flip.assert_called_once_with()


@pytest.fixture
def textures(monkeypatch, render_target):
    # Conversion needs a display in production. Keep these tests offscreen.
    def frombuffer(data, size, pixel_format):
        surface = pygame.Surface(size, pygame.SRCALPHA)
        raw = bytes(data)
        for y in range(size[1]):
            for x in range(size[0]):
                offset = (y * size[0] + x) * 4
                surface.set_at((x, y), tuple(raw[offset : offset + 4]))
        return Mock(convert_alpha=Mock(return_value=surface))

    monkeypatch.setattr(module.pygame.image, "frombuffer", frombuffer)
    return render_target.renderer.texture


@pytest.mark.parametrize(
    "pitch,data",
    [
        (-1, bytes((255, 0, 0, 255, 0, 255, 0, 255))),
        (8, bytes((255, 0, 0, 255, 9, 9, 9, 9, 0, 255, 0, 255, 9, 9, 9, 9))),
    ],
)
def test_texture_upload_handles_packed_and_padded_rows(
    render_target,
    textures,
    pitch,
    data,
):
    handle = textures.create(1, 2, data, pitch=pitch)
    textures.draw(handle, 2, 2, 1, 2)
    assert render_target.screen.get_at((2, 2))[:3] == (255, 0, 0)
    assert render_target.screen.get_at((2, 3))[:3] == (0, 255, 0)
    textures.destroy(handle)
    render_target.screen.fill((0, 0, 0))
    textures.draw(handle, 2, 2, 1, 2)
    assert render_target.screen.get_at((2, 2))[:3] == (0, 0, 0)


def test_texture_rejects_short_buffer(textures):
    with pytest.raises(ValueError, match="buffer too small"):
        textures.create(2, 2, bytes(15))


def test_alpha_polygon_includes_last_vertex(render_target):
    render_target.renderer.shape.polygon(
        [(2, 2), (8, 2), (8, 8), (2, 8)],
        (255, 0, 0, 128),
    )
    assert render_target.screen.get_at((8, 5)).r > 0


def test_tiled_texture_uses_viewport(render_target, textures):
    handle = textures.create(1, 1, bytes((255, 0, 0, 255)))
    render_target.transform.set(10, 10, 2)
    textures.tiled(handle, 1, 1, 2, 2)
    assert render_target.screen.get_at((12, 12)).r == 255
    assert render_target.screen.get_at((1, 1)).r == 0


@pytest.mark.xfail(
    strict=True, reason="B07: default_font loses to default alias"
)
def test_configured_default_font_is_selected(monkeypatch, render_target):
    font_type = Mock()
    font_type.return_value.size.return_value = (10, 10)
    monkeypatch.setattr(module.pygame.font, "Font", font_type)
    config = TextConfig(
        fonts=(FontConfig("default", "old.ttf"), FontConfig("ui", "ui.ttf")),
        default_font="ui",
    )
    context = module.PygameRendererContext(
        render_target.window,
        render_target.transform,
    )
    text = module.PygameText(context, config)
    text.measure("hello")
    font_type.assert_called_once_with("ui.ttf", 24)


@pytest.mark.parametrize("filled", [True, False])
@pytest.mark.parametrize("transform", [(0, 0, 1), (3, 4, 0.5), (1, 2, 2)])
@pytest.mark.parametrize(
    "points,clip",
    [
        ([(2, 2), (8, 2), (8, 8), (2, 8)], None),
        ([(2, 2), (8, 2), (5, 8)], (3, 3, 12, 12)),
        ([(-4, -4), (8, -4), (8, 8), (-4, 8)], None),
        ([(16, 16), (44, 16), (44, 44), (16, 44)], (20, 20, 20, 20)),
        ([(50, 50), (60, 50), (60, 60)], None),
    ],
)
def test_alpha_polygon_matches_opaque_coverage(
    render_target, filled, transform, points, clip
):
    target = render_target
    target.transform.set(*transform)
    target.screen.set_clip(clip)
    target.renderer.shape.polygon(points, (255, 0, 0), filled=filled)
    opaque_pixels = {
        (x, y)
        for y in range(target.screen.get_height())
        for x in range(target.screen.get_width())
        if target.screen.get_at((x, y)).r
    }

    target.screen.set_clip(None)
    target.screen.fill((0, 0, 0))
    target.screen.set_clip(clip)
    original_clip = target.screen.get_clip()
    target.renderer.shape.polygon(points, (255, 0, 0, 128), filled=filled)
    alpha_pixels = {
        (x, y)
        for y in range(target.screen.get_height())
        for x in range(target.screen.get_width())
        if target.screen.get_at((x, y)).r
    }
    assert alpha_pixels == opaque_pixels
    assert target.screen.get_clip() == original_clip
    for point in alpha_pixels:
        assert target.screen.get_at(point).r == 128


@pytest.mark.parametrize(
    "points",
    [
        [(4, 2), (4, 5), (4, 8)],
        [(2, 4), (5, 4), (8, 4)],
        [(4, 4), (4, 4), (4, 4)],
    ],
)
def test_collapsed_alpha_polygon_includes_endpoint(render_target, points):
    render_target.renderer.shape.polygon(points, (255, 0, 0, 128))
    assert render_target.screen.get_at(points[-1]).r == 128


@pytest.mark.parametrize(
    "scale,source_rows,tile_rows",
    [
        (0.5, [0, 0, 1, 1], [0, 1]),
        (1, [0, 1], [0, 1]),
        (2, [0, 1], [0, 0, 1, 1]),
    ],
)
@pytest.mark.parametrize("height", [1, 5])
@pytest.mark.parametrize("clip", [None, (5, 6, 4, 5)])
def test_tiled_texture_pattern_crop_and_clip(
    render_target, textures, scale, source_rows, tile_rows, height, clip
):
    colors = [(255, 0, 0, 255), (0, 255, 0, 255)]
    pixels = bytes(channel for row in source_rows for channel in colors[row])
    handle = textures.create(1, len(source_rows), pixels)
    render_target.transform.set(3, 4, scale)
    render_target.screen.set_clip(clip)
    original_clip = render_target.screen.get_clip()
    textures.tiled(handle, 2, 2, 4, height)
    bounds = pygame.Rect(
        round(3 + 2 * scale),
        round(4 + 2 * scale),
        round(4 * scale),
        round(height * scale),
    )
    for y in range(render_target.screen.get_height()):
        for x in range(render_target.screen.get_width()):
            if bounds.collidepoint(x, y) and original_clip.collidepoint(x, y):
                expected = colors[tile_rows[(y - bounds.y) % len(tile_rows)]][
                    :3
                ]
            else:
                expected = (0, 0, 0)
            assert render_target.screen.get_at((x, y))[:3] == expected
    assert render_target.screen.get_clip() == original_clip


def test_tiled_texture_stretches_width_without_horizontal_repetition(
    render_target, textures
):
    handle = textures.create(2, 1, bytes((255, 0, 0, 255, 0, 0, 255, 255)))
    textures.tiled(handle, 0, 0, 4, 1)
    assert [render_target.screen.get_at((x, 0))[:3] for x in range(4)] == [
        (255, 0, 0),
        (255, 0, 0),
        (0, 0, 255),
        (0, 0, 255),
    ]


@pytest.mark.parametrize("destroyed", [False, True])
def test_tiled_missing_handle_is_noop(render_target, textures, destroyed):
    handle = 999
    if destroyed:
        handle = textures.create(1, 1, bytes((255, 0, 0, 255)))
        textures.destroy(handle)
    before = pygame.image.tostring(render_target.screen, "RGBA")
    textures.tiled(handle, 0, 0, 4, 4)
    assert pygame.image.tostring(render_target.screen, "RGBA") == before


@pytest.mark.parametrize(
    "width,height,scale",
    [
        (0, 5, 1),
        (-1, 5, 1),
        (5, 0, 1),
        (5, -1, 1),
        (1, 5, 0.25),
        (5, 1, 0.25),
        (8, 8, 0.25),
    ],
)
def test_tiled_empty_mapped_size_or_tile_is_noop(
    monkeypatch, render_target, textures, width, height, scale
):
    handle = textures.create(1, 1, bytes((255, 0, 0, 255)))
    render_target.transform.set(0, 0, scale)
    scaling = Mock(side_effect=AssertionError("must not allocate a tile"))
    monkeypatch.setattr(module.pygame.transform, "scale", scaling)
    before = pygame.image.tostring(render_target.screen, "RGBA")
    textures.tiled(handle, 0, 0, width, height)
    scaling.assert_not_called()
    assert pygame.image.tostring(render_target.screen, "RGBA") == before
