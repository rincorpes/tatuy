"""Contracts for shapes, text, textures, clipping, and frame presentation."""

from __future__ import annotations

from typing import Protocol

from tatuy.backend.config import RendererConfig
from tatuy.geometry.size import Size
from tatuy.graphics.color import Color
from tatuy.graphics.viewport.transform import ViewportTransform
from tatuy.math.vec2 import Vec2


class Shape(Protocol):
    """Draw logical geometry and colors through the backend viewport."""

    def rect(
        self,
        pos: Vec2,
        size: Size,
        color: Color = (255, 255, 255),
        *,
        radius: float = 0.0,
    ):
        """Draw a logical rectangle, optionally with rounded corners.

        Args:
            pos (Vec2): Top-left position in logical coordinates.
            size (Size): Width and height in logical units.
            color (Color): RGB or RGBA drawing color; omitted alpha is opaque.
            radius (float): Rounded-corner radius in logical units.

        Returns:
            None: This method does not return a value.
        """

    def line(
        self,
        start: Vec2,
        end: Vec2,
        color: Color = (255, 255, 255),
        thickness=5,
    ):
        """Draw a line whose thickness is expressed in logical units.

        Args:
            start (Vec2): Starting point in logical coordinates.
            end (Vec2): Ending point in logical coordinates.
            color (Color): RGB or RGBA drawing color; omitted alpha is opaque.
            thickness (int): Nonnegative line width in logical units; zero
                draws nothing.

        Returns:
            None: This method does not return a value.

        Raises:
            ValueError: Thickness is negative.
        """

    def circle(
        self, x: int, y: int, radius: int, color: Color = (255, 255, 255)
    ):
        """Draw a circle whose center and radius are expressed in logical units.

        Args:
            x (int): Horizontal position in logical coordinates.
            y (int): Vertical position in logical coordinates.
            radius (int): Nonnegative circle radius in logical units; zero
                draws nothing.
            color (Color): RGB or RGBA drawing color; omitted alpha is opaque.

        Returns:
            None: This method does not return a value.

        Raises:
            ValueError: Radius is negative.
        """

    def polygon(
        self,
        points: list[tuple[int, int]],
        color: Color = (255, 255, 255),
        filled: bool = True,
    ):
        """Draw a filled polygon or a one-pixel outline from logical vertices.

        Args:
            points (list[tuple[int, int]]): Polygon vertices in logical
                coordinates.
            color (Color): RGB or RGBA drawing color; omitted alpha is opaque.
            filled (bool): Whether to fill the polygon instead of drawing a
                one-pixel outline.

        Returns:
            None: This method does not return a value.
        """


class Text(Protocol):
    """Measure and draw text using configured font aliases and logical sizes."""

    def measure(
        self,
        text: str,
        font_size: int | None = None,
        font_name: str | None = None,
    ) -> tuple[int, int]:
        """Return logical text dimensions using the selected font and logical size.

        Args:
            text (str): Text to measure or render.
            font_size (int | None): Logical font size, or None to use the
                selected font configuration.
            font_name (str | None): Font alias, or None for the configured
                default. Unknown names fall back to the literal default alias,
                then the configured default.

        Returns:
            tuple[int, int]: Text width and height in logical units.
        """

    def draw(
        self,
        x: int,
        y: int,
        text: str,
        color=(255, 255, 255),
        font_size: int | None = None,
        font_name: str | None = None,
    ):
        """Draw text at a logical position using the selected font, size, and color.

        Args:
            x (int): Horizontal position in logical coordinates.
            y (int): Vertical position in logical coordinates.
            text (str): Text to measure or render.
            color (Color): RGB or RGBA drawing color; omitted alpha is opaque.
            font_size (int | None): Logical font size, or None to use the
                selected font configuration.
            font_name (str | None): Font alias, or None for the configured
                default. Unknown names fall back to the literal default alias,
                then the configured default.

        Returns:
            None: This method does not return a value.
        """


class Texture(Protocol):
    """Create opaque handles for RGBA textures and draw them in logical coordinates."""

    def create(
        self,
        w: int,
        h: int,
        data: bytes | bytearray | memoryview,
        pitch: int = -1,
    ) -> int:
        """Upload RGBA pixels with optional padded row pitch and return an opaque handle.

        Args:
            w (int): Texture width in pixels when uploading, or logical width
                when drawing.
            h (int): Texture height in pixels when uploading, or logical height
                when drawing.
            data (bytes | bytearray | memoryview): C-contiguous RGBA pixel
                buffer, including row padding. Typed and multidimensional
                views are interpreted as a flat sequence of bytes.
            pitch (int): Bytes per input row. Nonpositive values select tightly
                packed RGBA rows; positive values must be at least four times
                the width.

        Returns:
            int: Opaque handle identifying the uploaded texture.

        Raises:
            ValueError: Dimensions are nonpositive, positive pitch is too
                small, or the pixel buffer is too short or not C-contiguous.
        """

    def draw(
        self,
        tex: int,
        x: int,
        y: int,
        w: int,
        h: int,
        angle_deg: float = 0.0,
    ):
        """Draw a texture at logical bounds, optionally rotated clockwise about its center.

        Args:
            tex (int): Opaque texture handle returned by create().
            x (int): Horizontal position in logical coordinates.
            y (int): Vertical position in logical coordinates.
            w (int): Texture width in pixels when uploading, or logical width
                when drawing.
            h (int): Texture height in pixels when uploading, or logical height
                when drawing.
            angle_deg (float): Clockwise rotation in degrees about the
                destination center.

        Returns:
            None: This method does not return a value.
        """

    def tiled(self, tex_id: int, x: int, y: int, w: int, h: int):
        """Stretch a texture to logical width and repeat it vertically within logical height.

        Args:
            tex_id (int): Opaque texture handle returned by create().
            x (int): Horizontal position in logical coordinates.
            y (int): Vertical position in logical coordinates.
            w (int): Texture width in pixels when uploading, or logical width
                when drawing.
            h (int): Texture height in pixels when uploading, or logical height
                when drawing.

        Returns:
            None: This method does not return a value.
        """

    def destroy(self, tex: int):
        """Release the surface associated with a texture handle.

        Args:
            tex (int): Opaque texture handle returned by create().

        Returns:
            None: This method does not return a value.
        """


class Clip(Protocol):
    """Replace or clear the active logical drawing clip."""

    def set(
        self,
        pos: Vec2,
        size: Size,
    ) -> None:
        """Replace the active clip with the viewport-mapped logical rectangle.

        Args:
            pos (Vec2): Top-left position in logical coordinates.
            size (Size): Width and height in logical units.

        Returns:
            None: This method does not return a value.
        """

    def clear(self) -> None:
        """Restore clipping to the entire target surface.

        Returns:
            None: This method does not return a value.
        """


class Renderer(Protocol):
    """Compose drawing capabilities and control frame clearing and presentation.

    Attributes:
        config (RendererConfig): Settings for this capability.
        viewport_transform (ViewportTransform): Mapping between logical
            coordinates and display pixels.
    """

    config: RendererConfig
    viewport_transform: ViewportTransform

    @property
    def shape(self) -> Shape:
        """Return the shape drawing capability.

        Returns:
            Shape: The requested capability.
        """

    @property
    def text(self) -> Text:
        """Return the text measurement and drawing capability.

        Returns:
            Text: The requested capability.
        """

    @property
    def texture(self) -> Texture:
        """Return the texture upload and drawing capability.

        Returns:
            Texture: The requested capability.
        """

    @property
    def clip(self) -> Clip:
        """Return the clip rectangle capability.

        Returns:
            Clip: The requested capability.
        """

    def set_clear_color(self, r: int, g: int, b: int):
        """Select the RGB color used when clearing subsequent frames.

        Args:
            r (int): Red channel in the range 0 through 255.
            g (int): Green channel in the range 0 through 255.
            b (int): Blue channel in the range 0 through 255.

        Returns:
            None: This method does not return a value.
        """

    def begin_frame(self):
        """Clear the target before drawing the next frame.

        Returns:
            None: This method does not return a value.
        """

    def end_frame(self):
        """Present the completed frame to the display.

        Returns:
            None: This method does not return a value.
        """
