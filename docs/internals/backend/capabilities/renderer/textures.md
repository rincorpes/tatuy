# Renderer Textures

`create(w, h, data, pitch=-1)` uploads four-channel RGBA bytes and returns
an integer handle. Pygame surfaces stay inside the implementation.

A non-positive pitch selects tightly packed rows (`w * 4` bytes).
The buffer must hold at least `h * pitch` bytes. Packed data goes through
`pygame.image.frombuffer(..., "RGBA").convert_alpha()`; padded rows are
repacked before conversion. Conversion requires an initialized display.
The converted surface does not retain the caller's mutable buffer.

Non-positive width/height, a positive pitch below `w * 4`, and a buffer
shorter than `h * pitch` raise `ValueError` before allocation/conversion or
handle creation. Extra trailing bytes are allowed. Non-positive pitch
retains the tightly packed-row convention.

`draw(handle, x, y, w, h, angle_deg=0.0)` maps logical position and dimensions
through the viewport, ignores missing handles and non-positive mapped sizes,
scales when needed, then rotates clockwise around the destination center
when an angle is supplied. Scaling/rotation currently occur on every draw.

`tiled(handle, x, y, w, h)` maps logical position and destination size
through the viewport, then stretches the source across the mapped width.
Its tile height is `round(source_height * viewport_scale)` screen pixels,
independent of the requested width. It repeats vertically and crops the
last tile to the remaining mapped destination height, without rescaling it.
The target surface's active clip applies and is left unchanged.
Missing/destroyed handles, non-positive mapped destination sizes, and tile
heights that round to zero are no-ops. Tiling remains vertical-only.

`destroy(handle)` removes a stored surface and silently ignores unknown
handles. Resource ownership belongs to the renderer instance; the protocol
does not expose a separate texture shutdown.

