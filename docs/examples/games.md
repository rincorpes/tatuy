# Games

Larger games demonstrate how several Tatuy features work together while keeping the same game-facing APIs used by fundamentals.

## Public showcase status

| Game | Browser status | Notes |
| --- | --- | --- |
| [Pong](https://github.com/rincorpes/tatuy/tree/main/examples/games/001_pong) | Pending | Browser-safe OGG audio assets are still required before promotion. |
| [Breakout](https://github.com/rincorpes/tatuy/tree/main/examples/games/002_breakout) | Candidate | Tracked for a later browser migration pass. |
| [Snake](https://github.com/rincorpes/tatuy/tree/main/examples/games/003_snake) | Playable | Public V0 game; use WASD to change direction. |
| [Asteroids](https://github.com/rincorpes/tatuy/tree/main/examples/games/004_asteroids) | Candidate | Tracked for a later browser migration pass. |

Snake is intentionally the first browser game because it is self-contained and exercises ECS, lifecycle, grid placement, rendering, and discrete keyboard input without adding browser-only game code.

Pong and Breakout remain canonical reference games even while their browser promotion is pending; browser support is tracked independently through their showcase metadata.

---
