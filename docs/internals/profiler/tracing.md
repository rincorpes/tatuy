# Profiler Tracing

Spans form hierarchical execution trees.

Typical engine instrumentation includes:

```text
frame
scene
system_pipeline
system
lifecycle
render
events
```

Custom game spans can participate in the same hierarchy.

Trace structure should preserve enough context to explain where frame time was spent.

---
