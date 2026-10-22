# Renderer Textures

`create(w, h, data, pitch=-1)` uploads four-channel RGBA bytes and returns
an integer handle. Pygame surfaces stay inside the implementation.

A non-positive pitch selects tightly packed rows (`w * 4` bytes).
The buffer must hold at least `h * pitch` bytes. Packed data goes through
`pygame.image.frombuffer(..., "RGBA").convert_alpha()`; padded rows are
repacked before conversion. Conversion requires an initialized display.
The converted surface does not retain the caller's mutable buffer.

The current code does not explicitly reject a positive pitch smaller than
`w * 4` or non-positive dimensions. Those values are not supported inputs;
error handling needs to be made explicit before expanding this contract.

`draw(handle, x, y, w, h, angle_deg=0.0)` maps logical position and dimensions
through the viewport, ignores missing handles and non-positive mapped sizes,
scales when needed, then rotates clockwise around the destination center
when an angle is supplied. Scaling/rotation currently occur on every draw.

`tiled(handle, x, y, w, h)` stretches the tile to the requested width,
repeats it vertically at its original pixel height, and crops the last tile.
It currently bypasses the viewport transform and raises KeyError for a
missing handle, unlike `draw`. It is not general two-axis tiling.

`destroy(handle)` removes a stored surface and silently ignores unknown
handles. Resource ownership belongs to the renderer instance; the protocol
does not expose a separate texture shutdown.

