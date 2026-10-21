# Collisions

Tatuy currently supports:

- box colliders
- circle colliders
- polygon colliders
- collision bodies
- detection
- contact frames
- generic response

## Collision frame

Detection writes contacts into a `CollisionFrame`.

Game systems can inspect those contacts after detection.

This keeps:

```text
collision geometry
```

separate from:

```text
game meaning
```

The engine can determine that two objects collided.

The game decides whether that means:

- damage
- score
- pickup
- death
- wave progress

## Ordering

Advanced games may override collision built-ins when they need game rules inserted between detection and generic response.

---
