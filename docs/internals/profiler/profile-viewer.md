# Profile Viewer

The separate `tatuy_profiler` package serves exported profile JSON through a local browser UI.

Run:

```bash
poetry run python -m tatuy_profiler .tatuy/profiles/latest.json
```

The viewer should evolve toward helping answer:

- which frames were slowest?
- what dominated those frames?
- which systems ran?
- what workload existed?
- how does one frame compare with another?

---
