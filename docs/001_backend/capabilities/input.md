# Input

Events describe things that happened, input describes the current state of an input device. Those are related concepts, but they are not the same thing.
 he `Input` capability currently provides pointer state and cursor control.

For example:

```python
pointer = backend.input.get_pointer_state()

print(pointer.position)
print(pointer.inside)
```

Cursor appearance can also be changed:

```python
backend.input.set_cursor(
    Cursor.HAND
)
```

Supported cursor types currently include:

- ARROW
- HAND
- TEXT

The Pygame implementation avoids resetting the cursor when the requested cursor is already active. Tiny optimization? Yes. Will it save the world? No. But neither will most code.
