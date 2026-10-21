# Entity Factory Internals

`EntityFactory` resolves blueprint names from:

1. the legacy/manual `registry`
2. the class-specific implementation registry

Blueprint instances are cached per factory instance.

Entity creation delegates to the selected blueprint.

Typed blueprints can:

- construct attrs
- add base components
- compose additional components
- create collider data
- create collision body data

Factory work is instrumented with profiler metrics.

---
