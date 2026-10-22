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
one-pixel width. Circles currently clamp their mapped radius to at least
one pixel, even for a zero/negative logical radius. Input range policy is
not otherwise validated consistently.

Translucent polygon temporary bounds currently use `max - min` rather than
including the final vertex pixel. This clips the rightmost/bottommost
boundary compared with opaque rendering; an expected-failure pixel test
records the issue.

Temporary alpha surfaces are allocated per draw. Profile actual workloads
before introducing pooling, batching, or native implementations.
See [Coordinates](coordinates.md) for scaling differences.

