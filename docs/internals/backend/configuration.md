# Backend Configuration

`BackendConfig` is a frozen dataclass with a required `name` and six
capability configurations. `PygameBackendConfig` supplies `name="pygame"`
and concrete capability defaults.

```python
from tatuy.backend.pygame import PygameBackendConfig

config = PygameBackendConfig.from_dict({
    "window": {
        "width": 1280,
        "height": 720,
        "title": "My game",
        "resizable": True,
    },
    "renderer": {
        "background_color": [24, 28, 36],
        "text": {
            "fonts": [
                {"name": "ui", "path": "assets/ui.ttf", "size": 24},
            ],
            "default_font": "ui",
        },
    },
    "audio": {
        "enabled": True,
        "auto_init": True,
        "master_volume": 0.5,
        "sounds": [
            {"name": "hit", "path": "assets/hit.wav"},
        ],
    },
})
assert isinstance(config, PygameBackendConfig)
assert config.window.width == 1280
assert PygameBackendConfig.from_dict(config.to_dict()) == config
```

With `TatuyApp`, `app.backend` selects the builder and the top-level
`backend` dictionary supplies these capability fields. The config's `name`
field does not select or validate the builder.

## Defaults and behavior

| Section | Fields and defaults |
| --- | --- |
| events | No configurable fields |
| window | width=800, height=600, title="Pygame Backend", resizable=False |
| renderer | background_color=(0, 0, 0); text configuration below |
| renderer.text | fonts=(), default_font="default" |
| audio | enabled=False, auto_init=True, master_volume=1.0, frequency=44100, channels=2, chunk_size=2048, sounds=() |
| input | enable_keyboard=True, enable_mouse=True, enable_gamepad=False |
| capture | enabled=False, directory="captures", format="png" |

The shared `WindowConfig` title defaults to `"tatuy"`; the concrete
Pygame type overrides it. Each font entry has `name`, optional `path`,
and `size=24`. Each sound requires `name` and `path`.

## Dictionary decoding

`from_dict()` delegates to `tatuy.dataclass_utils.dataclass_from_dict`.
It resolves nested dataclasses, enums, unions/optional values, tuples,
lists, and dictionaries from their annotations. Omitted values retain
defaults. Lists can populate tuple fields, including fonts and sounds.

Unknown fields, invalid primitive types, missing required fields, and
wrong tuple lengths become `tatuy.backend.config.BackendConfigError`
with the original `TypeError` or `ValueError` as its cause.
Booleans are not accepted as integers. Integer values are accepted for
float fields. Numeric strings are not coerced.

Decoding validates structure and types, not semantic ranges such as positive
window dimensions, valid mixer channel counts, or existing asset paths.
Frozen configuration prevents reassignment; runtime operations such as
resize do not rewrite configuration.

## Current limitations

- Input enable flags are not enforced by Pygame input or event polling;
  gamepad events are not translated.
- Pygame capture methods do not consult the capture configuration fields.
  Higher-level capture settings and services control capture workflows.
- Font entry `size` is decoded but not used as a per-font rendering default.
- See [Text](capabilities/renderer/text.md) for current default-font and
  viewport-size behavior, and [Audio](capabilities/audio.md) for volume
  units and initialization details.

These limitations describe the current source; they are not guarantees for
future backend implementations.

