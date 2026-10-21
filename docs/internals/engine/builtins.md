# Built-in System Catalog

`BuiltinSystemCatalog` creates fresh registrations for each scene.

Each built-in defines:

- system instance
- optional order
- activation predicate

The scene may modify that dictionary through `builtin_overrides()` before the pipeline is constructed.

This is the authoritative implementation behind [Built-in systems reference](../../reference/built-in-systems.md).

---
