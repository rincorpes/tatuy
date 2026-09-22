
# Window

The `Window` capability represents the game window.

Its responsibilities include:

- Opening the window
- Reading its size
- Changing the title
- Resizing
- Tracking its position
- Tracking minimized/maximized state
- Tracking close requests

A window can be opened with:

```python
backend.window.open()
```

Its size can be inspected using:

```python
size = backend.window.size

print(size.width)
print(size.height)
```

The title can be changed at runtime:

```python
backend.window.set_title(
    "Tatuy - Definitely Not Crashing"
)
```

And the window can be resized:

```python
backend.window.resize(
    1280,
    720,
)
```

The important part is that game code interacts with the `Window` protocol rather than directly using Pygame's display API.
