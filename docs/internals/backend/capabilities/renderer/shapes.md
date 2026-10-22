# Renderer Shapes

The shape port exposes:

- `rect(pos: Vec2, size: Size, color, *, radius=0.0)`;
- `line(start: Vec2, end: Vec2, color, thickness=5)`;
- `circle(x, y, radius, color)`;
- `polygon(points, color, filled=True)`.

Colors are normalized through `ColorFormatter.rgba`.
Opaque shapes draw directly to the window surface. Translucent shapes use a
temporary SRCALPHA surface clipped to display bounds, then alpha-blit it onto
the target. A fully offscreen translucent shape returns without allocation.
The target surface's active clip also applies during drawing/blitting.

Polygons with fewer than three points are ignored. Outlined polygons use
one raster pixel. Line thickness and circle radius are logical dimensions
scaled through the viewport. Zero sizes are no-ops; negative line thickness
or circle radius raises `ValueError`. Positive sizes mapping to zero draw
nothing instead of being clamped to one pixel.

Translucent polygon bounds include both extreme vertex pixels after
viewport mapping (`max - min + 1` in screen pixels). The active target clip
is translated onto the temporary surface before drawing, preserving clipped
outline rasterization as well as the final blit's clipping.

Temporary alpha surfaces are allocated per draw. Profile actual workloads
before introducing pooling, batching, or native implementations.
See [Coordinates](coordinates.md) for scaling differences.

