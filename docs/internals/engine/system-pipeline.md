# SystemPipeline Implementation

`SystemPipeline` stores scheduled steps by phase.

Important behavior:

```text
add registration
    ↓
build scheduled steps
    ↓
sort by order/name/sequence
    ↓
execute phases
```

Update phases include the two structural barriers.

Presentation runs only the presentation phase.

At a commit phase, the pipeline invokes its structural committer.

The pipeline also records diagnostic state for each scheduled step.

---
