# Backend Boundary

The backend is Tatuy's platform-facing boundary.

```text
Game
  ↓
Tatuy
  ↓
Backend contracts
  ↓
Pygame
```

A future implementation could replace Pygame without requiring gameplay systems to understand SDL, native handles, or another low-level API.

## Capabilities

```text
Backend
├── Events
├── Window
├── Input
├── Renderer
├── Audio
└── Capture
```

## Rules

- Do not leak Pygame types upward unnecessarily.
- Depend on the smallest capability required.
- Keep platform-specific work inside the backend.
- Do not add abstractions merely because a hypothetical backend might need them someday.

The boundary exists because Tatuy genuinely expects platform infrastructure to be replaceable.
