# Configure a Game

TatuyApp accepts a configuration dictionary.

```python
app = TatuyApp(
    {
        "engine": {
            "start_scene": "main",
            "fps": 120,
            "debug_overlay": False,
        },
        "backend": {
            "window": {
                "width": 1280,
                "height": 720,
            },
        },
        "settings": {
            "my_game": {
                "difficulty": "normal",
            }
        },
        "profiler": {
            "enabled": False,
        },
    }
)
```

Top-level areas are:

```text
app
backend
engine
settings
profiler
```

Game-specific settings should use the settings registry rather than being hard-coded throughout gameplay systems.

---
