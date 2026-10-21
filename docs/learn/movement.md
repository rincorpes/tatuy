# Movement

Tatuy separates several movement concepts.

At the lowest level:

```text
Transform
+
Velocity
    ↓
VelocityIntegrationSystem
```

Higher-level controlled movement can use:

```text
MovementControls
DesiredMovement
Movement
Velocity
Transform
```

Conceptually:

```text
input
 ↓
desired direction
 ↓
movement acceleration/speed
 ↓
velocity
 ↓
position
```

This allows control logic to remain separate from spatial integration.

Movement behavior is supplied by built-ins when the required component combinations exist.

---
