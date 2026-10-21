# Backend Architecture

Tatuy high-level code depends on backend contracts rather than concrete Pygame classes.

The backend acts as a composition root for focused capabilities.

Rules:

1. depend on protocols/contracts rather than concrete implementations
2. keep platform-specific types contained
3. depend on the smallest capability required
4. keep capabilities focused
5. allow implementation-specific ugliness inside the implementation boundary

The backend boundary is allowed to know exactly how Pygame works.

The rest of the engine should not have to.

---
