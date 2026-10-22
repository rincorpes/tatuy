# Capture Capability

The backend extracts rendered pixels. Screenshot paths, worker queues,
replay orchestration, and video encoding belong to higher-level capture
services.

## Pygame operations

`bmp(path: str | None = None)` returns false when the path is omitted,
`None`, or empty, without accessing the screen or saving a file.
Otherwise it calls
`pygame.image.save(window.screen, str(path))` and returns true.
Pygame chooses the encoding from the filename, so this method's name does
not force BMP when another extension is supplied. Save errors propagate;
the method does not create missing parent directories.

`bgra8888_bytes()` returns `(width, height, data)`. Data has four bytes
per pixel in B, G, R, A order, with `width * height * 4` bytes.
This matches the capture worker's BGRA decoding. The source docstrings
currently say ARGB in places; the actual export format is BGRA.

Saving to a nonempty path and extracting raw bytes need an available screen
surface. They do not check
`CaptureConfig.enabled`, `directory`, or `format`.

