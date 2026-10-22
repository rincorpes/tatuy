# Renderer Coordinates

Backend drawing uses a top-left origin, X increasing right, and Y increasing
down. Most drawing methods accept logical integer coordinates and apply
the shared `ViewportTransform`:

- position: round(offset + coordinate * scale);
- dimensions: round(dimension * scale).

Shapes, text positions, texture draw, and clip rectangles apply this
transform. Text measurement returns dimensions converted back to logical
units. Shape inputs that use `Vec2` are currently truncated to integers
before mapping, so fractional logical positions lose precision.

Circles scale their radius; rectangle corner radii scale too.
Line thickness currently remains in screen pixels. Text's explicit font
size scales with the viewport, but an omitted size takes the unscaled
24-pixel fallback.

`texture.tiled()` currently bypasses viewport transformation entirely,
unlike `texture.draw()`. Treat this as an unresolved inconsistency, not a
portable rule to reproduce in another backend.

Viewport policy and camera/world-to-view conversion belong to rendering
infrastructure above this port. Do not add backend-specific coordinate
conversion to gameplay to compensate for these differences.

