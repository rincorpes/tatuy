# System Pipeline Architecture

Tatuy uses explicit phases because simulation ordering matters.

```text
CONTROL
    ↓
PRE_SIMULATION
    ↓
PRE_SIM_COMMIT
    ↓
SIMULATION
    ↓
POST_SIMULATION
    ↓
POST_SIM_COMMIT
```

Presentation runs separately.

## Registrations become scheduled steps

A registration contains:

```text
system
optional phase override
optional order override
optional activation predicate
```

A `BaseSystem` normally creates one step.

A `GameSystem` may create one step per implemented phase callback.

## Why phase + order?

Phase communicates semantic location.

Order resolves sequencing inside that location.

This is easier to understand than one global list of arbitrary numeric priorities.

## Diagnostics

Scheduled steps track their latest state.

This allows the pipeline to expose whether a system:

- did not apply
- was disabled
- ran
- failed

The goal is inspectable execution.

---
