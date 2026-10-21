# Backend Configuration

Backend configuration mirrors the backend capability tree.

Conceptually:

```text
BackendConfig
├── events
├── window
├── input
├── renderer
├── audio
└── capture
```

Concrete backends may extend these configuration types.

Pygame provides defaults so games can start with minimal configuration.

Backend configuration can be constructed from dictionaries and recursively converted into the appropriate dataclass structure.

Supported nested structures include ordinary dataclasses, enums, optional/union values, tuples, lists, and dictionaries.

The detailed configuration examples from the former `docs/001_backend/config.md` belong here.

---
