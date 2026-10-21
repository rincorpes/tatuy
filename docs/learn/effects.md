# Effects

Tatuy contains reusable presentation/simulation helpers for effects.

Current areas include:

- particles
- trails
- camera effects
- screen effects

Effects can span several phases.

For example:

```text
particle simulation
    ↓
trail state update
    ↓
presentation
```

A `GameSystem` is often a good way to group those related operations while keeping their phase placement explicit.

---
