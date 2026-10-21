# World Internals

`World` stores:

```text
entities
components
resources
query strategy
```

Queries return entities matching requested component types.

Engine features should use the world API rather than relying directly on a particular internal component-storage representation.

This leaves room for future storage changes.

---
