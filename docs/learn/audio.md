# Audio

Tatuy exposes audio through runtime/backend abstractions rather than requiring game code to call Pygame directly.

Audio configuration can enable or disable the subsystem.

Game code should prefer Tatuy's audio service.

Backend-specific audio initialization and playback implementation belong inside the backend layer.

---
