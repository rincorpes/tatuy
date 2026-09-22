# Pygame Backend

Pygame is currently Tatuy's default backend.

It implements the backend protocols using Pygame and exposes:

```text
PygameBackend
├── PygameEvents
├── PygameWindow
├── PygameInput
├── PygameRenderer
├── PygameAudio
└── PygameCapture
```

Each component implements one of Tatuy's backend capabilities.

This is important because Pygame itself is not allowed to become part of the engine's public architecture.

The backend is the wall between:

```text
Tatuy
```

and:

```text
pygame.*
```

Anything above that wall should speak Tatuy.

Anything below it is allowed to speak Pygame and worship `pygame.Surface`.
