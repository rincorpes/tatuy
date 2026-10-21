# Use Collisions

Attach a collider and collision body to relevant entities.

Ensure the scene provides `CollisionFrame` when collision processing is required.

Game rules can inspect contacts after detection:

```python
frame = ctx.world.get_resource(CollisionFrame)

for contact in frame.contacts:
    ...
```

Use helpers such as `match_contact()` to interpret semantic entity pairs.

Keep game consequences outside generic collision detection.

Override built-in collision scheduling only when the game genuinely requires different ordering.

---
