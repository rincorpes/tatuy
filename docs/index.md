# Tatuy Documentation

Tatuy is a Python-first 2D game engine built around scenes, ECS, explicit system scheduling, reusable features, and a replaceable backend boundary.

The documentation is organized around **what you are trying to accomplish**, not around the order in which Tatuy's source code was implemented.

## Choose your path

### Understand the project

If you are exploring Tatuy, reviewing the repository, or evaluating its architecture:

1. [Why Tatuy?](overview/why-tatuy.md)
2. [Architecture at a glance](overview/architecture-at-a-glance.md)
3. [Features](overview/features.md)
4. [Roadmap](overview/roadmap.md)

### Build a game

1. [Installation](getting-started/installation.md)
2. [Your first game](getting-started/first-game.md)
3. [Project structure](getting-started/project-structure.md)
4. [Learn Tatuy](learn/index.md)

### Solve a specific task

Use [Guides](guides/index.md).

### Look up exact behavior

Use the relevant [Learn](learn/index.md), [Guides](guides/index.md), and [Internals](internals/index.md) sections, then inspect the implementation when exact runtime behavior matters.

### Understand the architecture

Use [Architecture](architecture/index.md).

### Work on Tatuy itself

Use [Internals](internals/index.md), then inspect the implementation and nearby examples.

### Use an AI coding assistant

Read:

1. [`AGENTS.md`](https://github.com/rincorpes/tatuy/blob/main/AGENTS.md)
2. [AI development guide](ai/index.md)
3. [Architecture map](ai/architecture-map.md)
4. [Architectural invariants](ai/invariants.md)

## Documentation types

| Area | Purpose |
| --- | --- |
| `overview/` | Explain Tatuy quickly |
| `getting-started/` | Get something running |
| `learn/` | Teach concepts |
| `guides/` | Complete a task |
| `architecture/` | Explain design decisions |
| `internals/` | Explain implementation |
| `examples/` | Find executable demonstrations |
| `ai/` | Help agents navigate the project |

When documentation and current code disagree, inspect the implementation and update stale documentation.

---
