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

from .window import PygameWindow


@dataclass(frozen=True)
class PygameRendererContext:
    window: PygameWindow
    viewport_transform: ViewportTransform


class PygameShape:
    def __init__(self, ctx: PygameRendererContext):
        self._context = ctx

    def _blit_alpha_shape(
        self,
        *,
        bounds: pygame.Rect,
        color: tuple[int, int, int, int],
        draw_fn,
    ) -> None:
        clipped = bounds.clip(self._context.window.screen.get_rect())
        if clipped.width <= 0 or clipped.height <= 0:
            return

        surface = pygame.Surface(
            (int(clipped.width), int(clipped.height)),
            pygame.SRCALPHA,
        )
        local_offset = (-int(clipped.x), -int(clipped.y))
        draw_fn(surface, local_offset, color)
        self._context.window.screen.blit(surface, clipped.topleft)

    def rect(
        self,
        pos: Vec2,
        size: Size,
        color=(255, 255, 255),
        *,
        radius: float = 0.0,
    ):
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

    def line(
        self,
        start: Vec2,
        end: Vec2,
        color=(255, 255, 255),
        thickness=5,
    ):
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

    def circle(self, x: int, y: int, radius: int, color=(255, 255, 255)):
        r, g, b, a = ColorFormatter.rgba(color)

        # Map center via viewport
        sx, sy = self._context.viewport_transform.map_xy(int(x), int(y))

        # Scale radius using map_wh on diameter (works with your current vp API)
        d = int(radius) * 2
        sw, sh = self._context.viewport_transform.map_wh(d, d)
        sr = max(1, int(min(sw, sh) // 2))

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

    def polygon(
        self,
        points: list[tuple[int, int]],
        color=(255, 255, 255),
        filled: bool = True,
    ):
        r, g, b, a = ColorFormatter.rgba(color)
        if len(points) < 3:
            return

        mapped_points = [
            self._context.viewport_transform.map_xy(int(x), int(y))
            for (x, y) in points
        ]

        width = 0 if filled else 1
        if a >= 255:
            pygame.draw.polygon(
                self._context.window.screen,
                (r, g, b),
                mapped_points,
                width=width,
            )
            return

        min_x = min(int(x) for x, _ in mapped_points)
        min_y = min(int(y) for _, y in mapped_points)
        max_x = max(int(x) for x, _ in mapped_points)
        max_y = max(int(y) for _, y in mapped_points)
        rect = pygame.Rect(
            min_x, min_y, max(1, max_x - min_x), max(1, max_y - min_y)
        )
        self._blit_alpha_shape(
            bounds=rect,
            color=(r, g, b, a),
            draw_fn=lambda surface, offset, rgba_color: pygame.draw.polygon(
                surface,
                rgba_color,
                [
                    (int(px) + offset[0], int(py) + offset[1])
                    for (px, py) in mapped_points
                ],
                width=width,
            ),
        )


class PygameText:
    def __init__(self, ctx: PygameRendererContext, config: TextConfig):
        self._context = ctx
        self._font_paths = {font.name: font.path for font in config.fonts}
        self._font_path = self._font_paths.get(config.default_font)
        self._fonts: dict[tuple[str | None, int], pygame.font.Font] = {}

    def _resolve_font_path(self, font_name: str | None) -> str | None:
        if font_name is None:
            return self._font_paths.get("default", self._font_path)
        if font_name in self._font_paths:
            return self._font_paths[font_name]
        return self._font_paths.get("default", self._font_path)

    def _font(
        self, font_size: int | None, font_name: str | None
    ) -> pygame.font.Font:
        size = int(font_size or 24)
        size = max(8, size)
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
        """
        Measure the width and height of the given text.
        """
        scaled_size = (
            None
            if font_size is None
            else max(
                8, int(round(font_size * self._context.viewport_transform.s))
            )
        )
        f = self._font(scaled_size, font_name)
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
        """
        Draw the given text at the specified position.
        """
        r, g, b, alpha = ColorFormatter.rgba(color)
        sx, sy = self._context.viewport_transform.map_xy(int(x), int(y))

        scaled_size = (
            None
            if font_size is None
            else max(
                8, int(round(font_size * self._context.viewport_transform.s))
            )
        )
        f = self._font(scaled_size, font_name)

        surf = f.render(text, True, (r, g, b))
        surf.set_alpha(alpha)
        self._context.window.screen.blit(surf, (sx, sy))


class PygameTexture:
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
        w = int(w)
        h = int(h)
        if pitch <= 0:
            pitch = w * 4

        mv = memoryview(data)
        needed = h * pitch
        if mv.nbytes < needed:
            raise ValueError(
                f"create_texture_rgba: buffer too small ({mv.nbytes}) for h*pitch ({needed})"
            )

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
        surf = self._textures[tex_id]  # adapt to your texture store
        # Scale the tile to target width, keep tile height
        tile_h = surf.get_height()
        tile = pygame.transform.scale(surf, (int(w), int(tile_h)))

        cur_y = int(y)
        end_y = int(y + h)

        while cur_y < end_y:
            remaining = end_y - cur_y
            if remaining >= tile_h:
                self._context.window.screen.blit(tile, (int(x), cur_y))
                cur_y += tile_h
            else:
                # partial tile at the end
                partial = tile.subsurface(
                    pygame.Rect(0, 0, int(w), int(remaining))
                )
                self._context.window.screen.blit(partial, (int(x), cur_y))
                break

    def destroy(self, tex: int):
        self._textures.pop(int(tex), None)


class PygameClip:
    def __init__(self, context: PygameRendererContext):
        self._context = context

    def set(
        self,
        pos: Vec2,
        size: Size,
    ) -> None:
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
        self._context.window.screen.set_clip(None)


class PygameRenderer(BackendComponent[PygameRendererConfig]):
    """
    Render port for the tatuy native backend.
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
        """
        Set the clear color for the renderer.
        """
        self._clear = (int(r), int(g), int(b), 255)
        print(self._clear)

    def begin_frame(self):
        """Begin a new rendering frame."""
        r, g, b, _ = self._clear
        # print(r, g, b)
        self._window.screen.fill((r, g, b))

    def end_frame(self):
        """End the current rendering frame."""
        pygame.display.flip()
