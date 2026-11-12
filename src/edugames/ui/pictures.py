"""The picture library: language-neutral concepts (`cat`, `moon`) drawn with shapes in the art
style, a navy outline and one cel shade, with no text, so every language can use them. Each locale
says which pictures it uses and their words (`content/<locale>/pictures.json`).

Pictures are drawn in units on a 100 × 100 square centred on (0, 0), once per size, and cached.
"""

import math
from collections.abc import Callable
from functools import lru_cache

import pygame

from edugames.ui import paint, style
from edugames.ui.paint import K, mix, shade

OUTLINE_W = 3  # in picture units
CLEAR = (0, 0, 0, 0)  # paints a hole in a transparent sprite

RED = (230, 60, 60)
ORANGE = (250, 150, 50)
YELLOW = (255, 210, 60)
GREEN = (90, 180, 80)
LEAF = (70, 165, 80)
BLUE = (70, 140, 230)
PURPLE = (150, 90, 200)
PINK = (245, 160, 180)
BROWN = (150, 100, 60)
CREAM = (252, 246, 228)
GREY = (200, 205, 220)


class _Pic(paint.Pen):
    def shaded_circle(self, color, center, r: float) -> None:
        """A circle with its cel shade as a crescent at the bottom right, like the avatar's
        head."""
        self.circle(shade(color, 0.84), center, r)
        x, y = center
        self.circle(color, (x - r * 0.08, y - r * 0.08), r * 0.86, outline=False)

    def shaded_polygon(self, color, points, band: float = 0.3) -> None:
        """A polygon with its cel shade as a strip along the bottom (like the boxes)."""
        pts = [self.p(*q) for q in points]
        pygame.draw.polygon(self.s, color, pts)
        top = min(y for _, y in pts)
        bottom = max(y for _, y in pts)
        old = self.s.get_clip()
        cut = round(bottom - (bottom - top) * band)
        self.s.set_clip(pygame.Rect(0, cut, self.s.get_width(), self.s.get_height() - cut))
        pygame.draw.polygon(self.s, shade(color, 0.86), pts)
        self.s.set_clip(old)
        pygame.draw.polygon(self.s, style.OUTLINE, pts, self.lw)

    def shaded_ellipse(self, color, box, band: float = 0.3) -> None:
        x, y, w, h = box
        self.ellipse(color, box)
        old = self.s.get_clip()
        self.s.set_clip(self.rect(x, y + h * (1 - band), w, h * band + 1))
        pygame.draw.ellipse(self.s, shade(color, 0.86), self.rect(*box))
        self.s.set_clip(old)

    def shine(self, center, w: float, h: float) -> None:
        x, y = center
        pygame.draw.ellipse(self.s, style.WHITE, self.rect(x - w / 2, y - h / 2, w, h))

    def hole(self, center, r: float) -> None:
        """A see-through hole with an outline (the ring of a key)."""
        pygame.draw.circle(self.s, style.OUTLINE, self.p(*center), r * self.u + self.lw)
        pygame.draw.circle(self.s, CLEAR, self.p(*center), r * self.u)

    def line(self, color, a, b, width: float) -> None:
        pygame.draw.line(self.s, color, self.p(*a), self.p(*b), max(1, round(width * self.u)))

    def eyes(self, y: float, gap: float, r: float = 4.5) -> None:
        for d in (-1, 1):
            pygame.draw.circle(self.s, style.OUTLINE, self.p(d * gap, y), r * self.u)
            pygame.draw.circle(
                self.s, style.WHITE, self.p(d * gap - r * 0.3, y - r * 0.35), r * 0.35 * self.u
            )

    def smile(self, y: float, w: float) -> None:
        box = self.rect(-w / 2, y - w / 3, w, w / 1.5)
        pygame.draw.arc(self.s, style.OUTLINE, box, math.pi + 0.5, 2 * math.pi - 0.5, self.lw)


def _arc_points(cx: float, cy: float, r: float, start: float, end: float, n: int = 24):
    return [
        (
            cx + r * math.cos(start + (end - start) * i / n),
            cy + r * math.sin(start + (end - start) * i / n),
        )
        for i in range(n + 1)
    ]


# --- The pictures -----------------------------------------------------------------------------


def _apple(d: _Pic) -> None:
    d.limb(BROWN, (0, -22), (5, -40), 6)
    d.shaded_polygon(LEAF, [(4, -34), (18, -46), (34, -42), (22, -30)])
    d.blobs(RED, [(-14, 6, 28), (14, 6, 28), (0, 18, 24)])
    old = d.s.get_clip()
    d.s.set_clip(d.rect(-50, 20, 100, 30))
    d.circle(shade(RED, 0.84), (-14, 6), 28, outline=False)
    d.circle(shade(RED, 0.84), (14, 6), 28, outline=False)
    d.circle(shade(RED, 0.84), (0, 18), 24, outline=False)
    d.s.set_clip(old)
    d.shine((-18, -6), 10, 14)


def _ball(d: _Pic) -> None:
    """A beach ball: coloured panels around a white cap."""
    d.circle(style.WHITE, (0, 2), 40)
    for i, color in enumerate((RED, style.WHITE, BLUE, style.WHITE, YELLOW, style.WHITE)):
        start = i * math.pi / 3 - math.pi / 2
        d.polygon(
            color, [(0, 2), *_arc_points(0, 2, 40, start, start + math.pi / 3, 8)], outline=False
        )
    pygame.draw.circle(d.s, style.OUTLINE, d.p(0, 2), 40 * d.u + d.lw, d.lw)
    d.circle(style.WHITE, (0, 2), 9)
    d.shine((-20, -16), 10, 8)


def _ears(d: _Pic, color, inner) -> None:
    for s in (-1, 1):
        d.polygon(color, [(s * 32, -2), (s * 30, -44), (s * 8, -24)])
        d.polygon(inner, [(s * 27, -10), (s * 26, -34), (s * 14, -22)], outline=False)


def _cat(d: _Pic) -> None:
    _ears(d, ORANGE, PINK)
    d.shaded_circle(ORANGE, (0, 6), 34)
    for s in (-1, 1):
        d.line(shade(ORANGE, 0.8), (s * 10, -24), (s * 6, -14), 3)
    d.eyes(0, 13, 5)
    d.polygon(PINK, [(-5, 10), (5, 10), (0, 16)])
    for s in (-1, 1):
        d.line(style.OUTLINE, (s * 12, 16), (s * 44, 10), 1.6)
        d.line(style.OUTLINE, (s * 12, 20), (s * 44, 24), 1.6)
    d.smile(20, 14)


def _dog(d: _Pic) -> None:
    tan = (200, 145, 90)
    d.shaded_circle(tan, (0, 4), 34)
    for s in (-1, 1):
        d.shaded_ellipse(shade(BROWN, 0.9), (s * 34 - 11, -30, 22, 48))
    d.ellipse(CREAM, (-18, 6, 36, 26))
    d.ellipse(style.OUTLINE, (-7, 6, 14, 9), outline=False)
    d.eyes(-8, 13, 5)
    d.ellipse(PINK, (-6, 26, 12, 14))
    d.line(style.OUTLINE, (0, 15), (0, 24), 2)


def _egg(d: _Pic) -> None:
    d.shaded_ellipse(CREAM, (-27, -40, 54, 78), band=0.28)
    d.shine((-10, -18), 9, 16)


def _fish(d: _Pic) -> None:
    d.shaded_polygon(shade(ORANGE, 0.95), [(18, 0), (46, -22), (40, 0), (46, 22)])
    d.shaded_polygon(ORANGE, [(-4, -20), (8, -32), (14, -14)])
    d.shaded_ellipse(ORANGE, (-42, -22, 68, 44))
    d.line(shade(ORANGE, 0.8), (4, -14), (4, 14), 3)
    pygame.draw.circle(d.s, style.OUTLINE, d.p(-22, -5), 5 * d.u)
    pygame.draw.circle(d.s, style.WHITE, d.p(-23.5, -6.8), 1.8 * d.u)
    for x, y, r in ((-40, -34, 4), (-32, -44, 3)):
        pygame.draw.circle(d.s, style.OUTLINE, d.p(x, y), r * d.u, max(1, d.lw // 2))


def _grapes(d: _Pic) -> None:
    d.limb(BROWN, (0, -28), (4, -44), 5)
    d.shaded_polygon(LEAF, [(4, -38), (20, -48), (34, -38), (18, -30)])
    for x, y in ((-18, -20), (0, -20), (18, -20), (-9, -2), (9, -2), (-18, 16), (18, 16), (0, 16),
                 (-9, 32), (9, 32)):  # fmt: skip
        d.shaded_circle(PURPLE, (x, y), 11)


def _hat(d: _Pic) -> None:
    straw = (235, 195, 105)
    d.shaded_ellipse(straw, (-46, 4, 92, 26))
    d.shaded_polygon(straw, [(-26, 14), (-22, -26), (-10, -32), (10, -32), (22, -26), (26, 14)])
    d.polygon(RED, [(-25, 0), (25, 0), (26, 12), (-26, 12)])


def _igloo(d: _Pic) -> None:
    ice = (235, 245, 255)
    d.shaded_polygon(ice, [(-44, 30), *_arc_points(0, 30, 44, math.pi, 2 * math.pi), (44, 30)])
    for y in (14, -2, -16):  # the rows of ice blocks
        half = math.sqrt(max(0, 44**2 - (30 - y) ** 2))
        d.line((170, 195, 225), (-half + 3, y), (half - 3, y), 2)
    d.polygon((120, 150, 200), [(-14, 30), *_arc_points(0, 30, 14, math.pi, 2 * math.pi), (14, 30)])


def _jam(d: _Pic) -> None:
    glass = (215, 235, 245)
    d.rrect(glass, (-26, -18, 52, 60), 12)
    d.rrect(shade(RED, 0.85), (-22, -8, 44, 46), 9, outline=False)
    d.rrect(RED, (-26, -32, 52, 16), 6)
    d.rrect(CREAM, (-16, 4, 32, 22), 5)
    d.circle(RED, (0, 16), 7)
    d.polygon(LEAF, [(-5, 8), (5, 8), (0, 12)], outline=False)
    d.shine((-18, 0), 5, 14)


def _key(d: _Pic) -> None:
    gold = (245, 190, 50)
    d.rrect(gold, (-10, -6, 52, 12), 4)
    d.rrect(gold, (28, 4, 7, 14), 2)
    d.rrect(gold, (38, 4, 6, 10), 2)
    d.shaded_circle(gold, (-24, 0), 22)
    d.hole((-26, 0), 8)


def _leaf(d: _Pic) -> None:
    d.limb(BROWN, (-34, 34), (-18, 18), 5)
    top = _arc_points(0, 26, 52, -math.pi * 0.72, -math.pi * 0.28)
    outline = [(x - y * 0.55, y - x * 0.25 - 6) for x, y in top]
    bottom = [(-x, -y - 12) for x, y in outline]
    d.shaded_polygon(LEAF, outline + bottom)
    d.line(shade(LEAF, 0.7), (-20, 16), (24, -30), 3)


def _moon(d: _Pic) -> None:
    outer, inner = (0, 0, 38), (16, -10, 32)

    def inside(x, y, circle) -> bool:
        cx, cy, r = circle
        return (x - cx) ** 2 + (y - cy) ** 2 < r**2

    away = math.atan2(inner[1], inner[0]) + math.pi
    rim = [
        p
        for p in _arc_points(0, 0, 38, away - math.pi, away + math.pi, 90)
        if not inside(*p, inner)
    ]
    cut = _arc_points(inner[0], inner[1], inner[2], away + math.pi, away - math.pi, 90)
    cut = [p for p in cut if inside(*p, outer)]
    d.shaded_polygon(YELLOW, rim + cut)


def _octopus(d: _Pic) -> None:
    color = (235, 110, 160)
    for x in (-32, -16, 0, 16, 32):
        d.limb(color, (x * 1.25, 42 - abs(x) * 0.25), (x * 0.7, 0), 10)
    d.shaded_ellipse(color, (-30, -44, 60, 54))
    d.eyes(-20, 11, 5)
    d.smile(-8, 12)


def _pig(d: _Pic) -> None:
    for s in (-1, 1):
        d.polygon(PINK, [(s * 30, -14), (s * 32, -42), (s * 12, -30)])
    d.shaded_circle(PINK, (0, 4), 36)
    d.ellipse(shade(PINK, 0.88), (-15, 6, 30, 20))
    for s in (-1, 1):
        d.ellipse(shade(PINK, 0.6), (s * 6 - 3, 12, 6, 9), outline=False)
        pygame.draw.ellipse(d.s, (250, 130, 140), d.rect(s * 24 - 6, 6, 12, 7))
    d.eyes(-10, 13, 4.5)


def _rainbow(d: _Pic) -> None:
    colors = (RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE)
    r, band = 46, 5.5
    d.polygon(style.OUTLINE, _arc_points(0, 22, r + OUTLINE_W, math.pi, 2 * math.pi), outline=False)
    for i, color in enumerate(colors):
        d.polygon(color, _arc_points(0, 22, r - i * band, math.pi, 2 * math.pi), outline=False)
    d.polygon(style.OUTLINE, _arc_points(0, 22, r - 6 * band, math.pi, 2 * math.pi), outline=False)
    inner = _arc_points(0, 22, r - 6 * band - OUTLINE_W, math.pi, 2 * math.pi)
    pygame.draw.polygon(d.s, CLEAR, [d.p(*q) for q in inner])
    for s in (-1, 1):
        d.blobs(style.WHITE, [(s * 36, 26, 10), (s * 26, 28, 9), (s * 44, 28, 8), (s * 34, 18, 9)])


def _sun(d: _Pic) -> None:
    for i in range(10):
        a = i * math.pi / 5
        tip = (44 * math.cos(a), 44 * math.sin(a))
        sides = [(30 * math.cos(a + s * 0.22), 30 * math.sin(a + s * 0.22)) for s in (-1, 1)]
        d.polygon(ORANGE, [tip, *sides])
    d.shaded_circle(YELLOW, (0, 0), 28)
    d.eyes(-5, 9, 3.5)
    d.smile(8, 14)


def _tree(d: _Pic) -> None:
    d.rrect(BROWN, (-8, 4, 16, 42), 4)
    d.blobs(LEAF, [(-18, -6, 22), (18, -6, 22), (0, -24, 26), (0, 2, 22)])
    pygame.draw.circle(d.s, mix(LEAF, style.WHITE, 0.25), d.p(-8, -30), 12 * d.u)


def _umbrella(d: _Pic) -> None:
    d.limb(style.OUTLINE, (0, -36), (0, 30), 3)
    pygame.draw.arc(d.s, style.OUTLINE, d.rect(0, 18, 18, 20), math.pi, 2 * math.pi, round(5 * d.u))
    canopy = _arc_points(0, 4, 44, math.pi, 2 * math.pi)
    scallops = []
    for i in range(4):
        x0 = 44 - i * 22
        scallops += _arc_points(x0 - 11, 4, 11, 0, math.pi, 8)
    d.shaded_polygon(RED, canopy + scallops, band=0.25)
    for x in (-15, 15):
        d.line(style.OUTLINE, (0, -40), (x, 6), 1.6)


def _volcano(d: _Pic) -> None:
    d.blobs(GREY, [(-6, -38, 10), (6, -42, 12), (16, -36, 9)])
    d.shaded_polygon(BROWN, [(-46, 40), (-12, -20), (12, -20), (46, 40)])
    d.polygon(ORANGE, [(-12, -20), (12, -20), (8, -8), (3, 4), (-2, -6), (-7, 2), (-10, -10)])


def _watermelon(d: _Pic) -> None:
    d.polygon(GREEN, [(-46, -10), *_arc_points(0, -10, 46, 0, math.pi)[::-1], (46, -10)])
    d.polygon(
        CREAM, [(-40, -10), *_arc_points(0, -10, 40, 0, math.pi)[::-1], (40, -10)], outline=False
    )
    d.shaded_polygon(
        RED, [(-35, -10), *_arc_points(0, -10, 35, 0, math.pi)[::-1], (35, -10)], band=0.2
    )
    for x, y in ((-18, 0), (0, 8), (18, 0), (-8, 16), (8, 16)):
        d.ellipse(style.OUTLINE, (x - 2.5, y - 4, 5, 8), outline=False)


def _yoyo(d: _Pic) -> None:
    d.line(style.OUTLINE, (0, 8), (0, -44), 2)
    d.circle(style.WHITE, (0, -44), 5)
    d.shaded_circle(BLUE, (0, 10), 34)
    d.circle(mix(BLUE, style.WHITE, 0.4), (0, 10), 16)
    d.circle(YELLOW, (0, 10), 5)


def _fallback(d: _Pic) -> None:
    """For a picture the code cannot draw: a plain disc, so a content typo never crashes."""
    d.shaded_circle(GREY, (0, 0), 36)


DRAWINGS: dict[str, Callable[[_Pic], None]] = {
    "apple": _apple,
    "ball": _ball,
    "cat": _cat,
    "dog": _dog,
    "egg": _egg,
    "fish": _fish,
    "grapes": _grapes,
    "hat": _hat,
    "igloo": _igloo,
    "jam": _jam,
    "key": _key,
    "leaf": _leaf,
    "moon": _moon,
    "octopus": _octopus,
    "pig": _pig,
    "rainbow": _rainbow,
    "sun": _sun,
    "tree": _tree,
    "umbrella": _umbrella,
    "volcano": _volcano,
    "watermelon": _watermelon,
    "yoyo": _yoyo,
}


@lru_cache(maxsize=256)
def picture(picture_id: str, size: int) -> pygame.Surface:
    """The picture `size` pixels square (the fallback disc if there is no drawing for it)."""
    side = max(8, size) * K
    big = pygame.Surface((side, side), pygame.SRCALPHA)
    pen = _Pic(big, side / 100, (side / 2, side / 2), OUTLINE_W)
    DRAWINGS.get(picture_id, _fallback)(pen)
    return paint.finish(big)


def draw_picture(
    surface: pygame.Surface, picture_id: str, center: tuple[int, int], size: int
) -> None:
    sprite = picture(picture_id, size)
    surface.blit(sprite, sprite.get_rect(center=center))
