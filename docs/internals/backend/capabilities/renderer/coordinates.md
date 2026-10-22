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

`texture.tiled()` maps position and destination dimensions like
`texture.draw()`. Source tile height is treated as logical height and
scaled independently of the stretched destination width. Repetition and
the final crop use the resulting integer screen dimensions.

Viewport policy and camera/world-to-view conversion belong to rendering
infrastructure above this port. Do not add backend-specific coordinate
conversion to gameplay to compensate for these differences.

