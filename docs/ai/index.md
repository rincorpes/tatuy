# AI Development Guide

Tatuy provides AI-oriented documentation to reduce blind repository
exploration and make architectural constraints explicit.

Before proposing a change:

1. read `/AGENTS.md`
2. read [Architecture map](architecture-map.md)
3. read [Invariants](invariants.md)
4. inspect relevant canonical documentation
5. inspect the current implementation
6. identify relevant Tatuy-owned source/tooling tests
7. when changing `src/tatuy`, inspect the nearest relevant fundamental
8. search experiments and games that use the affected capability

Pytest tests validate Tatuy-owned source and tooling. Fundamentals,
experiments, and games are executable documentation and integration
pressure rather than pytest targets.

Do not invent APIs because they would be convenient.

Verify current source.
