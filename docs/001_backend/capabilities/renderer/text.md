# Text

Text rendering is available through:

```python
backend.renderer.text
```

Text can be drawn using:

```python
backend.renderer.text.draw(
    x=100,
    y=100,
    text="Hello Tatuy",
    color=(255, 255, 255),
    font_size=24,
)
```

Text can also be measured before drawing:

```python
width, height = (
    backend.renderer.text.measure(
        "Game Over",
        font_size=32,
    )
)
```

This is useful for centering text, layout calculations, menus, UI, and every other place where you eventually discover that text is somehow harder than drawing a triangle.

---

## Fonts

Fonts can be configured through `TextConfig`.

For example:

```python
TextConfig(
    fonts=(
        FontConfig(
            name="ui",
            path="assets/fonts/ui.ttf",
            size=24,
        ),
    ),
    default_font="ui",
)
```

The renderer keeps an internal cache of created font objects so it does not recreate the same font every time text is drawn.
