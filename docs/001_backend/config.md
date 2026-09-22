
# Backend Configuration

Every backend is configured using dataclasses.

The common configuration model is defined by `BackendConfig`:

```text
BackendConfig
├── EventsConfig
├── WindowConfig
├── InputConfig
├── RendererConfig
├── AudioConfig
└── CaptureConfig
```

Concrete backends can extend those configuration types when they need backend-specific options.

---

## Default configuration

The Pygame backend provides defaults, so the smallest valid configuration is simply:

```python
from tatuy.backend.pygame import PygameBackendConfig

config = PygameBackendConfig()
```

The backend name defaults to:

```python
"pygame"
```

Window defaults include:

```text
width:      800
height:     600
title:      "Pygame Backend"
resizable:  False
```

Other subsystems also provide sensible defaults.

This allows examples and experiments to start with very little configuration.

Because configuring 37 options before showing a rectangle is how frameworks become LinkedIn posts instead of game engines.

---

## Overriding defaults

Configuration objects are normal dataclasses.

For example:

```python
from tatuy.backend.pygame import (
    PygameBackendConfig,
    PygameWindowConfig,
)

config = PygameBackendConfig(
    window=PygameWindowConfig(
        width=1280,
        height=720,
        title="My Game",
        resizable=True,
    )
)
```

Only the settings that need to change have to be provide, everything else keeps its default value.

---

## Renderer configuration

Renderer configuration currently includes the background color and text configuration.

For example:

```python
from tatuy.backend.pygame import (
    PygameBackendConfig,
    PygameRendererConfig,
)

config = PygameBackendConfig(
    renderer=PygameRendererConfig(
        background_color=(20, 20, 20),
    )
)
```

---

## Audio configuration

Audio can be configured using:

```python
from tatuy.backend.pygame import (
    PygameAudioConfig,
    PygameBackendConfig,
)

config = PygameBackendConfig(
    audio=PygameAudioConfig(
        enabled=True,
        master_volume=0.8,
        frequency=44100,
        channels=2,
        chunk_size=2048,
    )
)
```

Audio can also be completely disabled:

```python
config = PygameBackendConfig(
    audio=PygameAudioConfig(
        enabled=False,
    )
)
```

When disabled, audio operations become effectively no-ops, the game keeps running, the speakers remain silent, everybody wins except the composer.

---

## Custom backend configuration

Concrete backends can extend any of the common configuration types.

For example:

```python
from dataclasses import dataclass

from tatuy.backend.config import RendererConfig


@dataclass(frozen=True)
class MyRendererConfig(RendererConfig):
    enable_extremely_questionable_feature: bool = True
```

The backend can then use this configuration internally while still satisfying Tatuy's common backend contracts.

## Configuration from Dictionaries

Backend configuration can also be created from dictionaries.

This is useful when configuration comes from TOML, JSON, YAML, project files, or another external source.

For example:

```python
config_data = {
    "window": {
        "width": 1280,
        "height": 720,
        "title": "My Game",
    },
    "audio": {
        "master_volume": 0.5,
    },
}
```

For a concrete Pygame configuration:

```python
config = PygameBackendConfig.from_dict(
    config_data
)
```

Tatuy recursively converts nested dictionaries into the appropriate configuration dataclasses.

That means:

```python
{
    "window": {
        "width": 1280
    }
}
```

becomes approximately:

```python
PygameBackendConfig(
    window=PygameWindowConfig(
        width=1280
    )
)
```

without making every caller manually reconstruct the entire object tree.

The decoder also understands common structures such as:

```text
Optional / Union values
Enums
Tuples
Lists
Dictionaries
Nested dataclasses
```
