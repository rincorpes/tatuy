# Audio

Tatuy exposes audio through runtime/backend abstractions rather than requiring game code to call Pygame directly.

Audio configuration can enable or disable the subsystem. Desktop runtimes may initialize enabled audio during backend startup, while browser hosts can defer initialization until the first user gesture by setting `auto_init: false`.

`AudioService` keeps game code host-neutral:

- sound loads requested before the device is ready are deferred until audio unlocks;
- key or pointer-button presses can unlock deferred audio at the host/runtime boundary;
- playback requests made while audio is still locked are safe no-ops;
- mute/unmute preserves the desired master volume;
- deferred initialization/load failures remain visible through `AudioService.last_error` without forcing the game loop to stop.

Game code should prefer Tatuy's audio service. Backend-specific audio initialization and playback implementation belong inside the backend layer.

---
