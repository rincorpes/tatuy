# Input and Intent

Tatuy separates raw device input from game meaning.

```text
device events
    ↓
InputFrame
    ↓
Intent
    ↓
game behavior
```

## InputFrame

The runtime input service produces a snapshot of the current input state.

## Intent

A game-specific `Intent` translates that snapshot.

```python
class GameIntent(Intent):
    move_left: bool = False

    def update_from(self, input_frame):
        self.move_left = input_frame.is_down(Key.A)
```

Game systems can then consume:

```text
move_left
launch
pause
aim
```

rather than repeatedly interpreting hardware state.

## Why?

This keeps:

```text
input device
```

separate from:

```text
game action
```

and also helps replay systems reproduce the same input-level behavior.

---
