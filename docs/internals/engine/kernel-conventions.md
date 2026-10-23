# Kernel and Reference Implementation Conventions

Tatuy kernel boundaries exist so hot engine work can move behind coarse-grained replaceable contracts while Python remains the authoring/orchestration layer.

Canonical architecture: [Kernel Boundaries](../../architecture/kernels.md).

## Kernel shape

Prefer:

```text
system / committer
    ↓ one operation
kernel contract
    ├── Python reference implementation
    └── future native implementation
```

Avoid per-entity Python/native crossings.

## System versus kernel ownership

The system/committer owns:

- phase placement
- activation/enablement
- orchestration with other systems
- game-facing extension points

The kernel owns:

- the batch operation over the relevant data
- implementation-specific iteration/storage strategy
- hot calculation that can be replaced without changing game code

Do not move scheduling policy into a kernel merely because the kernel may become native.

## Python reference behavior

Every kernelized subsystem keeps a Python implementation that defines observable behavior.

The reference implementation is valuable for:

- correctness tests
- debugging native implementations
- environments without native support
- authoring arbitrary Python-defined components/blueprints where the extension path remains Python-owned

A native implementation is conformant when it preserves the tested observable behavior, not when it copies the Python internal structure.

## Tests

Kernel work should include:

- direct reference-kernel behavior tests
- system delegation tests
- edge cases and side effects
- conformance tests that can later run against multiple implementations where practical

Game-facing tests should not assert private kernel representation.

## Native boundary checklist

Before introducing a native kernel, verify:

1. the Python contract is stable
2. the reference tests are complete
3. the call is coarse-grained
4. game code does not select native handles/storage layouts
5. Python extension points are either preserved above the boundary or explicitly isolated as fallback
6. scheduling remains owned by the Python system/runtime unless profiling proves otherwise

---