# Backend Discovery and Construction

`BackendFactory.create(name, config)` normalizes the requested name with
`strip().casefold()`, resolves a `BackendBuilder`, and returns
`builder_type().build(config)`. It does not initialize the result.

```python
from tatuy.backend.factory import BackendFactory

backend = BackendFactory.create(
    "pygame",
    {"window": {"width": 640, "height": 360}},
)
assert backend.initialized is False
```

## Registry and lazy discovery

`BackendRegistry` extends Onomasticon's `ImplementationRegistry` with
`BackendBuilder` as its implementation base. A builder registers through
`@BackendRegistry.implementation("pygame")`.

If a normalized name is already registered, the factory uses it directly.
Otherwise it validates that the name is an identifier that does not start
with an underscore, then imports `tatuy.backend.<name>.builder`.
Importing the module runs its registration decorator. Installed custom
builders outside that package should be imported and registered before
calling the factory.

## Error contract

| Condition | Result |
| --- | --- |
| Unregistered invalid name | ValueError: Invalid backend name |
| Backend package or builder module missing | ValueError: Unknown backend, chained from ModuleNotFoundError |
| Builder's dependency missing | Original ModuleNotFoundError propagates |
| Module imports without registering the requested name | ValueError: Builder module did not register backend |
| Builder rejects configuration | Builder/configuration exception propagates |

The original configuration dictionary is passed to the builder. Pygame's
builder decodes it as `PygameBackendConfig`, verifies that concrete type,
and constructs `PygameBackend`.

The dictionary's `name` field does not override the factory argument.
Import discovery relies on Python module caching; it is not a hot-reload
or registry-reset mechanism.

Configuration decoding uses the canonical `BackendConfigError` in
`tatuy.backend.config`; the historical Pygame config import aliases the
same class. `PygameBackendError` derives from `BackendError` (and therefore
`TatuyError`). Invalid operation arguments remain `ValueError`.
Native Pygame/file errors retain their original types; there is no blanket
exception wrapping that would hide specific failure information.
