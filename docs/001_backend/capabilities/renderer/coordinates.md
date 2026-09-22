# Renderer Coordinates

Drawing operations use Tatuy's logical coordinate space. Before objects are sent to the actual backend, coordinates are transformed through the active `ViewportTransform`.

Conceptually:

```text
Game coordinates
      ↓
ViewportTransform
      ↓
Display coordinates
      ↓
Backend renderer
```

This allows game logic to work with a stable logical resolution even when the actual window size changes.

Without this layer, resizing a window becomes the traditional game-dev experience of discovering that everything is now three pixels to the left for reasons known only to God and floating-point arithmetic.
