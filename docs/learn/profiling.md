# Profiling

Tatuy includes an engine-aware profiler.

Enable it:

```python
TatuyApp(
    {
        "profiler": {
            "enabled": True,
        }
    }
)
```

The profiler records hierarchical spans and metrics.

Typical areas include:

```text
frame
scene
system pipeline
system
lifecycle
rendering
events/input
custom game work
```

Game code can add its own spans:

```python
with profiler.span("enemy.update", "game"):
    ...
```

and metrics:

```python
profiler.metric("enemies", count)
```

When enabled, Tatuy exports the latest profile to:

```text
.tatuy/profiles/latest.json
```

View it with:

```bash
poetry run python -m tatuy_profiler .tatuy/profiles/latest.json
```

Profile before redesigning performance-sensitive infrastructure.
