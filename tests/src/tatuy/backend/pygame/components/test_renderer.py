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


@pytest.mark.xfail(strict=True, reason="B05: alpha polygon omits max boundary")
def test_alpha_polygon_includes_last_vertex(render_target):
    render_target.renderer.shape.polygon(
        [(2, 2), (8, 2), (8, 8), (2, 8)],
        (255, 0, 0, 128),
    )
    assert render_target.screen.get_at((8, 5)).r > 0


@pytest.mark.xfail(strict=True, reason="B06: tiled ignores viewport transform")
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
