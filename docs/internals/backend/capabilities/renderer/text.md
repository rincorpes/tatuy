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

## Font selection

An omitted name (`font_name=None`) uses `TextConfig.default_font`.
If that name has no configured path, Pygame's built-in font is used.
A literal `"default"` alias does not override this selection.

A recognized explicit name uses its configured path. A missing path selects
Pygame's built-in font. An unknown explicit name preserves the fallback:
use the `"default"` alias if present, otherwise the path selected by
`TextConfig.default_font`. If that path is missing, use the built-in font.
Font-file errors still propagate rather than selecting another font.

Measurement and drawing share selection and caching. Callers that relied
on the literal alias for omitted names can pass `font_name="default"`
explicitly or set `default_font="default"`.

## Sizes and caching

`FontConfig.size` is not used by PygameText. An omitted font size is not
scaled with the viewport, unlike an explicitly supplied size.
Default-size and default-name semantics should be decided before changing
the implementation.

The cache retains fonts for every requested name/size pair during the
renderer lifetime. Continuous viewport/size changes can grow it; optimization
needs measurements and an agreed eviction policy.

