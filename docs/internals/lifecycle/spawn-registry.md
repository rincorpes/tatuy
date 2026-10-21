# SpawnRegistry Internals

`SpawnRegistry` maps gameplay definition names to `SpawnDefinition`s.

Scenes populate it during configuration.

Duplicate definitions are rejected.

Entity spawn requests reference the stable definition name rather than a blueprint directly.

---
