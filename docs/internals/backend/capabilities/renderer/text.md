# Renderer Text

`measure(text, font_size=None, font_name=None)` returns logical width/height.
`draw(x, y, text, color, font_size=None, font_name=None)` renders antialiased
text and applies the color's alpha as surface alpha before blitting.

PygameText stores configured font names/paths. Font objects are cached by
requested `(font_name, size)`. A missing path selects Pygame's default font.
Font-file errors propagate when the font is first needed.

Explicit font sizes scale with the viewport and clamp to at least 8 pixels.
An omitted size uses a 24-pixel fallback. Measurement
divides pixel dimensions by viewport scale (using 1.0 if scale is zero).

## Current selection behavior

For a recognized explicit name, its configured path is used.
An unknown name falls back to the `"default"` alias if present, otherwise to
the path named by `TextConfig.default_font`.

An omitted name currently follows that same fallback: the literal
`"default"` alias wins even if `default_font` explicitly selects another
font. This differs from the natural interpretation of that configuration
field and is covered by an expected-failure test.

`FontConfig.size` is not used by PygameText. An omitted font size is not
scaled with the viewport, unlike an explicitly supplied size.
Default-size and default-name semantics should be decided before changing
the implementation.

The cache retains fonts for every requested name/size pair during the
renderer lifetime. Continuous viewport/size changes can grow it; optimization
needs measurements and an agreed eviction policy.

