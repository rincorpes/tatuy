"""Viewport resizing preserves logical resolution and maps host coordinates."""

from tatuy.geometry.size import Size
from tatuy.graphics.viewport.service import ViewportService


def test_resize_preserves_virtual_size_and_letterboxes_fit_mode() -> None:
    viewport = ViewportService()
    viewport.initialize(Size(800, 600))

    viewport.resize(Size(1000, 1000))

    state = viewport.state
    assert (state.virtual_w, state.virtual_h) == (800, 600)
    assert (state.window_w, state.window_h) == (1000, 1000)
    assert state.scale == 1.25
    assert (state.viewport_w, state.viewport_h) == (1000, 750)
    assert (state.offset_x, state.offset_y) == (0, 125)


def test_window_points_map_back_into_logical_coordinates() -> None:
    viewport = ViewportService()
    viewport.initialize(Size(800, 600))
    viewport.resize(Size(1000, 1000))

    assert viewport.contains_window_point(500, 500)
    assert viewport.window_to_virtual(500, 500) == (400, 300)
    assert not viewport.contains_window_point(500, 50)


def test_resize_upscales_without_changing_logical_resolution() -> None:
    viewport = ViewportService()
    viewport.initialize(Size(800, 600))

    viewport.resize(Size(1600, 1200))

    state = viewport.state
    assert (state.virtual_w, state.virtual_h) == (800, 600)
    assert state.scale == 2.0
    assert (state.viewport_w, state.viewport_h) == (1600, 1200)
    assert (state.offset_x, state.offset_y) == (0, 0)
