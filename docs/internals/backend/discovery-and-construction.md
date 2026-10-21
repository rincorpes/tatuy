# Backend Discovery and Construction

Tatuy separates backend lookup from backend creation.

```text
BackendFactory
    ↓
BackendRegistry
    ↓
BackendBuilder
    ↓
BackendConfig
    ↓
Backend
```

## Registry

Maps backend names to builders.

## Builder

Converts raw configuration into the concrete backend/config pair.

## Factory

Looks up the backend name and asks its builder to construct the backend.

## Lazy discovery

If a built-in backend is not already registered, the factory can import its builder module so the registration decorator runs.

This avoids a giant hard-coded backend switch.

The former `registry.md` and `factory.md` should be merged here.

---
