"""The backgrounds: sky, rolling hills and a checkered ground, with one theme per level of the
path (meadow, beach, forest, snow, space). Each is drawn once and cached.

Themes are pictures only, with no text, so they work in every language.
"""

import math
from dataclasses import dataclass
from functools import cache

import pygame

from edugames.core.content import DEFAULT_THEME
from edugames.ui import paint, style
from edugames.ui.paint import K, shade

Color = tuple[int, int, int]
GROUND_TOP = 640  # where the ground starts; figures stand on it


@dataclass(frozen=True)
class Theme:
    sky: tuple[Color, Color]
    hills: tuple[Color, Color, Color]
    ground: tuple[Color, Color]
    accent: Color  # its colour on the goal path
    decor: str


THEMES: dict[str, Theme] = {
    "meadow": Theme(
        ((70, 190, 240), (190, 236, 250)),
        ((120, 190, 110), (90, 170, 80), (70, 150, 70)),
        ((150, 210, 90), (126, 192, 74)),
        (110, 200, 80),
        "clouds",
    ),
    "beach": Theme(
        ((60, 180, 245), (205, 242, 255)),
        ((80, 185, 230), (55, 160, 215), (240, 214, 150)),
        ((248, 226, 165), (234, 208, 142)),
        (255, 190, 60),
        "sun",
    ),
    "forest": Theme(
        ((110, 200, 230), (210, 242, 225)),
        ((75, 155, 95), (55, 135, 75), (45, 115, 62)),
        ((112, 182, 82), (96, 166, 70)),
        (60, 160, 90),
        "trees",
    ),
    "snow": Theme(
        ((140, 195, 240), (232, 244, 255)),
        ((215, 230, 248), (198, 216, 242), (238, 245, 255)),
        ((244, 249, 255), (222, 234, 250)),
        (130, 190, 245),
        "snowflakes",
    ),
    "space": Theme(
        ((18, 20, 58), (75, 52, 140)),
        ((95, 72, 165), (78, 58, 145), (115, 92, 185)),
        ((140, 118, 200), (124, 102, 184)),
        (150, 100, 230),
        "planets",
    ),
}


def theme(name: str) -> Theme:
    """The theme called `name`, or the meadow if there is none (a content typo must not crash)."""
    return THEMES.get(name, THEMES[DEFAULT_THEME])


def P(v: float) -> int:
    return round(v * K)


@cache
def background(name: str) -> pygame.Surface:
    t = theme(name)
    w, h = style.SIZE
    big = pygame.Surface((P(w), P(h)))
    big.blit(paint.gradient((P(w), P(h)), *t.sky), (0, 0))
    if t.decor in ("clouds", "trees", "snowflakes"):
        _clouds(big, (255, 255, 255) if t.decor != "snowflakes" else (248, 252, 255))
    if t.decor == "sun":
        _sun(big)
    if t.decor == "planets":
        _space(big)
    for i, (y, amp) in enumerate(((470, 60), (530, 50), (590, 40))):
        color = t.hills[i]
        points = [
            (P(x), P(y + amp * math.sin(x / (170 + i * 40) + i * 2))) for x in range(0, w + 20, 20)
        ]
        pygame.draw.polygon(big, color, points + [(P(w), P(h)), (0, P(h))])
        pygame.draw.lines(big, shade(color, 1.12), False, points, P(6))
        if t.decor == "trees" and i == 1:
            _trees(big, points)
        if t.decor == "sun" and i < 2:
            _waves(big, y, amp, i)
    _ground(big, t.ground, craters=t.decor == "planets")
    sparkles = ((620, 330, 16), (90, 420, 12), (1220, 600, 14), (720, 560, 10))
    for x, y, r in sparkles:
        paint.sparkle(big, (P(x), P(y)), P(r))
    if t.decor == "snowflakes":
        for x, y in ((150, 120), (400, 260), (880, 90), (1100, 300), (300, 520), (980, 470)):
            _flake(big, x, y, 14)
    return paint.finish(big)


def _clouds(s: pygame.Surface, color: Color) -> None:
    for cx, cy, sc in ((180, 150, 1.0), (1050, 110, 1.3), (700, 200, 0.7)):
        for dx, dy, r in ((-50, 10, 40), (0, -12, 55), (55, 8, 42), (0, 22, 45)):
            pygame.draw.circle(s, color, (P(cx + dx * sc), P(cy + dy * sc)), P(r * sc))


def _sun(s: pygame.Surface) -> None:
    cx, cy = 1080, 150
    for i in range(12):
        a = i * math.pi / 6
        tip = (P(cx + 120 * math.cos(a)), P(cy + 120 * math.sin(a)))
        side1 = (P(cx + 80 * math.cos(a - 0.15)), P(cy + 80 * math.sin(a - 0.15)))
        side2 = (P(cx + 80 * math.cos(a + 0.15)), P(cy + 80 * math.sin(a + 0.15)))
        pygame.draw.polygon(s, (255, 220, 90), [tip, side1, side2])
    pygame.draw.circle(s, style.OUTLINE, (P(cx), P(cy)), P(74))
    pygame.draw.circle(s, (255, 205, 50), (P(cx), P(cy)), P(70))
    pygame.draw.circle(s, (255, 232, 130), (P(cx - 14), P(cy - 14)), P(50))
    _clouds_small(s)


def _clouds_small(s: pygame.Surface) -> None:
    for cx, cy in ((250, 140), (650, 210)):
        for dx, dy, r in ((-36, 6, 28), (0, -8, 38), (38, 6, 30)):
            pygame.draw.circle(s, (255, 255, 255), (P(cx + dx), P(cy + dy)), P(r))


def _waves(s: pygame.Surface, y: float, amp: float, layer: int) -> None:
    for x in range(40 + layer * 60, style.WIDTH, 160):
        top = y + amp * math.sin(x / (170 + layer * 40) + layer * 2) + 30
        rect = pygame.Rect(P(x), P(top), P(46), P(22))
        pygame.draw.arc(s, (235, 248, 255), rect, 0.3, math.pi - 0.3, P(4))


def _trees(s: pygame.Surface, ridge: list[tuple[int, int]]) -> None:
    for index in (3, 12, 22, 34, 47, 58):
        x, y = ridge[min(index, len(ridge) - 1)]
        trunk = pygame.Rect(0, 0, P(16), P(40))
        trunk.midbottom = (x, y + P(14))
        pygame.draw.rect(s, style.OUTLINE, trunk.inflate(P(5), P(5)), border_radius=P(4))
        pygame.draw.rect(s, (140, 90, 50), trunk, border_radius=P(4))
        crown = (x, y - P(40))
        pygame.draw.circle(s, style.OUTLINE, crown, P(39))
        pygame.draw.circle(s, (55, 150, 70), crown, P(36))
        pygame.draw.circle(s, (85, 180, 90), (x - P(9), y - P(48)), P(24))


def _flake(s: pygame.Surface, x: float, y: float, r: float) -> None:
    for i in range(3):
        a = i * math.pi / 3
        dx, dy = r * math.cos(a), r * math.sin(a)
        pygame.draw.line(s, (255, 255, 255), (P(x - dx), P(y - dy)), (P(x + dx), P(y + dy)), P(4))
    pygame.draw.circle(s, (255, 255, 255), (P(x), P(y)), P(4))


def _space(s: pygame.Surface) -> None:
    for i in range(70):
        x = (i * 397) % style.WIDTH
        y = (i * 211) % 470
        pygame.draw.circle(s, (255, 255, 230), (P(x), P(y)), P(1 + i % 3))
    _ringed_planet(s, (P(1040), P(170)), P(70), (P(260), P(70)), P(8), P(4))
    moon = (P(220), P(150))
    pygame.draw.circle(s, style.OUTLINE, moon, P(46))
    pygame.draw.circle(s, (230, 232, 245), moon, P(42))
    pygame.draw.circle(s, (200, 204, 225), (moon[0] + P(12), moon[1] + P(8)), P(10))


def _ringed_planet(
    s: pygame.Surface, center: tuple[int, int], radius: float, ring_size, width: int, line: int
) -> None:
    """A planet whose ring passes behind it at the top and in front of it at the bottom."""
    ring = pygame.Rect(0, 0, *ring_size)
    ring.center = center

    def draw_ring() -> None:
        pygame.draw.ellipse(s, style.OUTLINE, ring.inflate(line * 2, line * 2), width + line * 2)
        pygame.draw.ellipse(s, (255, 220, 120), ring, width)

    draw_ring()  # all of it, then the planet hides the back half
    pygame.draw.circle(s, style.OUTLINE, center, radius + line)
    pygame.draw.circle(s, (250, 150, 90), center, radius)
    pygame.draw.circle(
        s, (255, 190, 130), (center[0] - radius * 0.26, center[1] - radius * 0.26), radius * 0.6
    )
    old = s.get_clip()
    s.set_clip(pygame.Rect(0, center[1], s.get_width(), s.get_height()))
    draw_ring()  # the front half, over the planet
    s.set_clip(old)


def _ground(s: pygame.Surface, colors: tuple[Color, Color], craters: bool) -> None:
    w = style.WIDTH
    rows = [GROUND_TOP, 668, 702, 744, 800]
    n = 18

    def x_at(col: float, y: float) -> float:
        return w / 2 + (col - n / 2) * (w / n) * (1 + (y - 600) / 90)

    for r in range(len(rows) - 1):
        y0, y1 = rows[r], rows[r + 1]
        for c in range(-6, n + 6):
            quad = [
                (P(x_at(c, y0)), P(y0)),
                (P(x_at(c + 1, y0)), P(y0)),
                (P(x_at(c + 1, y1)), P(y1)),
                (P(x_at(c, y1)), P(y1)),
            ]
            pygame.draw.polygon(s, colors[(r + c) % 2], quad)
    if craters:
        for x, y, rw in ((180, 700, 70), (640, 760, 90), (1090, 690, 60)):
            rect = pygame.Rect(0, 0, P(rw), P(rw * 0.35))
            rect.center = (P(x), P(y))
            pygame.draw.ellipse(s, shade(colors[0], 0.8), rect)


@cache
def icon(name: str, size: int) -> pygame.Surface:
    """A small picture of a theme, for its level on the goal path."""
    t = theme(name)
    big = pygame.Surface((P(size), P(size)), pygame.SRCALPHA)
    c = P(size) // 2
    r = P(size) * 0.36
    line = max(2, P(size) // 18)
    if t.decor == "sun":
        for i in range(8):
            a = i * math.pi / 4
            end = (c + r * 1.35 * math.cos(a), c + r * 1.35 * math.sin(a))
            pygame.draw.line(big, style.OUTLINE, (c, c), end, line * 2)
        pygame.draw.circle(big, style.OUTLINE, (c, c), r + line)
        pygame.draw.circle(big, (255, 205, 50), (c, c), r)
    elif t.decor == "trees":
        trunk = pygame.Rect(0, 0, r * 0.5, r * 1.1)
        trunk.midbottom = (c, c + r * 1.3)
        pygame.draw.rect(big, style.OUTLINE, trunk.inflate(line * 2, line * 2))
        pygame.draw.rect(big, (140, 90, 50), trunk)
        pygame.draw.circle(big, style.OUTLINE, (c, c - r * 0.25), r + line)
        pygame.draw.circle(big, (70, 170, 80), (c, c - r * 0.25), r)
    elif t.decor == "snowflakes":
        for i in range(3):
            a = i * math.pi / 3
            dx, dy = r * 1.2 * math.cos(a), r * 1.2 * math.sin(a)
            pygame.draw.line(big, style.OUTLINE, (c - dx, c - dy), (c + dx, c + dy), line * 3)
            pygame.draw.line(big, style.WHITE, (c - dx, c - dy), (c + dx, c + dy), line)
    elif t.decor == "planets":
        _ringed_planet(big, (c, c), r, (r * 2.8, r * 0.9), line * 2, line)
    else:  # a flower
        for i in range(5):
            a = -math.pi / 2 + i * 2 * math.pi / 5
            petal = (c + r * 0.7 * math.cos(a), c + r * 0.7 * math.sin(a))
            pygame.draw.circle(big, style.OUTLINE, petal, r * 0.55 + line)
            pygame.draw.circle(big, (255, 140, 170), petal, r * 0.55)
        pygame.draw.circle(big, style.OUTLINE, (c, c), r * 0.45 + line)
        pygame.draw.circle(big, style.GOLD, (c, c), r * 0.45)
    return paint.finish(big)
