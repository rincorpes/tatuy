# Backend Lifecycle

Backend lifecycle:

```text
construct
   ↓
init()
   ↓
capabilities available
   ↓
window open / runtime use
   ↓
stop()
```

Construction should not unexpectedly initialize platform devices.

Initialization prepares backend capabilities.

Window opening remains a separate platform operation.

Shutdown releases platform resources.

The former `docs/001_backend/lifecycle.md` should be migrated here.

---
