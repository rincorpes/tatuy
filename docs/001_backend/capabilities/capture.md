# Capture

The `Capture` capability provides access to the current rendered frame.

A screenshot can be written using:

```python
backend.capture.bmp(
    "capture.bmp"
)
```

The current frame can also be retrieved as raw pixel data:

```python
width, height, data = (
    backend.capture.argb8888_bytes()
)
```

This lower-level API exists primarily for systems such as frame recording and asynchronous video capture.

Normal games probably do not need it. Normal games also probably do not need a custom engine, yet here we are.
