# Implementing a Backend

Start with `src/tatuy/backend/backend.py` and the capability protocols.
Implement config, events, window, input, renderer, audio, capture,
`viewport_transform`, `initialized`, `init()`, and `stop()`.

The renderer composes shape, text, texture, and clip capabilities.
Use the shared `ViewportTransform` consistently and specify byte formats,
coordinate units, ownership, and errors explicitly. Keep platform types
inside the implementation where practical. The existing window protocol's
`screen: Any` is an escape hatch, not a portable surface specification.

## Builder registration

Define concrete configuration types, normally frozen dataclasses extending
the shared types, and a builder extending `BackendBuilder`:

```python
from typing import Any

from tatuy.backend.backend import Backend
from tatuy.backend.registry import BackendBuilder, BackendRegistry

@BackendRegistry.implementation("custom")
class CustomBackendBuilder(BackendBuilder):
    def build(self, config: dict[str, Any]) -> Backend:
        # Decode config, then return your concrete backend.
        raise NotImplementedError
```

For a backend in `tatuy.backend.custom`, put registration in
`builder.py` for lazy discovery. For an external package, import the
registration module before `BackendFactory.create("custom", config)`.
Keep normalized registry keys consistent with the factory.

## Lifecycle and verification

Construction should not open devices. Initialization prepares capabilities;
window opening creates display resources. Design cleanup for partial
initialization, repeated shutdown, and repeated initialization explicitly.

Add tests under `tests/src/tatuy/backend/<implementation>/`, mirroring
source directories. Verify discovery errors, dictionary decoding, lifecycle,
event payloads, pointer bounds, viewport conversion, alpha/clipping,
texture byte layout and pitch, font selection, audio state, and capture bytes.
Use offscreen surfaces and mocks for unit tests; reserve real windows,
audio devices, and FFmpeg for separate integration checks.

The protocols are structural, but the current Pygame builder uses a cast.
A passing mypy run alone is therefore not proof that a concrete backend
satisfies every method signature. In particular, review the current
`Capture.bmp` default-argument mismatch before copying that implementation.

