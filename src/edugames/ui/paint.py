"""Drawing helpers for the art style: shapes drawn at twice the size and scaled down (smooth
edges), with a navy outline, a cel shade or a gloss. Every sprite is cached, so a frame only blits.
"""

import math
from functools import lru_cache

import pygame

from edugames.ui import style

K = 2  # supersampling factor
Color = tuple[int, ...]
Point = tuple[float, float]


def shade(color: Color, factor: float) -> tuple[int, int, int]:
    return tuple(max(0, min(255, round(v * factor))) for v in color[:3])  # type: ignore[return-value]


def mix(a: Color, b: Color, t: float) -> tuple[int, int, int]:
    return tuple(round(x + (y - x) * t) for x, y in zip(a[:3], b[:3], strict=True))  # type: ignore[return-value]


def gradient(size: tuple[int, int], top: Color, bottom: Color) -> pygame.Surface:
    w, h = size
    strip = pygame.Surface((1, max(1, h)), pygame.SRCALPHA)
    for y in range(h):
        strip.set_at((0, y), mix(top, bottom, y / max(1, h - 1)))
    return pygame.transform.scale(strip, (max(1, w), max(1, h)))


def gradient_fill(
    surface: pygame.Surface, rect: pygame.Rect, shape, top: Color, bottom: Color
) -> None:
    """Fill the shape that `shape(layer, color)` draws on a rect-sized layer with a gradient."""
    layer = pygame.Surface(rect.size, pygame.SRCALPHA)
    shape(layer, (255, 255, 255, 255))
    layer.blit(gradient(rect.size, top, bottom), (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surface.blit(layer, rect.topleft)


def finish(big: pygame.Surface) -> pygame.Surface:
    """Scale a supersampled drawing down to its real size."""
    w, h = big.get_size()
    return pygame.transform.smoothscale(big, (max(1, w // K), max(1, h // K)))


def star_points(center: Point, radius: float, inner: float = 0.47) -> list[Point]:
    cx, cy = center
    points = []
    for i in range(10):
        r = radius if i % 2 == 0 else radius * inner
        angle = -math.pi / 2 + i * math.pi / 5
        points.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    return points


# --- Boxes and buttons --------------------------------------------------------------------------

LIP = 8  # the darker edge under a button, so it looks pressable
RING = 7  # the gold ring around a selected button
BAND = 44  # the most height of the cel shade on a box
PAD = RING + 2  # room around a box sprite for the ring and the lip


@lru_cache(maxsize=512)
def box(
    size: tuple[int, int],
    color: Color,
    radius: int,
    *,
    gloss: bool = False,
    lip: bool = True,
    ring: Color | None = None,
) -> pygame.Surface:
    """A rounded box: navy outline, a cel shade on its lower part (or a gloss), a darker lip
    below and an optional ring. The sprite is `PAD` larger than `size` on every side."""
    w, h = size
    big = pygame.Surface(((w + 2 * PAD) * K, (h + 2 * PAD) * K), pygame.SRCALPHA)
    r = pygame.Rect(PAD * K, PAD * K, w * K, h * K)
    rad = radius * K
    line = 3 * K
    if ring:
        pygame.draw.rect(
            big, ring, r.inflate(RING * 2 * K, RING * 2 * K), border_radius=rad + RING * K
        )
    if lip:
        under = r.move(0, LIP * K)
        pygame.draw.rect(big, style.OUTLINE, under.inflate(line, line), border_radius=rad)
        pygame.draw.rect(big, shade(color, 0.7), under, border_radius=rad)
    pygame.draw.rect(big, style.OUTLINE, r.inflate(line, line), border_radius=rad + line // 2)
    if gloss:
        gradient_fill(
            big,
            r,
            lambda layer, c: pygame.draw.rect(layer, c, layer.get_rect(), border_radius=rad),
            shade(color, 1.18),
            shade(color, 0.9),
        )
        shine = pygame.Rect(r.x + rad // 2 + 6 * K, r.y + 6 * K, r.w - rad - 12 * K, r.h * 0.3)
        if shine.w > 0:
            pygame.draw.rect(big, mix(color, style.WHITE, 0.45), shine, border_radius=shine.h // 2)
    else:
        pygame.draw.rect(big, color, r, border_radius=rad)
        band_h = min(r.h * 0.38, BAND * K)  # the cel shade: a strip along the bottom
        band = pygame.Rect(r.x, r.bottom - band_h, r.w, band_h)
        old = big.get_clip()
        big.set_clip(band)
        pygame.draw.rect(big, shade(color, 0.92), r, border_radius=rad)
        big.set_clip(old)
    return finish(big)


def draw_box(
    surface: pygame.Surface, rect: pygame.Rect, color: Color, radius: int, **options
) -> None:
    surface.blit(box(rect.size, tuple(color), radius, **options), (rect.x - PAD, rect.y - PAD))


# --- Text ---------------------------------------------------------------------------------------


@lru_cache(maxsize=512)
def title_text(
    text: str, size: int, color: Color, outline: Color | None, depth: int
) -> pygame.Surface:
    """Fredoka text with an outline and a drop shadow, like the titles of the art style."""
    font = style.title_font(size)
    image = font.render(text, True, color)
    w, h = image.get_size()
    edge = max(2, size // 16) if outline else 0
    sprite = pygame.Surface((w + 2 * edge, h + 2 * edge + depth), pygame.SRCALPHA)
    if outline:
        dark = font.render(text, True, outline)
        for i in range(16):
            angle = i * math.pi / 8
            offset = (edge + edge * math.cos(angle), edge + edge * math.sin(angle) + depth)
            sprite.blit(dark, offset)
            sprite.blit(dark, (offset[0], offset[1] - depth))
    sprite.blit(image, (edge, edge))
    return sprite


def draw_title_text(
    surface: pygame.Surface,
    text: str,
    size: int,
    center: tuple[int, int],
    color: Color = style.WHITE,
    outline: Color | None = style.OUTLINE,
    depth: int = 4,
) -> pygame.Rect:
    sprite = title_text(text, size, tuple(color), outline, depth)
    rect = sprite.get_rect(center=center)
    surface.blit(sprite, rect)
    return rect


# --- Rewards (glossy) ---------------------------------------------------------------------------


@lru_cache(maxsize=64)
def star(size: int, filled: bool) -> pygame.Surface:
    """A star `size` pixels wide: glossy gold, or an empty slot when not earned."""
    s = size * K
    big = pygame.Surface((s, s + 6 * K), pygame.SRCALPHA)
    center = (s / 2, s / 2 + 2 * K)
    outer = star_points(center, s / 2 - 3 * K)
    if filled:
        pygame.draw.polygon(big, (225, 145, 0), [(x, y + 5 * K) for x, y in outer])
        pygame.draw.polygon(big, style.GOLD, outer)
        top_half = outer[8:] + outer[:3] + [center]
        pygame.draw.polygon(big, (255, 232, 120), top_half)
        hx, hy = center[0] - s * 0.12, center[1] - s * 0.18
        pygame.draw.ellipse(big, style.WHITE, (hx - s * 0.05, hy - s * 0.03, s * 0.1, s * 0.07))
    else:
        pygame.draw.polygon(big, (255, 255, 255, 150), outer)
    pygame.draw.polygon(big, style.OUTLINE, outer, max(2, round(s * 0.04)))
    return finish(big)


@lru_cache(maxsize=64)
def coin(radius: int) -> pygame.Surface:
    """A glossy gold coin with a rim."""
    r = radius * K
    big = pygame.Surface((2 * r + 4 * K, 2 * r + 4 * K), pygame.SRCALPHA)
    c = (big.get_width() // 2, big.get_height() // 2)
    pygame.draw.circle(big, style.OUTLINE, c, r + 2 * K)
    rect = pygame.Rect(0, 0, 2 * r, 2 * r)
    rect.center = c
    gradient_fill(
        big,
        rect,
        lambda layer, col: pygame.draw.circle(layer, col, (r, r), r),
        (255, 225, 90),
        (232, 150, 20),
    )
    pygame.draw.circle(big, (215, 135, 10), c, r * 0.68, max(2, r // 9))
    pygame.draw.ellipse(big, (255, 245, 190), (c[0] - r * 0.55, c[1] - r * 0.7, r * 0.5, r * 0.32))
    return finish(big)


def sparkle(
    surface: pygame.Surface, center: Point, radius: float, color: Color = style.WHITE
) -> None:
    x, y = center
    points = []
    for i in range(8):
        r = radius if i % 2 == 0 else radius * 0.25
        angle = i * math.pi / 4
        points.append((x + r * math.cos(angle), y + r * math.sin(angle)))
    pygame.draw.polygon(surface, color, points)
