# Internals

Internals documentation explains how Tatuy's architecture is implemented.

This section is primarily for:

- Tatuy contributors
- developers debugging engine behavior
- developers implementing alternative infrastructure
- technical reviewers exploring the codebase

Sections:

- [Engine](engine/index.md)
- [ECS](ecs/index.md)
- [Backend](backend/index.md)
- [Lifecycle](lifecycle/index.md)
- [Profiler](profiler/index.md)
- [MCP](mcp/index.md)
- [Dependency constraints](dependency-constraints.md)
- [Runtime dependencies and extras](runtime-dependencies.md)

Important contributor contracts:

- [Runtime feature composition](engine/runtime-feature-composition.md)
- [Render fallback handling](engine/render-fallback.md)
- [Kernel/reference implementation conventions](engine/kernel-conventions.md)

Read [`AGENTS.md`](../../AGENTS.md) before changing engine internals.

---