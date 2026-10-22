# Examples

Tatuy examples are executable documentation.

```text
examples/
├── fundamentals/
├── experiments/
└── games/
```

Topic indexes:

- [Experiments](experiments.md)
- [Games](games.md)

## Fundamentals

Teach one concept with minimal unrelated behavior.

## Experiments

Explore architecture, performance, and APIs under real pressure.

## Games

Demonstrate larger feature integration.

Documentation should link to example source rather than reproducing entire example files.

## Maintenance contract

Examples participate in validating Tatuy changes but are not pytest test
targets.

When Tatuy engine behavior changes:

- review the nearest relevant fundamental
- review experiments using the affected capability
- review games using the affected capability
- add, update, or remove examples when necessary

Fundamentals should remain focused demonstrations of supported Tatuy APIs.

Experiments may intentionally pressure architecture or explore unfinished
ideas and are not automatically canonical API guidance.

Games demonstrate larger integration and should remain compatible with the
engine behavior they intentionally exercise.

---
