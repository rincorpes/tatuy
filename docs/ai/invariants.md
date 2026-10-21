# Architectural Invariants

1. Game rules belong in games.
2. Reusable mechanics belong in engine features.
3. Preserve control → simulation → presentation separation.
4. Structural changes use lifecycle or structural-command mechanisms.
5. Commit phases are synchronization barriers, not normal game hooks.
6. Reuse built-ins before recreating their behavior.
7. Built-ins activate from relevant world state.
8. `GameSystem` groups coherent gameplay behavior across phases.
9. Backend-specific behavior stays inside the backend where practical.
10. Depend on the smallest useful interface.
11. Prefer declarative scene hooks over giant `on_enter()` setup.
12. Initial and runtime spawning share lifecycle machinery.
13. Use resources for scene-wide state.
14. Components primarily hold state.
15. Optimize from profiler evidence.
16. Experiments are not automatically public API patterns.
17. Public API changes should update docs/examples/tests.
18. Verify imports, signatures, ordering, and lifecycle timing against source.
19. Prefer narrow reusable changes over broad framework redesign.
20. Current intentional source behavior is authoritative when docs are stale.

---
