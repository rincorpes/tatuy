# Backend Factory

Most games should not need to instantiate concrete backends directly. Tatuy provides `BackendFactory` for this.

Instead of:

```python
backend = PygameBackend(
    PygameBackendConfig.from_dict(config)
)
```

you can use:

```python
backend = BackendFactory.create(
    "pygame",
    config, # This config is a dict.
)
```

The factory handles finding the backend implementation and letting its builder construct the correct configuration and backend instance. This becomes especially useful when the backend name comes from an application configuration file:

```python
backend = BackendFactory.create(
    self.app_config.backend,
    self.config.get("backend", {}),
)
```

Now the engine does not need code like:

```python
if backend == "pygame":
    ...
elif backend == "sdl":
    ...t
elif backend == "whatever-I-invent-nex":
    ...
```

That is exactly the type of code the registry exists to kill before it reproduces.

---

## Lazy Backend Discovery

`BackendFactory` lazily imports backend builders.

When:

```python
BackendFactory.create("pygame", config)
```

is called, the factory first checks whether `"pygame"` has already been registered. If not, it tries to import:

```text
tatuy.backend.pygame.builder
```

Importing that module executes the registration decorator:

```python
@BackendRegistry.implementation("pygame")
```

After that, the factory retrieves the builder and constructs the backend.

The flow looks like this:

```text
BackendFactory.create("pygame")
        ↓
Is "pygame" registered?
        ↓
       No
        ↓
Import tatuy.backend.pygame.builder
        ↓
Decorator registers PygameBackendBuilder
        ↓
Registry.get("pygame")
        ↓
builder.build(config)
        ↓
PygameBackend
```

This keeps concrete backend imports out of the core factory.

Adding another built-in backend does not require editing a giant registry dictionary.

That is Future Me's problem solved before Future Me can complain about Past Me.
