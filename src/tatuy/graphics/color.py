from __future__ import annotations

ColorRGB = tuple[int, int, int]
ColorRGBA = tuple[int, int, int, int]

Color = ColorRGB | ColorRGBA
Alpha = float | int


class ColorFormatter:

    @classmethod
    def alpha_to_u8(cls, alpha: Alpha | None) -> int:
        """
        Convert an alpha value to an 8-bit integer (0-255).
        """
        if alpha is None:
            return 255
        if isinstance(alpha, bool):
            raise TypeError("alpha must be a float in [0,1], not bool")
        if isinstance(alpha, int):
            if not 0 <= alpha <= 255:
                raise ValueError(
                    f"int alpha must be in [0, 255], got {alpha!r}"
                )
            return alpha

        a = float(alpha)
        if not 0.0 <= a <= 1.0:
            raise ValueError(f"float alpha must be in [0,1], got {alpha!r}")
        return int(round(a * 255))

    @classmethod
    def rgba(cls, color: Color) -> ColorRGBA:
        """
        Convert a color tuple to RGBA format.
        """
        if len(color) == 3:
            r, g, b = color
            return int(r), int(g), int(b), 255
        if len(color) == 4:
            r, g, b, a = color
            return int(r), int(g), int(b), ColorFormatter.alpha_to_u8(a)
        raise ValueError(f"Color must be (r,g,b) or (r,g,b,a), got {color!r}")
