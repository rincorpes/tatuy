# Runtime Services

Tatuy keeps runtime capabilities behind focused services.

Examples include:

```text
SceneService
ViewportService
EventsService
WindowService
InputService
CaptureService
AudioService
```

This avoids requiring game-facing code to manipulate the backend directly.

Services form a boundary between:

```text
engine/game concepts
```

and:

```text
platform implementation
```

Depend on the smallest useful service/capability rather than passing the entire runtime everywhere.

---
