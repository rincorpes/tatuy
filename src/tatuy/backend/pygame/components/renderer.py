"""Render viewport-mapped shapes, text, and textures on Pygame surfaces."""

from __future__ import annotations

from dataclasses import dataclass

# Justification: Disabling no-member checks for pygame attributes since they are
# dynamically added after initialization.
# pylint: disable=no-member
import pygame

from tatuy.backend.backend_component import BackendComponent
from tatuy.backend.config import TextConfig
from tatuy.backend.pygame.config import PygameRendererConfig
from tatuy.geometry.size import Size
from tatuy.graphics.color import ColorFormatter
from tatuy.graphics.viewport.transform import ViewportTransform
from tatuy.math.vec2 import Vec2
from tatuy.tooling.profiler import profiler

from .window import PygameWindow

# pylint: disable=too-many-arguments,too-many-positional-arguments


@dataclass(frozen=True)
class PygameRendererContext:
    """Share the concrete display window and viewport transform across renderers.

    Args:
        window (PygameWindow): Concrete window providing the display surface.
        viewport_transform (ViewportTransform): Mapping between logical
            coordinates and display pixels.

    Attributes:
        window (PygameWindow): Concrete window providing the display surface.
        viewport_transform (ViewportTransform): Mapping between logical
            coordinates and display pixels.
    """

    window: PygameWindow
    viewport_transform: ViewportTransform


class PygameShape:
    """Rasterize opaque or alpha-blended geometry using logical coordinates.

    Args:
        ctx (PygameRendererContext): Shared display window and viewport
            mapping.
    """

    def __init__(self, ctx: PygameRendererContext):
        self._context = ctx

    def _blit_alpha_shape(
        self,
        *,
        bounds: pygame.Rect,
        color: tuple[int, int, int, int],
        draw_fn,
    ) -> None:
        """Blend a clipped temporary shape surface into the display.

        Args:
            bounds (pygame.Rect): Screen-space rectangle enclosing the shape,
                including its final pixels.
            color (tuple[int, int, int, int]): RGBA color with an explicit 8-bit alpha channel.
            draw_fn (Callable[..., object]):
                Callback receiving a temporary surface, local offset, and RGBA
                color.

        Returns:
            None: This method does not return a value.
        """
        clipped = bounds.clip(self._context.window.screen.get_rect())
        if clipped.width <= 0 or clipped.height <= 0:
            return

        surface = pygame.Surface(
            (int(clipped.width), int(clipped.height)),
            pygame.SRCALPHA,
        )
        local_offset = (-int(clipped.x), -int(clipped.y))
        # Match direct rasterization, including clipped diagonal outlines.
        surface.set_clip(
            self._context.window.screen.get_clip().move(*local_offset)
        )
        draw_fn(surface, local_offset, color)
        self._context.window.screen.blit(surface, clipped.topleft)

    # TODO: Fix too-many-locals
    def rect(  # pylint: disable=too-many-locals
        self,
        pos: Vec2,
        size: Size,
        color=(255, 255, 255),
        *,
        radius: float = 0.0,
    ):
        """Draw a viewport-mapped rectangle with scaled corner radius and optional alpha.

        Args:
            pos (Vec2): Top-left position in logical coordinates.
            size (Size): Width and height in logical units.
            color (Color): RGB or RGBA drawing color; omitted alpha is opaque.
            radius (float): Rounded-corner radius in logical units.

        Returns:
            None: This method does not return a value.

        Raises:
            ValueError: The color or alpha value is invalid.
            TypeError: The alpha value has an unsupported type.
        """
        x, y = pos.to_tuple()
        w, h = size.to_tuple()
        r, g, b, a = ColorFormatter.rgba(color)
        sx, sy = self._context.viewport_transform.map_xy(int(x), int(y))
        sw, sh = self._context.viewport_transform.map_wh(int(w), int(h))
        if a >= 255:
            pygame.draw.rect(
                self._context.window.screen,
                (r, g, b),
                pygame.Rect(sx, sy, sw, sh),
                border_radius=max(
                    0, int(radius * self._context.viewport_transform.s)
                ),
            )
            return

        rect = pygame.Rect(int(sx), int(sy), int(sw), int(sh))
        self._blit_alpha_shape(
            bounds=rect,
            color=(r, g, b, a),
            draw_fn=lambda surface, offset, rgba_color: pygame.draw.rect(
                surface,
                rgba_color,
                pygame.Rect(
                    rect.x + offset[0],
                    rect.y + offset[1],
                    rect.width,
                    rect.height,
                ),
                border_radius=max(
                    0, int(radius * self._context.viewport_transform.s)
                ),
            ),
        )

    # TODO: Fix too-many-locals
    def line(  # pylint: disable=too-many-locals
        self,
        start: Vec2,
        end: Vec2,
        color=(255, 255, 255),
        thickness=5,
    ):
        """Draw a viewport-mapped line with logical thickness and optional alpha.

        Negative thickness raises ValueError; zero or rounded-away thickness is a no-op.

        Args:
            start (Vec2): Starting point in logical coordinates.
            end (Vec2): Ending point in logical coordinates.
            color (Color): RGB or RGBA drawing color; omitted alpha is opaque.
            thickness (int): Nonnegative line width in logical units; zero
                draws nothing.

        Returns:
            None: This method does not return a value.

        Raises:
            ValueError: Thickness is negative. The color or alpha value is
                invalid.
            TypeError: The alpha value has an unsupported type.
        """
        if thickness < 0:
            raise ValueError("Line thickness cannot be negative")
        thickness = int(round(thickness * self._context.viewport_transform.s))
        if thickness <= 0:
            return
        x1, y1 = start.x, start.y
        x2, y2 = end.x, end.y
        r, g, b, a = ColorFormatter.rgba(color)
        sx1, sy1 = self._context.viewport_transform.map_xy(int(x1), int(y1))
        sx2, sy2 = self._context.viewport_transform.map_xy(int(x2), int(y2))
        if a >= 255:
            pygame.draw.line(
                self._context.window.screen,
                (r, g, b),
                (sx1, sy1),
                (sx2, sy2),
                int(thickness),
            )
            return

        pad = max(1, int(thickness))
        min_x = min(int(sx1), int(sx2)) - pad
        min_y = min(int(sy1), int(sy2)) - pad
        max_x = max(int(sx1), int(sx2)) + pad
        max_y = max(int(sy1), int(sy2)) + pad
        rect = pygame.Rect(
            min_x, min_y, max(1, max_x - min_x), max(1, max_y - min_y)
        )
        self._blit_alpha_shape(
            bounds=rect,
            color=(r, g, b, a),
            draw_fn=lambda surface, offset, rgba_color: pygame.draw.line(
                surface,
                rgba_color,
                (int(sx1) + offset[0], int(sy1) + offset[1]),
                (int(sx2) + offset[0], int(sy2) + offset[1]),
                int(thickness),
            ),
        )

    # TODO: Fix too-many-locals
    def circle(  # pylint: disable=too-many-locals
        self,
        x: int,
        y: int,
        radius: int,
        color=(255, 255, 255),
    ):
        """Draw a viewport-mapped circle, blending translucent colors when needed.

        Negative radius raises ValueError; zero or rounded-away radius is a no-op.

        Args:
            x (int): Horizontal position in logical coordinates.
            y (int): Vertical position in logical coordinates.
            radius (int): Nonnegative circle radius in logical units; zero
                draws nothing.
            color (Color): RGB or RGBA drawing color; omitted alpha is opaque.

        Returns:
            None: This method does not return a value.

        Raises:
            ValueError: Radius is negative. The color or alpha value is
                invalid.
            TypeError: The alpha value has an unsupported type.
        """
        if radius < 0:
            raise ValueError("Circle radius cannot be negative")
        if radius == 0:
            return
        r, g, b, a = ColorFormatter.rgba(color)

        # Map center via viewport
        sx, sy = self._context.viewport_transform.map_xy(int(x), int(y))

        # Scale radius using map_wh on diameter (works with your current vp API)
        d = int(radius) * 2
        sw, sh = self._context.viewport_transform.map_wh(d, d)
        sr = int(min(sw, sh) // 2)
        if sr <= 0:
            return

        if a >= 255:
            pygame.draw.circle(
                self._context.window.screen,
                (r, g, b),
                (int(sx), int(sy)),
                int(sr),
            )
            return

        rect = pygame.Rect(
            int(sx - sr),
            int(sy - sr),
            int(sr * 2),
            int(sr * 2),
        )
        self._blit_alpha_shape(
            bounds=rect,
            color=(r, g, b, a),
            draw_fn=lambda surface, offset, rgba_color: pygame.draw.circle(
                surface,
                rgba_color,
                (int(sx) + offset[0], int(sy) + offset[1]),
                int(sr),
            ),
        )

    def _map_polygon_points(
        self,
        points: list[tuple[int, int]],
    ) -> list[tuple[int, int]]:
        """Map logical polygon vertices to integer screen coordinates."""
        mapped: list[tuple[int, int]] = []
        for x, y in points:
            mapped_x, mapped_y = self._context.viewport_transform.map_xy(
                int(x), int(y)
            )
            mapped.append((int(mapped_x), int(mapped_y)))
        return mapped

    @staticmethod
    def _polygon_is_collapsed(points: list[tuple[int, int]]) -> bool:
        """Return whether all polygon vertices lie on one raster line."""
        if len(points) < 3:
            return True

        origin_x, origin_y = points[0]
        direction_x = points[1][0] - origin_x
        direction_y = points[1][1] - origin_y

        for point_x, point_y in points[2:]:
            offset_x = point_x - origin_x
            offset_y = point_y - origin_y
            if direction_x * offset_y != direction_y * offset_x:
                return False

        return True

    @staticmethod
    def _polygon_bounds(points: list[tuple[int, int]]) -> pygame.Rect:
        """Return inclusive raster bounds for mapped polygon vertices."""
        xs = [x for x, _ in points]
        ys = [y for _, y in points]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        return pygame.Rect(min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)

    @staticmethod
    def _draw_collapsed_polygon(
        surface: pygame.Surface,
        color: tuple[int, ...],
        points: list[tuple[int, int]],
    ) -> None:
        """Rasterize a zero-area polygon with inclusive extreme endpoints."""
        start = min(points)
        end = max(points)
        pygame.draw.line(surface, color, start, end, width=1)

    @classmethod
    def _draw_polygon_raster(
        cls,
        surface: pygame.Surface,
        color: tuple[int, ...],
        points: list[tuple[int, int]],
        *,
        width: int,
        collapsed: bool,
        offset: tuple[int, int] = (0, 0),
    ) -> None:
        """Rasterize mapped polygon points using Tatuy's stable semantics."""
        local_points = [(x + offset[0], y + offset[1]) for x, y in points]
        if collapsed:
            cls._draw_collapsed_polygon(surface, color, local_points)
            return
        pygame.draw.polygon(surface, color, local_points, width=width)

    def polygon(
        self,
        points: list[tuple[int, int]],
        color=(255, 255, 255),
        filled: bool = True,
    ):
        """Draw logical vertices as a filled polygon or one-pixel raster outline.

        Ignore fewer than three vertices. Alpha bounds include both maximum-edge
        pixels and preserve the target clip during local rasterization.

        Args:
            points (list[tuple[int, int]]): Polygon vertices in logical
                coordinates.
            color (Color): RGB or RGBA drawing color; omitted alpha is opaque.
            filled (bool): Whether to fill the polygon instead of drawing a
                one-pixel outline.

        Returns:
            None: This method does not return a value.

        Raises:
            ValueError: The color or alpha value is invalid.
            TypeError: The alpha value has an unsupported type.
        """
        r, g, b, a = ColorFormatter.rgba(color)
        if len(points) < 3:
            return

        mapped_points = self._map_polygon_points(points)
        collapsed = self._polygon_is_collapsed(mapped_points)

        width = 0 if filled else 1
        if a >= 255:
            self._draw_polygon_raster(
                self._context.window.screen,
                (r, g, b),
                mapped_points,
                width=width,
                collapsed=collapsed,
            )
            return

        # Polygon rasterization includes pixels at both extreme vertices.
        rect = self._polygon_bounds(mapped_points)
        self._blit_alpha_shape(
            bounds=rect,
            color=(r, g, b, a),
            draw_fn=lambda surface, offset, rgba_color: self._draw_polygon_raster(
                surface,
                rgba_color,
                mapped_points,
                width=width,
                collapsed=collapsed,
                offset=offset,
            ),
        )


class PygameText:
    """Resolve configured fonts and cache them by requested name and raster size.

    Args:
        ctx (PygameRendererContext): Shared display window and viewport
            mapping.
        config (TextConfig): Settings used to configure this capability.
    """

    def __init__(self, ctx: PygameRendererContext, config: TextConfig):
        self._context = ctx
        self._font_paths = {font.name: font.path for font in config.fonts}
        self._font_path = self._font_paths.get(config.default_font)
        self._default_font = config.default_font
        self._font_sizes = {font.name: font.size for font in config.fonts}
        self._fonts: dict[tuple[str | None, int], pygame.font.Font] = {}

    def _resolve_font_path(self, font_name: str | None) -> str | None:
        """Resolve a font alias using the configured default and fallback policy.

        Args:
            font_name (str | None): Font alias, or None for the configured
                default. Unknown names fall back to the literal default alias,
                then the configured default.

        Returns:
            str | None: Resolved font path, or None for the built-in font.
        """
        if font_name is None:
            return self._font_path
        if font_name in self._font_paths:
            return self._font_paths[font_name]
        return self._font_paths.get("default", self._font_path)

    def _font(
        self, font_size: int | None, font_name: str | None
    ) -> pygame.font.Font:
        """Get or create a cached font with viewport-scaled raster size.

        Args:
            font_size (int | None): Logical font size, or None to use the
                selected font configuration.
            font_name (str | None): Font alias, or None for the configured
                default. Unknown names fall back to the literal default alias,
                then the configured default.

        Returns:
            pygame.font.Font: Cached or newly constructed native font.

        Raises:
            pygame.error: A required native subsystem is unavailable or the
                platform operation fails.
            OSError: The selected font file cannot be opened.
        """
        selected = self._default_font if font_name is None else font_name
        if selected not in self._font_paths and font_name is not None:
            selected = (
                "default"
                if "default" in self._font_paths
                else self._default_font
            )
        logical_size = (
            self._font_sizes.get(selected, 24)
            if font_size is None
            else font_size
        )
        size = max(
            8, int(round(logical_size * self._context.viewport_transform.s))
        )
        cache_key = (font_name, size)
        cached = self._fonts.get(cache_key)
        if cached:
            return cached

        font_path = self._resolve_font_path(font_name)
        if font_path:
            f = pygame.font.Font(font_path, size)
        else:
            f = pygame.font.Font(None, size)  # default font

        self._fonts[cache_key] = f
        return f

    def measure(
        self,
        text: str,
        font_size: int | None = None,
        font_name: str | None = None,
    ) -> tuple[int, int]:
        """Return logical text dimensions using the same font resolution as drawing.

        Args:
            text (str): Text to measure or render.
            font_size (int | None): Logical font size, or None to use the
                selected font configuration.
            font_name (str | None): Font alias, or None for the configured
                default. Unknown names fall back to the literal default alias,
                then the configured default.

        Returns:
            tuple[int, int]: Text width and height in logical units.

        Raises:
            pygame.error: A required native subsystem is unavailable or the
                platform operation fails.
            OSError: The selected font file cannot be opened.
        """
        f = self._font(font_size, font_name)
        w_px, h_px = f.size(text)

        s = self._context.viewport_transform.s or 1.0
        return int(round(w_px / s)), int(round(h_px / s))

    def draw(
        self,
        x: int,
        y: int,
        text: str,
        color=(255, 255, 255),
        font_size: int | None = None,
        font_name: str | None = None,
    ):
        """Render antialiased text at a logical position and blend its requested alpha.

        Omitted names use the configured default. Omitted sizes use the selected
        font default; logical sizes scale once and clamp to at least eight raster pixels.

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

        Raises:
            ValueError: The color layout, channel value, or alpha value is invalid.
            TypeError: A color channel or alpha has an unsupported type,
                including a boolean alpha.
            pygame.error: A required native subsystem is unavailable or the
                platform operation fails.
            OSError: The selected font file cannot be opened.
        """
        r, g, b, alpha = ColorFormatter.rgba(color)
        sx, sy = self._context.viewport_transform.map_xy(int(x), int(y))

        f = self._font(font_size, font_name)

        surf = f.render(text, True, (r, g, b))
        surf.set_alpha(alpha)
        self._context.window.screen.blit(surf, (sx, sy))


class PygameTexture:
    """Own texture surfaces and expose integer handles for viewport-mapped drawing.

    Args:
        ctx (PygameRendererContext): Shared display window and viewport
            mapping.
    """

    def __init__(self, ctx: PygameRendererContext):
        self._context = ctx
        self._next_tex_id = 1
        self._textures: dict[int, pygame.Surface] = {}

    def create(
        self,
        w: int,
        h: int,
        data: bytes | bytearray | memoryview,
        pitch: int = -1,
    ) -> int:
        """Copy RGBA pixels into a native surface and return its texture handle.

        Nonpositive pitch means tightly packed rows. Invalid dimensions, undersized
        positive pitch, or short buffers raise ValueError before native conversion.
        Padded rows are repacked; conversion requires an initialized display.

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
            pygame.error: A required native subsystem is unavailable or the
                platform operation fails.
        """
        w = int(w)
        h = int(h)
        if w <= 0 or h <= 0:
            raise ValueError("Texture width and height must be positive")
        if 0 < pitch < w * 4:
            raise ValueError("Texture pitch must be at least width * 4")
        if pitch <= 0:
            pitch = w * 4

        mv = memoryview(data)
        if not mv.c_contiguous:
            raise ValueError("Texture pixel buffer must be C-contiguous")
        needed = h * pitch
        if mv.nbytes < needed:
            raise ValueError(
                f"create_texture_rgba: buffer too small ({mv.nbytes}) for h*pitch ({needed})"
            )

        # Pitch and slices count bytes, regardless of input element type/shape.
        mv = mv.cast("B")

        # Fast path: tightly packed RGBA rows
        if pitch == w * 4:
            # frombuffer shares memory; copy() to detach from Python buffer lifetime
            surf = pygame.image.frombuffer(
                mv[:needed], (w, h), "RGBA"
            ).convert_alpha()
        else:
            # Slow path: repack rows (supports padded pitch)
            packed = bytearray(w * h * 4)
            for row in range(h):
                src0 = row * pitch
                src1 = src0 + (w * 4)
                dst0 = row * (w * 4)
                dst1 = dst0 + (w * 4)
                packed[dst0:dst1] = mv[src0:src1]
            surf = pygame.image.frombuffer(
                bytes(packed), (w, h), "RGBA"
            ).convert_alpha()

        tex_id = self._next_tex_id
        self._next_tex_id += 1
        self._textures[tex_id] = surf
        return tex_id

    def draw(
        self,
        tex: int,
        x: int,
        y: int,
        w: int,
        h: int,
        angle_deg: float = 0.0,
    ):
        """Draw mapped texture bounds, optionally rotated clockwise about their center.

        Missing handles and nonpositive mapped dimensions are no-ops. Native
        scaling and rotation occur when required by the requested output.

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

        Raises:
            pygame.error: A required native subsystem is unavailable or the
                platform operation fails.
        """
        surf = self._textures.get(int(tex))
        if surf is None:
            return

        sx, sy = self._context.viewport_transform.map_xy(int(x), int(y))
        sw, sh = self._context.viewport_transform.map_wh(int(w), int(h))

        if sw <= 0 or sh <= 0:
            return

        draw_surf = surf
        if surf.get_width() != sw or surf.get_height() != sh:
            draw_surf = pygame.transform.scale(surf, (sw, sh))

        if abs(float(angle_deg)) > 0.001:
            rotated = pygame.transform.rotate(draw_surf, -float(angle_deg))
            rect = rotated.get_rect(
                center=(int(sx + (sw / 2)), int(sy + (sh / 2)))
            )
            self._context.window.screen.blit(rotated, rect.topleft)
            return

        self._context.window.screen.blit(draw_surf, (sx, sy))

    def tiled(self, tex_id: int, x: int, y: int, w: int, h: int):
        """Stretch to logical width and repeat vertically within logical height.

        Scale source tile height with the viewport, crop the final tile, and retain
        the active clip. Missing handles or mapped dimensions/tile height at zero
        or below are no-ops. Horizontal repetition is not performed.

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

        Raises:
            pygame.error: A required native subsystem is unavailable or the
                platform operation fails.
        """
        surf = self._textures.get(int(tex_id))
        if surf is None:
            return

        sx, sy = self._context.viewport_transform.map_xy(int(x), int(y))
        sw, sh = self._context.viewport_transform.map_wh(int(w), int(h))
        _, tile_h = self._context.viewport_transform.map_wh(
            0, surf.get_height()
        )
        if sw <= 0 or sh <= 0 or tile_h <= 0:
            return

        tile = pygame.transform.scale(surf, (sw, tile_h))
        for offset in range(0, sh, tile_h):
            self._context.window.screen.blit(
                tile,
                (sx, sy + offset),
                pygame.Rect(0, 0, sw, min(tile_h, sh - offset)),
            )

    def destroy(self, tex: int):
        """Remove a stored texture surface, ignoring unknown handles.

        Args:
            tex (int): Opaque texture handle returned by create().

        Returns:
            None: This method does not return a value.
        """
        self._textures.pop(int(tex), None)


class PygameClip:
    """Map logical clip rectangles onto the active Pygame display surface.

    Args:
        context (PygameRendererContext): Shared display window and viewport
            mapping.
    """

    def __init__(self, context: PygameRendererContext):
        self._context = context

    def set(
        self,
        pos: Vec2,
        size: Size,
    ) -> None:
        """Replace the surface clip with the viewport-mapped logical bounds.

        Args:
            pos (Vec2): Top-left position in logical coordinates.
            size (Size): Width and height in logical units.

        Returns:
            None: This method does not return a value.
        """
        x, y = pos.to_tuple()
        w, h = size.to_tuple()

        sx, sy = self._context.viewport_transform.map_xy(
            int(x),
            int(y),
        )
        sw, sh = self._context.viewport_transform.map_wh(
            int(w),
            int(h),
        )

        self._context.window.screen.set_clip(
            pygame.Rect(
                int(sx),
                int(sy),
                int(sw),
                int(sh),
            )
        )

    def clear(self) -> None:
        """Reset the surface clip to the full display bounds.

        Returns:
            None: This method does not return a value.
        """
        self._context.window.screen.set_clip(None)


class PygameRenderer(BackendComponent[PygameRendererConfig]):
    """Compose native drawing ports and present completed Pygame frames.

    Args:
        config (PygameRendererConfig): Settings used to configure this
            capability.
        window (PygameWindow): Concrete window providing the display
            surface.
        viewport_transform (ViewportTransform): Mapping from logical
            coordinates to display pixels.

    Raises:
        ValueError: The configured clear color or alpha value is invalid.
        TypeError: The configured alpha has an unsupported type.
    """

    def __init__(
        self,
        config: PygameRendererConfig,
        window: PygameWindow,
        viewport_transform: ViewportTransform,
    ):
        super().__init__(config)
        self._window = window
        self.viewport_transform = viewport_transform
        self._clear = ColorFormatter.rgba(config.background_color)

        context = PygameRendererContext(self._window, self.viewport_transform)

        self.shape = PygameShape(context)
        self.text = PygameText(context, self.config.text)
        self.texture = PygameTexture(context)
        self.clip = PygameClip(context)

    def set_clear_color(self, r: int, g: int, b: int):
        """Select an opaque RGB clear color without producing console output.

        Args:
            r (int): Red channel in the range 0 through 255.
            g (int): Green channel in the range 0 through 255.
            b (int): Blue channel in the range 0 through 255.

        Returns:
            None: This method does not return a value.
        """
        self._clear = (int(r), int(g), int(b), 255)

    def begin_frame(self):
        """Fill the display with the clear color, respecting the active surface clip.

        Returns:
            None: This method does not return a value.

        Raises:
            pygame.error: A required native subsystem is unavailable or the
                platform operation fails.
        """
        r, g, b, _ = self._clear
        self._window.screen.fill((r, g, b))

    def end_frame(self):
        """Present the completed display surface through pygame.display.flip.

        Returns:
            None: This method does not return a value.

        Raises:
            pygame.error: A required native subsystem is unavailable or the
                platform operation fails.
        """
        with profiler.span(
            "pygame.display.flip",
            "wait",
            metadata={"kind": "presentation"},
        ):
            pygame.display.flip()
