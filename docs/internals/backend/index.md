# Backend Internals

The backend is Tatuy's platform integration layer. Read
[Backend boundary](../../architecture/backend-boundary.md) for the architectural
reason behind it. The current implementation is Pygame.

## Read in this order

- [Architecture](architecture.md): capability composition and dependencies.
- [Discovery and construction](discovery-and-construction.md): factory,
  registry, builders, and error handling.
- [Configuration](configuration.md): defaults, dictionary decoding, and limits.
- [Lifecycle](lifecycle.md): construction, initialization, window opening,
  and shutdown.
- [Capabilities](capabilities/index.md): events, window, input, rendering,
  audio, and capture.
- [Pygame implementation](implementations/pygame.md): concrete implementation
  and verification.
- [Implementing a backend](implementing-a-backend.md): extension requirements.

Source lives in `src/tatuy/backend/`. Runtime adapters live in
`tatuy.events`, `tatuy.window`, `tatuy.input`, `tatuy.audio`,
`tatuy.capture`, and the engine render pipeline.

The backend owns platform operations. Replay orchestration, scene simulation,
capture workers, viewport policy, and game rules belong to higher layers.

