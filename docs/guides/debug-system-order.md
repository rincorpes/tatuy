# Debug System Order

When behavior depends on scheduling:

1. identify the relevant phase
2. inspect built-ins
3. inspect game systems
4. compare `order` / `phase_orders`
5. inspect pipeline diagnostics

The pipeline can produce a debug report showing scheduled steps and latest execution state.

Remember that built-ins exist even if the scene's `game_systems()` does not list them.

---
