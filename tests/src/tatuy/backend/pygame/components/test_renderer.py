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
    # TODO(web): Replace deprecated tostring snapshots with pygame.image.tobytes.
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
    "points,expected_points",
    [
        (
            [(4, 2), (4, 5), (4, 8)],
            {(4, y) for y in range(2, 9)},
        ),
        (
            [(2, 4), (5, 4), (8, 4)],
            {(x, 4) for x in range(2, 9)},
        ),
        ([(4, 4), (4, 4), (4, 4)], {(4, 4)}),
    ],
)
@pytest.mark.parametrize(
    "color,expected_red",
    [((255, 0, 0), 255), ((255, 0, 0, 128), 128)],
)
def test_collapsed_polygon_uses_inclusive_line_coverage(
    render_target,
    points,
    expected_points,
    color,
    expected_red,
):
    render_target.renderer.shape.polygon(points, color)
    actual_points = {
        (x, y)
        for y in range(render_target.screen.get_height())
        for x in range(render_target.screen.get_width())
        if render_target.screen.get_at((x, y)).r
    }
    assert actual_points == expected_points
    for point in expected_points:
        assert render_target.screen.get_at(point).r == expected_red


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
    # TODO(web): Replace deprecated tostring snapshots with pygame.image.tobytes.
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
    # TODO(web): Replace deprecated tostring snapshots with pygame.image.tobytes.
    handle = textures.create(1, 1, bytes((255, 0, 0, 255)))
    render_target.transform.set(0, 0, scale)
    scaling = Mock(side_effect=AssertionError("must not allocate a tile"))
    monkeypatch.setattr(module.pygame.transform, "scale", scaling)
    before = pygame.image.tostring(render_target.screen, "RGBA")
    textures.tiled(handle, 0, 0, width, height)
    scaling.assert_not_called()
    assert pygame.image.tostring(render_target.screen, "RGBA") == before


@pytest.mark.parametrize(
    "fonts,default_font,font_name,expected",
    [
        (
            (FontConfig("default", "old.ttf"), FontConfig("ui", "ui.ttf")),
            "ui",
            None,
            "ui.ttf",
        ),
        ((FontConfig("default", "old.ttf"),), "missing", None, None),
        (
            (FontConfig("default", "old.ttf"), FontConfig("ui", "ui.ttf")),
            "ui",
            "default",
            "old.ttf",
        ),
        (
            (FontConfig("default", "old.ttf"), FontConfig("ui", "ui.ttf")),
            "ui",
            "missing",
            "old.ttf",
        ),
        ((FontConfig("ui", "ui.ttf"),), "ui", "missing", "ui.ttf"),
        ((), "default", None, None),
        ((), "default", "missing", None),
        (
            (FontConfig("default", "old.ttf"), FontConfig("ui", None)),
            "ui",
            "ui",
            None,
        ),
        (
            (FontConfig("default", "old.ttf"), FontConfig("ui", None)),
            "ui",
            None,
            None,
        ),
    ],
)
def test_font_selection_matches_for_measure_and_draw(
    monkeypatch, render_target, fonts, default_font, font_name, expected
):
    font_type = Mock()
    font_type.return_value.size.return_value = (10, 12)
    font_type.return_value.render.return_value = pygame.Surface((2, 2))
    monkeypatch.setattr(module.pygame.font, "Font", font_type)
    text = module.PygameText(
        module.PygameRendererContext(
            render_target.window, render_target.transform
        ),
        TextConfig(fonts=fonts, default_font=default_font),
    )
    assert text.measure("hello", font_size=16, font_name=font_name) == (10, 12)
    text.draw(1, 1, "hello", font_size=16, font_name=font_name)
    # Measuring and drawing reuse the selected font at the same size.
    font_type.assert_called_once_with(expected, 16)
    font_type.return_value.render.assert_called_once_with(
        "hello", True, (255, 255, 255)
    )


def test_configured_font_load_errors_propagate(monkeypatch, render_target):
    error = FileNotFoundError("missing configured font")
    font_type = Mock(side_effect=error)
    monkeypatch.setattr(module.pygame.font, "Font", font_type)
    text = module.PygameText(
        module.PygameRendererContext(
            render_target.window, render_target.transform
        ),
        TextConfig(
            fonts=(
                FontConfig("default", "old.ttf"),
                FontConfig("ui", "bad.ttf"),
            ),
            default_font="ui",
        ),
    )
    with pytest.raises(FileNotFoundError) as caught:
        text.measure("hello")
    assert caught.value is error
    font_type.assert_called_once_with("bad.ttf", 24)


@pytest.mark.parametrize(
    "w,h,pitch", [(0, 2, -1), (-1, 2, -1), (2, 0, -1), (2, -1, -1), (2, 2, 7)]
)
def test_invalid_texture_geometry_fails_before_conversion(
    monkeypatch, textures, w, h, pitch
):
    conversion = Mock()
    monkeypatch.setattr(module.pygame.image, "frombuffer", conversion)
    with pytest.raises(ValueError):
        textures.create(w, h, bytes(100), pitch=pitch)
    conversion.assert_not_called()


@pytest.mark.parametrize("shape", ["line", "circle"])
@pytest.mark.parametrize("size", [0, -1])
def test_invalid_shape_sizes(render_target, shape, size):
    # TODO(web): Replace deprecated tostring snapshots with pygame.image.tobytes.
    before = pygame.image.tostring(render_target.screen, "RGBA")

    def draw():
        if shape == "line":
            render_target.renderer.shape.line(
                Vec2(1, 1), Vec2(8, 8), thickness=size
            )
        else:
            render_target.renderer.shape.circle(8, 8, size)

    if size < 0:
        with pytest.raises(ValueError):
            draw()
    else:
        draw()
    assert pygame.image.tostring(render_target.screen, "RGBA") == before


def test_line_thickness_scales_with_viewport(monkeypatch, render_target):
    draw = Mock()
    monkeypatch.setattr(module.pygame.draw, "line", draw)
    render_target.transform.set(0, 0, 2)
    render_target.renderer.shape.line(Vec2(1, 1), Vec2(8, 8), thickness=3)
    assert draw.call_args.args[-1] == 6


def test_tiny_shapes_rounding_to_zero_are_noops(render_target):
    # TODO(web): Replace deprecated tostring snapshots with pygame.image.tobytes.
    render_target.transform.set(0, 0, 0.1)
    before = pygame.image.tostring(render_target.screen, "RGBA")
    render_target.renderer.shape.line(Vec2(1, 1), Vec2(8, 8), thickness=1)
    render_target.renderer.shape.circle(8, 8, 1)
    assert pygame.image.tostring(render_target.screen, "RGBA") == before


@pytest.mark.parametrize(
    "name,size,expected",
    [
        (None, None, 36),
        ("ui", None, 36),
        ("default", None, 40),
        ("missing", None, 40),
        (None, 12, 24),
    ],
)
def test_font_default_sizes_scale_once(
    monkeypatch, render_target, name, size, expected
):
    font = Mock()
    font.return_value.size.return_value = (20, 20)
    font.return_value.render.return_value = pygame.Surface((2, 2))
    monkeypatch.setattr(module.pygame.font, "Font", font)
    render_target.transform.set(0, 0, 2)
    text = module.PygameText(
        module.PygameRendererContext(
            render_target.window, render_target.transform
        ),
        TextConfig(
            fonts=(
                FontConfig("ui", None, 18),
                FontConfig("default", None, 20),
            ),
            default_font="ui",
        ),
    )
    assert text.measure("hello", size, name) == (10, 10)
    text.draw(0, 0, "hello", font_size=size, font_name=name)
    font.assert_called_once_with(None, expected)


def test_clear_color_setter_has_no_stdout(render_target, capsys):
    render_target.renderer.set_clear_color(1, 2, 3)
    assert capsys.readouterr().out == ""


@pytest.mark.parametrize("pitch", [-1, 8])
@pytest.mark.parametrize("pixel_format", ["B", "I"])
@pytest.mark.parametrize("multidimensional", [False, True])
def test_texture_upload_normalizes_memoryview_bytes(
    monkeypatch, render_target, textures, pitch, pixel_format, multidimensional
):
    pixels = bytes((255, 0, 0, 255, 0, 255, 0, 255))
    rows = pixels if pitch < 0 else pixels[:4] + b"pad!" + pixels[4:] + b"pad!"
    # Trailing bytes expose element-based slicing in the packed path too.
    storage = bytearray(rows + b"trailing")
    view = memoryview(storage).cast(pixel_format)
    if multidimensional:
        view = view.cast("B").cast(pixel_format, shape=(2, len(view) // 2))
    conversion = Mock(wraps=module.pygame.image.frombuffer)
    monkeypatch.setattr(module.pygame.image, "frombuffer", conversion)

    handle = textures.create(1, 2, view, pitch=pitch)
    assert bytes(conversion.call_args.args[0]) == pixels
    storage[:] = bytes(len(storage))
    textures.draw(handle, 2, 2, 1, 2)
    assert render_target.screen.get_at((2, 2))[:3] == (255, 0, 0)
    assert render_target.screen.get_at((2, 3))[:3] == (0, 255, 0)


@pytest.mark.parametrize("pitch", [-1, 8])
@pytest.mark.parametrize("step", [2, -1])
def test_texture_rejects_noncontiguous_memoryviews_before_conversion(
    monkeypatch, textures, pitch, step
):
    conversion = Mock()
    monkeypatch.setattr(module.pygame.image, "frombuffer", conversion)
    view = memoryview(bytes(32))[::step]
    with pytest.raises(ValueError, match="C-contiguous"):
        textures.create(1, 2, view, pitch=pitch)
    conversion.assert_not_called()


@pytest.mark.parametrize("pitch", [-1, 8])
def test_texture_rejects_short_typed_memoryviews(monkeypatch, textures, pitch):
    conversion = Mock()
    monkeypatch.setattr(module.pygame.image, "frombuffer", conversion)
    needed = 8 if pitch < 0 else 16
    view = memoryview(bytes(needed - 4)).cast("I")
    with pytest.raises(ValueError, match="buffer too small"):
        textures.create(1, 2, view, pitch=pitch)
    conversion.assert_not_called()
