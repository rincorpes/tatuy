# Capture Capability

The backend extracts rendered pixels. Screenshot paths, worker queues,
replay orchestration, and video encoding belong to higher-level capture
services.

## Pygame operations

`bmp(path)` returns false for an empty path. Otherwise it calls
`pygame.image.save(window.screen, str(path))` and returns true.
Pygame chooses the encoding from the filename, so this method's name does
not force BMP when another extension is supplied. Save errors propagate;
the method does not create missing parent directories.

`bgra8888_bytes()` returns `(width, height, data)`. Data has four bytes
per pixel in B, G, R, A order, with `width * height * 4` bytes.
This matches the capture worker's BGRA decoding. The source docstrings
currently say ARGB in places; the actual export format is BGRA.

Both operations need an available screen surface. They do not check
`CaptureConfig.enabled`, `directory`, or `format`.

## Contract issue

The shared protocol allows `bmp(path: str | None = None)`. The concrete
Pygame implementation requires `path: str`, so calling `bmp()` through the
documented protocol fails with TypeError. Callers should pass an explicit
path until the contract is aligned. The choice between requiring a path
everywhere and supporting an omitted path remains an implementation decision.

