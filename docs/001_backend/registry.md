# Backend Registry

Backend implementations are registered through `BackendRegistry`. Each backend should provide a `BackendBuilder`, the builder has one responsibility:

> Convert configuration data into a concrete backend instance.

The interface is:

```python
class BackendBuilder(ABC):
    @abstractmethod
    def build(
        self,
        config: dict[str, Any],
    ) -> Backend:
        ...
```

A Pygame builder looks like:

```python
@BackendRegistry.implementation("pygame")
class PygameBackendBuilder(BackendBuilder):
    def build(
        self,
        config: dict[str, Any],
    ) -> Backend:
        backend_config = (
            PygameBackendConfig.from_dict(config)
        )

        if not isinstance(
            backend_config,
            PygameBackendConfig,
        ):
            raise TypeError(
                "Expected PygameBackendConfig"
            )

        return PygameBackend(backend_config)
```

The registry therefore connects:

```text
"pygame"
    ↓
PygameBackendBuilder
    ↓
PygameBackendConfig
    ↓
PygameBackend
```
