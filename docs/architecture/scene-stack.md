# Scene Stack

Tatuy supports a stack rather than one global scene.

Each entry contains:

```text
scene ID
scene instance
overlay flag
ScenePolicy
```

## ScenePolicy

Controls:

```text
blocks_update
blocks_input
is_opaque
receives_input
```

## Visibility

Rendering walks visible entries from bottom to top.

An opaque scene hides entries below it.

## Input

The top-most eligible input receiver gets the effective input frame.

Other updating scenes receive an empty input frame.

## Updates

Update traversal respects `blocks_update`.

This allows patterns such as:

```text
Gameplay
   +
Pause overlay
```

where the pause overlay remains visible and receives input while stopping gameplay beneath it.

---
