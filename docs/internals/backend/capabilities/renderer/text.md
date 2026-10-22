# Renderer Text

`measure(text, font_size=None, font_name=None)` returns logical width/height.
`draw(x, y, text, color, font_size=None, font_name=None)` renders antialiased
text and applies the color's alpha as surface alpha before blitting.

PygameText stores configured font names/paths. Font objects are cached by
requested `(font_name, size)`. A missing path selects Pygame's default font.
Font-file errors propagate when the font is first needed.

Explicit and omitted font sizes are logical units and scale with the viewport.
The selected font's `FontConfig.size` supplies an omitted size; an unconfigured
font falls back to 24 logical units. Explicit sizes override the font default.
Raster sizes round once and clamp to at least 8 pixels. Measurement divides
pixel dimensions by viewport scale (using 1.0 when scale is zero).

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

Font fallback resolves name/path/size together: unknown explicit names use
the literal default alias when present, otherwise the configured default.
An omitted name uses only the configured default, preserving B07 semantics.
Both measure and draw share this resolution and the scaled-size cache.

Omitted sizes now scale; callers relying on the former fixed 24 screen
pixels should provide a suitable logical size for their viewport.
The cache retains fonts for requested name/size pairs during renderer life;
an eviction policy should follow measurements rather than arbitrary limits.
