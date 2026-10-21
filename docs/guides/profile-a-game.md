# Profile a Game

Enable profiling:

```python
"profiler": {
    "enabled": True,
}
```

Run the actual workload you care about.

On exit Tatuy writes:

```text
.tatuy/profiles/latest.json
```

Open it:

```bash
poetry run python -m tatuy_profiler .tatuy/profiles/latest.json
```

When diagnosing performance:

1. inspect slow frames
2. find dominant spans
3. inspect metrics
4. identify whether the cost is game-specific or reusable engine infrastructure
5. optimize only after identifying the actual bottleneck

---
