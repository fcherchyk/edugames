"""The shop's items, drawn with shapes in the art style (navy outline, one cel shade), so that they
need no image files and work in every language.

Items are drawn in the avatar's units (feet at (0, 0), the head's centre at (0, -268), the eyes
at (±34, -247)), so the same drawing goes on the avatar and, alone, on its tile in the shop.
Each item belongs to a layer: `back` items go behind the body, `feet` items over the legs
(instead of the avatar's own red shoes), `head` items on top of the hair, `eyes` items over the
eyes (a mask goes under them, so the eyes show through its holes), and a `pet` sits beside the
avatar, in front of everything.
"""

import math
from collections.abc import Callable
from functools import lru_cache

import pygame

from edugames.ui import paint, style
from edugames.ui.paint import K, Point, mix, shade

OUTLINE_W = 4  # in avatar units, as the avatar's own outline
CLEAR = (0, 0, 0, 0)
# Where items may reach, in avatar units: wider and taller than the figure (wings, tall hats, a
# pet on the right, flames under rocket boots).
ITEMS_FRAME = (-215, -530, 295, 40)  # left, top, right, bottom
PET_X = 212  # where a pet sits, right of the avatar, on the ground (y = 0)
EYES = ((-34, -247), (34, -247))

RED = (225, 55, 65)
PINK = (245, 130, 175)
ORANGE = (250, 150, 50)
YELLOW = (255, 210, 60)
GREEN = (90, 180, 80)
BLUE = (60, 120, 225)
SKY = (120, 185, 250)
PURPLE = (110, 80, 200)
WHITE = style.WHITE
SILVER = (205, 212, 228)
DARK = (48, 52, 86)


def oval(cx: float, cy: float, rx: float, ry: float, angle: float = 0, n: int = 36):
    """The points of an ellipse turned by `angle` degrees (negative turns its right end up)."""
    a = math.radians(angle)
    points = []
    for i in range(n):
        t = 2 * math.pi * i / n
        x, y = rx * math.cos(t), ry * math.sin(t)
        turned = (x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a))
        points.append((cx + turned[0], cy + turned[1]))
    return points


def half_oval(cx: float, base: float, rx: float, ry: float, top: bool = True, n: int = 24):
    """The top (or bottom) half of an ellipse whose middle line is y = `base`: a dome, a brim."""
    sign = -1 if top else 1
    return [
        (cx + rx * math.cos(math.pi * i / n), base + sign * ry * math.sin(math.pi * i / n))
        for i in range(n + 1)
    ]


def mirrored(side: int, points) -> list[Point]:
    """`points` drawn for the right side, flipped to the left when `side` is -1."""
    return [(side * x, y) for x, y in points]


def arc_band(center: Point, r_out: float, r_in: float, start: float, end: float, n: int = 24):
    """A curved band around `center` between two radii, from `start` to `end` degrees (counted
    anticlockwise from the right, as on a clock face seen from the front)."""
    cx, cy = center
    angles = [math.radians(start + (end - start) * i / n) for i in range(n + 1)]
    outer = [(cx + r_out * math.cos(a), cy - r_out * math.sin(a)) for a in angles]
    inner = [(cx + r_in * math.cos(a), cy - r_in * math.sin(a)) for a in reversed(angles)]
    return outer + inner


def heart(cx: float, cy: float, r: float, n: int = 40):
    points = []
    for i in range(n):
        t = 2 * math.pi * i / n
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        points.append((cx + x * r / 16, cy + (y - 2.5) * r / 16))
    return points


def rounded_box(cx: float, cy: float, half_w: float, half_h: float, radius: float, n: int = 6):
    """A rounded rectangle as points (so it can be scaled like any other shape)."""
    radius = min(radius, half_w, half_h)
    corners = ((1, 1, 0), (-1, 1, 90), (-1, -1, 180), (1, -1, 270))
    points = []
    for sx, sy, start in corners:
        ox, oy = cx + sx * (half_w - radius), cy + sy * (half_h - radius)
        for i in range(n + 1):
            a = math.radians(start + 90 * i / n)
            points.append((ox + radius * math.cos(a), oy + radius * math.sin(a)))
    return points


class ItemPen(paint.Pen):
    """The avatar's pen, with the shapes items need."""

    def shaded(self, color, points, split_x: float = 30, factor: float = 0.84) -> None:
        """A polygon with its cel shade on the right of `split_x`, like the avatar's shirt."""
        pts = [self.p(*q) for q in points]
        pygame.draw.polygon(self.s, color, pts)
        old = self.s.get_clip()
        x = self.p(split_x, 0)[0]
        self.s.set_clip(pygame.Rect(x, 0, self.s.get_width() - x, self.s.get_height()))
        pygame.draw.polygon(self.s, shade(color, factor), pts)
        self.s.set_clip(old)
        pygame.draw.polygon(self.s, style.OUTLINE, pts, self.lw)

    def shaded_below(self, color, points, band: float = 0.3) -> None:
        """A polygon with its cel shade as a strip along the bottom (like the boxes)."""
        pts = [self.p(*q) for q in points]
        pygame.draw.polygon(self.s, color, pts)
        top, bottom = min(y for _, y in pts), max(y for _, y in pts)
        cut = round(bottom - (bottom - top) * band)
        old = self.s.get_clip()
        self.s.set_clip(pygame.Rect(0, cut, self.s.get_width(), self.s.get_height() - cut))
        pygame.draw.polygon(self.s, shade(color, 0.86), pts)
        self.s.set_clip(old)
        pygame.draw.polygon(self.s, style.OUTLINE, pts, self.lw)

    def frame(
        self,
        shape: Callable[[float], list[Point]],
        r: float,
        width: float,
        color,
        lens: tuple[int, int, int, int] | None = None,
    ) -> None:
        """A frame around a see-through hole (glasses), with a tinted lens: `shape(r)` gives the
        outline of the frame at size `r`."""
        layer = pygame.Surface(self.s.get_size(), pygame.SRCALPHA)
        edge = self.outline

        def fill(size: float, fill_color) -> None:
            pygame.draw.polygon(layer, fill_color, [self.p(*q) for q in shape(size)])

        fill(r + edge, style.OUTLINE)
        fill(r, color)
        fill(r - width, style.OUTLINE)
        fill(r - width - edge, lens or CLEAR)
        self.s.blit(layer, (0, 0))

    def line(self, color, a: Point, b: Point, width: float) -> None:
        pygame.draw.line(self.s, color, self.p(*a), self.p(*b), max(1, round(width * self.u)))

    def glass(self, color: tuple[int, int, int, int], points) -> None:
        """A see-through shape (the space helmet's bubble), blended over what is below."""
        layer = pygame.Surface(self.s.get_size(), pygame.SRCALPHA)
        pygame.draw.polygon(layer, color, [self.p(*q) for q in points])
        self.s.blit(layer, (0, 0))


# --- Head: drawn on top of the hair -------------------------------------------------------------


def _cap(d: ItemPen) -> None:
    d.shaded(BLUE, half_oval(0, -300, 102, 94))
    d.polygon(YELLOW, paint.star_points((0, -340), 18))
    d.polygon(shade(BLUE, 0.78), half_oval(0, -302, 104, 30, top=False))
    d.circle(BLUE, (0, -396), 9)


def _party_hat(d: ItemPen) -> None:
    d.shaded(PINK, [(-46, -350), (46, -350), (8, -478)], split_x=14)
    for (x, y), r in (((-16, -370), 8), ((18, -374), 7), ((4, -404), 7), ((8, -438), 5)):
        d.circle(YELLOW, (x, y), r, outline=False)
    d.blobs(YELLOW, [(8, -482, 15), (-4, -478, 9), (20, -478, 9)])


def _bunny_ears(d: ItemPen) -> None:
    for s in (-1, 1):
        d.polygon(WHITE, oval(s * 46, -420, 24, 64, s * 12))
        d.polygon(PINK, oval(s * 47, -414, 11, 44, s * 12), outline=False)
    d.polygon(PINK, arc_band((0, -268), 114, 98, 18, 162))


def _flower_crown(d: ItemPen) -> None:
    d.polygon(GREEN, arc_band((0, -268), 108, 96, 22, 158))
    colors = (PINK, WHITE, SKY, YELLOW, PINK, WHITE, SKY)
    for i, color in enumerate(colors):
        a = math.radians(30 + 120 * i / (len(colors) - 1))
        x, y = 102 * math.cos(a), -268 - 102 * math.sin(a)
        if i % 2:
            d.polygon(GREEN, oval(x, y + 14, 14, 7, -30 if x > 0 else 30))
        petals = [(px, py, 10) for px, py in paint.star_points((x, y), 11)[::2]]
        d.blobs(color, petals)
        d.circle(ORANGE if color == YELLOW else YELLOW, (x, y), 7)


def _woolly_hat(d: ItemPen) -> None:
    color = (230, 75, 90)
    d.blobs(WHITE, [(0, -412, 24), (-16, -400, 18), (16, -400, 18)])
    dome = half_oval(0, -306, 106, 96)
    d.shaded(color, dome)
    old = d.s.get_clip()
    d.s.set_clip(d.rect(-120, -366, 240, 20))
    pygame.draw.polygon(d.s, WHITE, [d.p(*q) for q in dome])
    d.s.set_clip(old)
    pygame.draw.polygon(d.s, style.OUTLINE, [d.p(*q) for q in dome], d.lw)
    band = mix(color, WHITE, 0.2)
    d.rrect(band, (-114, -330, 228, 42), 20)
    for x in range(-96, 100, 16):
        d.line(shade(band, 0.82), (x, -324), (x, -294), 4)


def _wizard_hat(d: ItemPen) -> None:
    brim = oval(0, -330, 128, 24)
    d.polygon(shade(PURPLE, 0.8), brim)
    cone = [(-72, -336), (-36, -430), (0, -490), (46, -520), (22, -470), (30, -420), (72, -336)]
    d.shaded(PURPLE, cone, split_x=20)
    d.polygon(style.GOLD, [(-68, -346), (68, -346), (62, -370), (-62, -370)])
    d.polygon(style.GOLD, paint.star_points((-12, -418), 16))
    d.polygon(style.GOLD, paint.star_points((16, -462), 10))
    d.polygon(shade(PURPLE, 0.8), half_oval(0, -330, 128, 24, top=False))


def _space_helmet(d: ItemPen) -> None:
    d.rrect(SILVER, (-86, -180, 172, 36), 18)
    for x in (-50, 0, 50):
        d.circle((240, 90, 80) if x else (90, 200, 110), (x, -162), 7)
    bubble = oval(0, -272, 138, 138, n=64)
    d.glass((215, 240, 255, 45), bubble)
    d.glass((255, 255, 255, 200), arc_band((0, -272), 122, 110, 110, 160))
    d.circle(WHITE, (-66, -378), 6, outline=False)
    pts = [d.p(*q) for q in bubble]
    pygame.draw.polygon(d.s, style.OUTLINE, pts, d.lw * 3)
    pygame.draw.polygon(d.s, SILVER, pts, d.lw)


def _crown(d: ItemPen) -> None:
    gold = style.GOLD
    spikes = [(-72, -330), (-86, -424), (-44, -384), (0, -444), (44, -384), (86, -424), (72, -330)]
    for x, y in spikes[1:6:2] + [spikes[3]]:
        d.circle(gold, (x, y), 10)
    d.shaded_below(gold, spikes)
    d.circle(RED, (0, -352), 12)
    d.polygon(SKY, oval(-44, -350, 10, 8))
    d.polygon(GREEN, oval(44, -350, 10, 8))
    d.circle(WHITE, (-4, -356), 3, outline=False)
    d.line(mix(gold, WHITE, 0.6), (-60, -402), (-56, -372), 5)


# --- Eyes: drawn over the eyes (a mask under them) ----------------------------------------------


def _temples(d: ItemPen, color, y: float = -252) -> None:
    for s in (-1, 1):
        d.limb(color, (s * 96, y - 6), (s * 62, y), 6)
    d.limb(color, (-10, y - 2), (10, y - 2), 6)


def _round_glasses(d: ItemPen) -> None:
    color = (215, 70, 80)
    _temples(d, color)
    for cx, cy in EYES:
        d.frame(lambda r, cx=cx, cy=cy: oval(cx, cy, r, r), 29, 7, color, (200, 230, 255, 50))


def _sunglasses(d: ItemPen) -> None:
    _temples(d, DARK)
    for cx, cy in EYES:
        d.rrect(DARK, (cx - 30, cy - 22, 60, 44), 18)
        d.polygon(
            mix(DARK, WHITE, 0.55),
            [(cx - 20, cy - 4), (cx - 8, cy - 16), (cx - 2, cy - 16), (cx - 14, cy - 4)],
            outline=False,
        )


def _heart_glasses(d: ItemPen) -> None:
    color = (235, 80, 150)
    _temples(d, color)
    for cx, cy in EYES:
        d.frame(lambda r, cx=cx, cy=cy: heart(cx, cy + 2, r), 34, 8, color, (255, 150, 200, 110))


def _star_glasses(d: ItemPen) -> None:
    _temples(d, ORANGE)
    for cx, cy in EYES:
        d.frame(
            lambda r, cx=cx, cy=cy: paint.star_points((cx, cy + 2), r, 0.62),
            40,
            8,
            style.GOLD,
            (255, 235, 130, 100),
        )


def _ski_goggles(d: ItemPen) -> None:
    d.rrect(ORANGE, (-108, -262, 216, 24), 10)
    lens = (255, 170, 60, 120)
    d.frame(lambda r: rounded_box(0, -250, r, r * 0.44, r * 0.4), 78, 10, WHITE, lens)
    d.line(WHITE, (-52, -260), (-40, -272), 5)


def _hero_mask(d: ItemPen) -> None:
    for s in (-1, 1):
        tail = [(90, -262), (124, -280), (118, -250), (128, -236), (90, -244)]
        d.polygon(RED, mirrored(s, tail))
    mask = [(-80, -262), (-62, -284), (-24, -280), (0, -266), (24, -280), (62, -284), (80, -262),
            (66, -226), (26, -222), (0, -238), (-26, -222), (-66, -226)]  # fmt: skip
    d.shaded_below(RED, mask)


# --- Back: drawn behind the body ----------------------------------------------------------------


def _cape(d: ItemPen) -> None:
    cape = [(-50, -172), (50, -172), (98, -26), (60, -14), (0, -20), (-60, -14), (-98, -26)]
    d.shaded(RED, cape, split_x=20)
    for s in (-1, 1):
        d.polygon(RED, [(s * 62, -166), (s * 44, -200), (s * 16, -166)])


def _butterfly_wings(d: ItemPen) -> None:
    """Monarch-like wings: a dark rim with white dots around orange and yellow."""
    for side in (-1, 1):
        for (x, y, rx, ry, angle), color in (
            ((92, -126, 46, 36, 28), YELLOW),
            ((116, -222, 76, 50, -28), ORANGE),
        ):
            d.polygon(DARK, oval(side * x, y, rx, ry, side * angle))
            d.polygon(color, oval(side * (x - 4), y + 2, rx - 12, ry - 11, side * angle), False)
        for x, y in ((176, -260), (186, -232), (132, -266), (124, -102)):
            d.circle(WHITE, (side * x, y), 5, outline=False)
        d.line(shade(ORANGE, 0.7), (side * 54, -196), (side * 150, -240), 4)


def _bird_wings(d: ItemPen) -> None:
    """White feathered wings: long flight feathers under a row of short ones."""
    wing = [(40, -196), (84, -254), (140, -292), (188, -300), (204, -268), (198, -214),
            (182, -160), (162, -112), (150, -136), (138, -118), (126, -146), (110, -130),
            (102, -158), (84, -142), (78, -168), (48, -150)]  # fmt: skip
    coverts = [(42, -200), (84, -256), (140, -292), (188, -300), (200, -262), (184, -234),
               (172, -248), (158, -222), (146, -240), (130, -212), (118, -230), (102, -204),
               (90, -220), (72, -192), (58, -200)]  # fmt: skip
    for side in (-1, 1):
        d.shaded_below((236, 241, 252), mirrored(side, wing), band=0.25)
        d.polygon(WHITE, mirrored(side, coverts))


def _dragon_wings(d: ItemPen) -> None:
    right = [(40, -190), (100, -262), (192, -302), (184, -226), (160, -238), (150, -180),
             (124, -196), (112, -142), (86, -162), (50, -124)]  # fmt: skip
    for s in (-1, 1):
        d.shaded_below(GREEN, mirrored(s, right), band=0.35)
        for x, y in ((184, -226), (150, -180), (112, -142)):
            d.line(shade(GREEN, 0.66), (s * 100, -262), (s * x, y), 5)
        d.circle(shade(GREEN, 0.66), (s * 100, -262), 8)


def _jetpack(d: ItemPen) -> None:
    for s in (-1, 1):
        x = 56 if s > 0 else -108
        flame = [(70, -80), (96, -80), (100, -56), (83, -22), (66, -56)]
        d.polygon(YELLOW, mirrored(s, flame))
        inner = [(76, -78), (90, -78), (92, -60), (83, -40), (74, -60)]
        d.polygon(ORANGE, mirrored(s, inner), outline=False)
        d.polygon(DARK, mirrored(s, [(66, -98), (100, -98), (94, -80), (72, -80)]))
        d.rrect(SILVER, (x, -204, 52, 114), 22)
        d.rrect(RED, (x + 2, -214, 48, 28), 12)


# --- Feet: drawn over the legs, instead of the avatar's own shoes -------------------------------


def _foot(d: ItemPen, side: int, color, box=(-28, -28, 56, 30)) -> None:
    """The front of a shoe, with its cel shade along the bottom."""
    x, y, w, h = box
    d.shaded_below(color, oval(side * 26 + x + w / 2, y + h / 2, w / 2, h / 2), band=0.35)


def _sneakers(d: ItemPen) -> None:
    for side in (-1, 1):
        d.polygon(WHITE, oval(side * 26, -10, 30, 13))
        _foot(d, side, BLUE, (-27, -30, 54, 26))
        d.polygon(WHITE, oval(side * 26, -12, 12, 7), outline=False)
        for y in (-24, -19):
            d.line(WHITE, (side * 26 - 7, y), (side * 26 + 7, y), 3)


def _bunny_slippers(d: ItemPen) -> None:
    for side in (-1, 1):
        for ear in (-9, 9):
            d.polygon(WHITE, oval(side * 26 + ear, -36, 6, 15, ear * 1.5))
            d.polygon(PINK, oval(side * 26 + ear, -35, 2.5, 9, ear * 1.5), outline=False)
        _foot(d, side, WHITE, (-31, -32, 62, 34))
        for ex in (-8, 8):
            d.circle(DARK, (side * 26 + ex, -20), 3, outline=False)
        d.circle(PINK, (side * 26, -12), 4, outline=False)


def _rain_boots(d: ItemPen) -> None:
    color = YELLOW
    for side in (-1, 1):
        d.rrect(color, (side * 22 - 18, -66, 36, 50), 8)
        d.rrect(shade(color, 0.8), (side * 22 - 20, -70, 40, 12), 6)
        _foot(d, side, color)


def _flippers(d: ItemPen) -> None:
    for side in (-1, 1):
        fin = [(side * 14, -26), (side * 40, -26), (side * 66, 10), (side * 40, 16), (side * 4, 12)]
        d.shaded_below(GREEN, fin, band=0.4)
        for x in (18, 32, 44):
            d.line(shade(GREEN, 0.7), (side * (x - 2), -16), (side * (x + 6), 8), 3)


def _snow_boots(d: ItemPen) -> None:
    brown = (150, 100, 60)
    for side in (-1, 1):
        d.rrect(brown, (side * 22 - 19, -58, 38, 46), 10)
        _foot(d, side, brown)
        d.blobs(WHITE, [(side * 22 + x, -58, 10) for x in (-13, 0, 13)])


def _roller_skates(d: ItemPen) -> None:
    for side in (-1, 1):
        for x in (-14, 14):
            d.circle(ORANGE, (side * 26 + x, 6), 8)
        d.rrect(WHITE, (side * 22 - 17, -60, 34, 44), 10)
        _foot(d, side, WHITE, (-28, -26, 56, 26))
        d.rrect(RED, (side * 22 - 17, -48, 34, 8), 3, outline=False)


def _rocket_boots(d: ItemPen) -> None:
    for side in (-1, 1):
        x = side * 26
        d.polygon(YELLOW, [(x - 16, 0), (x + 16, 0), (x + 8, 22), (x, 36), (x - 8, 22)])
        d.polygon(ORANGE, [(x - 8, 0), (x + 8, 0), (x + 4, 14), (x, 22), (x - 4, 14)], False)
        d.rrect(SILVER, (side * 22 - 18, -62, 36, 46), 8)
        _foot(d, side, SILVER)
        d.rrect(RED, (side * 22 - 18, -50, 36, 9), 3, outline=False)


# --- Pets: beside the avatar, in front of everything ----------------------------------------------


def _pet_pen(d: ItemPen) -> ItemPen:
    """The same pen, with (0, 0) on the ground where the pet sits."""
    return ItemPen(d.s, d.u, (d.ox + PET_X * d.u, d.oy), d.outline)


def _pet_shadow(d: ItemPen, width: float) -> None:
    shadow = pygame.Surface((round(width * d.u), round(14 * d.u)), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow, (20, 40, 20, 70), shadow.get_rect())
    d.s.blit(shadow, d.p(-width / 2, -7))


def _pet_eyes(d: ItemPen, y: float, gap: float, r: float = 5) -> None:
    for side in (-1, 1):
        d.circle(DARK, (side * gap, y), r, outline=False)
        d.circle(WHITE, (side * gap - r * 0.3, y - r * 0.35), r * 0.38, outline=False)


def _pet_smile(d: ItemPen, y: float, w: float, color=style.OUTLINE) -> None:
    box = d.rect(-w / 2, y - w / 3, w, w / 1.5)
    pygame.draw.arc(d.s, color, box, math.pi + 0.5, 2 * math.pi - 0.5, d.lw)


Draw = Callable[[ItemPen], None]


def _sitter(
    d: ItemPen,
    fur,
    nose,
    behind: Draw | None = None,
    on_head: Draw | None = None,
    eyes: Draw | None = None,
    tail_tip=None,
    mouth=style.OUTLINE,
) -> None:
    """A cat or a dog sitting and facing us. `behind` draws what goes behind its head (ears, a
    mane, spots on the body), `on_head` what goes on it (floppy ears, stripes, a mask)."""
    _pet_shadow(d, 80)
    d.limb(fur, (30, -10), (44, -56), 10)
    if tail_tip:
        d.circle(tail_tip, (44, -58), 9)
    d.polygon(fur, oval(0, -36, 30, 36))
    d.polygon(mix(fur, WHITE, 0.55), oval(0, -30, 15, 24), outline=False)
    for side in (-1, 1):
        d.polygon(fur, oval(side * 13, -4, 11, 7))
    if behind:
        behind(d)
    d.circle(fur, (0, -84), 30)
    if on_head:
        on_head(d)
    (eyes or (lambda d: _pet_eyes(d, -88, 11)))(d)
    d.circle(nose, (0, -78), 4, outline=False)
    _pet_smile(d, -72, 10, mouth)


def _pointed_ears(fur, inner) -> Draw:
    def ears(d: ItemPen) -> None:
        for side in (-1, 1):
            d.polygon(fur, [(side * 26, -96), (side * 26, -126), (side * 6, -108)])
            d.polygon(inner, [(side * 23, -101), (side * 23, -118), (side * 12, -107)], False)

    return ears


def _floppy_ears(color) -> Draw:
    def ears(d: ItemPen) -> None:
        for side in (-1, 1):
            d.polygon(color, oval(side * 30, -82, 10, 22, side * -18))

    return ears


def _whiskers(d: ItemPen, color=DARK) -> None:
    for side in (-1, 1):
        d.line(color, (side * 10, -76), (side * 34, -80), 1.6)
        d.line(color, (side * 10, -72), (side * 34, -68), 1.6)


def _cat_eyes(iris) -> Draw:
    """Coloured cat's eyes with slit pupils (for fur too dark for plain dark eyes)."""

    def eyes(d: ItemPen) -> None:
        for side in (-1, 1):
            d.circle(iris, (side * 11, -88), 6.5)
            d.polygon(DARK, oval(side * 11, -88, 1.8, 5.5), outline=False)
            d.circle(WHITE, (side * 11 - 2, -91), 1.6, outline=False)

    return eyes


# Cats


def _kitten(d: ItemPen) -> None:
    d = _pet_pen(d)
    grey = (175, 180, 195)
    _sitter(d, grey, PINK, behind=_pointed_ears(grey, PINK))
    _whiskers(d)


def _ginger_cat(d: ItemPen) -> None:
    d = _pet_pen(d)
    ginger = (240, 150, 70)

    def stripes(d: ItemPen) -> None:
        for x, top in ((-11, -110), (0, -113), (11, -110)):
            d.line(shade(ginger, 0.72), (x, top), (x * 0.8, top + 11), 4)

    _sitter(d, ginger, PINK, behind=_pointed_ears(ginger, PINK), on_head=stripes)
    _whiskers(d)
    for y in (-44, -32):
        d.line(shade(ginger, 0.72), (-28, y), (-20, y + 2), 4)


def _black_cat(d: ItemPen) -> None:
    d = _pet_pen(d)
    black = (62, 62, 88)
    _sitter(
        d, black, PINK, behind=_pointed_ears(black, PINK), eyes=_cat_eyes((160, 215, 90)),
        mouth=WHITE,
    )  # fmt: skip
    _whiskers(d, WHITE)


def _lion_cub(d: ItemPen) -> None:
    d = _pet_pen(d)
    fur, mane = (235, 185, 95), (200, 115, 55)

    def mane_ring(d: ItemPen) -> None:
        ring = [(38 * math.cos(a), -84 + 38 * math.sin(a), 14)
                for a in (2 * math.pi * i / 12 for i in range(12))]  # fmt: skip
        d.blobs(mane, ring)

    _sitter(d, fur, (120, 70, 40), behind=mane_ring, tail_tip=mane)


# Dogs


def _puppy(d: ItemPen) -> None:
    d = _pet_pen(d)
    tan = (205, 150, 95)
    _sitter(d, tan, DARK, on_head=_floppy_ears(shade(tan, 0.7)))
    d.polygon(PINK, oval(0, -66, 5, 6), outline=False)


def _dalmatian(d: ItemPen) -> None:
    d = _pet_pen(d)
    white = (248, 248, 252)

    def spots(d: ItemPen) -> None:
        for (x, y), r in (((-14, -46), 5), ((12, -26), 6), ((17, -55), 4), ((-8, -16), 4)):
            d.circle(DARK, (x, y), r, outline=False)

    def ears_and_spot(d: ItemPen) -> None:
        _floppy_ears(DARK)(d)
        d.circle(DARK, (14, -104), 6, outline=False)

    _sitter(d, white, DARK, behind=spots, on_head=ears_and_spot)
    d.polygon(PINK, oval(0, -66, 5, 6), outline=False)


def _poodle(d: ItemPen) -> None:
    d = _pet_pen(d)
    fur = (250, 212, 226)

    def topknot(d: ItemPen) -> None:
        d.blobs(fur, [(0, -114, 15), (-13, -108, 11), (13, -108, 11)])
        for side in (-1, 1):
            d.polygon(RED, [(0, -124), (side * 14, -132), (side * 14, -118)])
        d.circle(RED, (0, -124), 4)

    def fluffy_ears(d: ItemPen) -> None:
        for side in (-1, 1):
            d.blobs(fur, [(side * 32, -80, 12), (side * 34, -64, 11)])

    _sitter(d, fur, DARK, behind=topknot, on_head=fluffy_ears, tail_tip=fur)


def _husky(d: ItemPen) -> None:
    d = _pet_pen(d)
    grey = (135, 148, 172)

    def mask(d: ItemPen) -> None:
        d.polygon(WHITE, oval(0, -74, 22, 17), outline=False)
        d.polygon(WHITE, [(-6, -104), (6, -104), (0, -88)], outline=False)

    def blue_eyes(d: ItemPen) -> None:
        for side in (-1, 1):
            d.circle(SKY, (side * 11, -88), 5.5)
            d.circle(DARK, (side * 11, -88), 2.6, outline=False)

    _sitter(d, grey, DARK, behind=_pointed_ears(grey, WHITE), on_head=mask, eyes=blue_eyes)
    d.polygon(PINK, oval(0, -66, 5, 6), outline=False)  # a dog's tongue


# Birds


def _chick(d: ItemPen) -> None:
    d = _pet_pen(d)
    _pet_shadow(d, 66)
    for side in (-1, 1):
        d.polygon(ORANGE, oval(side * 11, -3, 9, 5))
    for x, angle in ((-6, 20), (0, 0), (6, -20)):
        d.polygon(YELLOW, oval(x, -86, 4, 10, angle))
    d.circle(YELLOW, (0, -42), 38)
    for side in (-1, 1):
        d.polygon(shade(YELLOW, 0.88), oval(side * 34, -38, 9, 16, side * -25))
    _pet_eyes(d, -54, 12)
    d.polygon(ORANGE, [(-7, -44), (7, -44), (0, -34)])
    d.polygon((245, 150, 170), oval(-22, -40, 5, 3), outline=False)
    d.polygon((245, 150, 170), oval(22, -40, 5, 3), outline=False)


def _parrot(d: ItemPen) -> None:
    d = _pet_pen(d)
    red = (225, 60, 60)
    _pet_shadow(d, 60)
    d.polygon(BLUE, [(-10, -30), (6, -30), (0, 2), (-14, -2)])
    d.polygon(YELLOW, [(2, -30), (16, -30), (16, 0), (4, -4)])
    for side in (-1, 1):
        d.polygon(DARK, oval(side * 10, -8, 8, 4))
    d.polygon(red, oval(0, -52, 26, 38))
    d.polygon(GREEN, oval(-20, -50, 12, 28, 12))
    d.polygon(BLUE, oval(-24, -36, 7, 14, 12), outline=False)
    d.circle(red, (2, -96), 24)
    d.polygon((245, 225, 150), [(16, -104), (34, -92), (22, -78), (14, -86)])
    d.circle(WHITE, (8, -102), 8)
    d.circle(DARK, (10, -102), 3.5, outline=False)


def _owl(d: ItemPen) -> None:
    d = _pet_pen(d)
    brown = (150, 100, 60)
    _pet_shadow(d, 70)
    for side in (-1, 1):
        d.polygon(ORANGE, oval(side * 12, -3, 9, 5))
        d.polygon(brown, [(side * 14, -90), (side * 30, -116), (side * 32, -86)])
    d.polygon(brown, oval(0, -50, 34, 48))
    d.polygon(mix(brown, WHITE, 0.55), oval(0, -34, 20, 26), outline=False)
    for x, y in ((-8, -40), (8, -40), (0, -28), (-8, -18), (8, -18)):
        d.line(shade(brown, 0.8), (x - 4, y - 3), (x, y), 2.5)
        d.line(shade(brown, 0.8), (x, y), (x + 4, y - 3), 2.5)
    for side in (-1, 1):
        d.polygon(shade(brown, 0.8), oval(side * 32, -48, 9, 22, side * -12))
        d.circle(WHITE, (side * 14, -74), 13)
        d.circle(YELLOW, (side * 14, -74), 8, outline=False)
        d.circle(DARK, (side * 14, -74), 4.5, outline=False)
        d.circle(WHITE, (side * 14 - 2, -77), 1.6, outline=False)
    d.polygon(ORANGE, [(-5, -64), (5, -64), (0, -54)])


def _penguin(d: ItemPen) -> None:
    d = _pet_pen(d)
    _pet_shadow(d, 70)
    d.polygon(ORANGE, oval(-12, -3, 12, 6))
    d.polygon(ORANGE, oval(12, -3, 12, 6))
    for side in (-1, 1):
        d.polygon(DARK, oval(side * 32, -46, 9, 24, side * -20))
    d.polygon(DARK, oval(0, -56, 32, 54))
    d.polygon(WHITE, oval(0, -44, 22, 38), outline=False)
    d.polygon(WHITE, oval(0, -80, 20, 16), outline=False)
    _pet_eyes(d, -84, 9, 4.5)
    d.polygon(ORANGE, [(-7, -76), (7, -76), (0, -66)])
    d.circle((245, 150, 170), (-16, -70), 4, outline=False)
    d.circle((245, 150, 170), (16, -70), 4, outline=False)


# Monsters (friendly ones)


def _fuzzy_monster(d: ItemPen) -> None:
    d = _pet_pen(d)
    blue = (90, 140, 235)
    _pet_shadow(d, 80)
    for side in (-1, 1):
        d.polygon(YELLOW, [(side * 14, -84), (side * 28, -108), (side * 30, -80)])
        d.polygon(blue, oval(side * 16, -4, 12, 7))
    fur = [(40 * math.cos(a), -46 + 40 * math.sin(a), 9)
           for a in (2 * math.pi * i / 16 for i in range(16))]  # fmt: skip
    d.blobs(blue, [*fur, (0, -46, 40)])
    for side in (-1, 1):
        d.circle(WHITE, (side * 13, -58), 11)
        d.circle(DARK, (side * 11, -56), 5, outline=False)
    mouth = half_oval(0, -38, 20, 14, top=False)
    d.polygon(DARK, mouth)
    d.polygon(WHITE, [(-4, -38), (6, -38), (1, -30)], outline=False)


def _one_eyed_monster(d: ItemPen) -> None:
    d = _pet_pen(d)
    green = (120, 205, 95)
    _pet_shadow(d, 70)
    for side in (-1, 1):
        d.limb(green, (side * 10, -88), (side * 18, -112), 4)
        d.circle(PINK, (side * 18, -114), 6)
        d.polygon(green, oval(side * 14, -4, 11, 7))
        d.limb(green, (side * 26, -50), (side * 40, -38), 7)
    d.polygon(green, oval(0, -50, 30, 44))
    d.circle(WHITE, (0, -64), 16)
    d.circle(PURPLE, (0, -62), 8, outline=False)
    d.circle(DARK, (0, -62), 4, outline=False)
    d.circle(WHITE, (-3, -66), 2, outline=False)
    _pet_smile(d, -34, 16)


# Robots


def _robot(d: ItemPen) -> None:
    d = _pet_pen(d)
    _pet_shadow(d, 70)
    for x in (-16, 16):
        d.circle(DARK, (x, -6), 8)
    d.rrect(SILVER, (-28, -58, 56, 48), 10)
    d.circle(RED, (0, -34), 7)
    d.limb(DARK, (0, -96), (0, -118), 3)
    d.circle(RED, (0, -120), 7)
    d.rrect(SILVER, (-30, -100, 60, 44), 12)
    d.rrect((70, 200, 220), (-22, -93, 44, 30), 8)
    for x in (-9, 9):
        d.circle(WHITE, (x, -80), 4.5, outline=False)
    for side in (-1, 1):
        d.limb(SILVER, (side * 28, -46), (side * 40, -30), 7)


def _robo_dog(d: ItemPen) -> None:
    d = _pet_pen(d)
    _pet_shadow(d, 80)
    d.limb(DARK, (24, -40), (40, -62), 3)
    d.circle(RED, (41, -64), 6)
    for x in (-22, -9, 9, 22):
        d.rrect(DARK, (x - 4, -18, 8, 18), 3)
    d.rrect(SILVER, (-30, -58, 60, 44), 12)
    d.circle(RED, (0, -36), 6)
    for side in (-1, 1):
        d.polygon(DARK, [(side * 10, -104), (side * 26, -122), (side * 24, -100)])
    d.rrect(SILVER, (-26, -106, 52, 42), 12)
    d.rrect((70, 200, 220), (-18, -98, 36, 24), 7)
    for x in (-8, 8):
        d.circle(WHITE, (x, -88), 4, outline=False)
    d.line(WHITE, (-5, -80), (5, -80), 2)


def _drone(d: ItemPen) -> None:
    """A little robot that hovers over its shadow."""
    d = _pet_pen(d)
    _pet_shadow(d, 56)
    d.limb(DARK, (0, -96), (0, -110), 4)
    d.polygon((215, 225, 240), oval(0, -112, 36, 6))
    d.circle(DARK, (0, -112), 4)
    for side, color in ((-1, RED), (1, GREEN)):
        d.circle(color, (side * 30, -66), 6)
    d.circle(SILVER, (0, -68), 28)
    d.rrect((70, 200, 220), (-16, -78, 32, 20), 7)
    for x in (-7, 7):
        d.circle(WHITE, (x, -68), 3.5, outline=False)
    d.polygon(YELLOW, [(-6, -40), (6, -40), (0, -30)])


def _baby_dragon(d: ItemPen) -> None:
    d = _pet_pen(d)
    green = (110, 195, 110)
    _pet_shadow(d, 90)
    d.limb(green, (24, -12), (50, -18), 10)
    d.polygon(ORANGE, [(50, -28), (62, -18), (50, -8), (54, -18)])
    for side in (-1, 1):
        wing = [
            (side * 18, -66),
            (side * 46, -96),
            (side * 52, -70),
            (side * 40, -74),
            (side * 30, -56),
        ]
        d.polygon(mix(green, SKY, 0.35), wing)
    d.polygon(green, oval(0, -36, 30, 36))
    d.polygon(YELLOW, oval(0, -30, 16, 24), outline=False)
    for side in (-1, 1):
        d.polygon(green, oval(side * 14, -4, 12, 7))
        d.polygon(YELLOW, [(side * 10, -104), (side * 22, -126), (side * 24, -104)])
    d.circle(green, (0, -84), 28)
    _pet_eyes(d, -88, 11)
    for x in (-5, 5):
        d.circle(shade(green, 0.6), (x, -74), 2.5, outline=False)
    _pet_smile(d, -68, 12)


def _nothing(d: ItemPen) -> None:
    """An item with no drawing (a typo, a removed item): nothing shows, nothing crashes."""


DRAWINGS: dict[str, Callable[[ItemPen], None]] = {
    "cap": _cap,
    "party_hat": _party_hat,
    "bunny_ears": _bunny_ears,
    "flower_crown": _flower_crown,
    "woolly_hat": _woolly_hat,
    "wizard_hat": _wizard_hat,
    "space_helmet": _space_helmet,
    "crown": _crown,
    "round_glasses": _round_glasses,
    "sunglasses": _sunglasses,
    "heart_glasses": _heart_glasses,
    "star_glasses": _star_glasses,
    "ski_goggles": _ski_goggles,
    "hero_mask": _hero_mask,
    "cape": _cape,
    "butterfly_wings": _butterfly_wings,
    "bird_wings": _bird_wings,
    "dragon_wings": _dragon_wings,
    "jetpack": _jetpack,
    "sneakers": _sneakers,
    "bunny_slippers": _bunny_slippers,
    "rain_boots": _rain_boots,
    "flippers": _flippers,
    "snow_boots": _snow_boots,
    "roller_skates": _roller_skates,
    "rocket_boots": _rocket_boots,
    "kitten": _kitten,
    "ginger_cat": _ginger_cat,
    "black_cat": _black_cat,
    "lion_cub": _lion_cub,
    "puppy": _puppy,
    "dalmatian": _dalmatian,
    "poodle": _poodle,
    "husky": _husky,
    "chick": _chick,
    "parrot": _parrot,
    "owl": _owl,
    "penguin": _penguin,
    "fuzzy_monster": _fuzzy_monster,
    "one_eyed_monster": _one_eyed_monster,
    "baby_dragon": _baby_dragon,
    "robot": _robot,
    "robo_dog": _robo_dog,
    "drone": _drone,
}
UNDER_THE_EYES = frozenset({"hero_mask"})


def draw_item(pen: ItemPen, item_id: str) -> None:
    """Draw an item with `pen`, in avatar units."""
    DRAWINGS.get(item_id, _nothing)(pen)


@lru_cache(maxsize=256)
def item_icon(item_id: str, size: int, silhouette: bool = False) -> pygame.Surface:
    """The item alone, fitted in a `size` square: for its tile in the shop. A silhouette (for an
    item not open yet) is its shape in one flat colour."""
    left, top, right, bottom = ITEMS_FRAME
    u = K * size / 150
    big = pygame.Surface((round((right - left) * u), round((bottom - top) * u)), pygame.SRCALPHA)
    draw_item(ItemPen(big, u, (-left * u, -top * u), OUTLINE_W), item_id)
    box = big.get_bounding_rect()
    if box.w == 0 or box.h == 0:
        return pygame.Surface((size, size), pygame.SRCALPHA)
    drawing = big.subsurface(box)
    scale = min(size / box.w, size / box.h)
    icon = pygame.transform.smoothscale(
        drawing, (max(1, round(box.w * scale)), max(1, round(box.h * scale)))
    )
    if silhouette:
        mask = pygame.mask.from_surface(icon, 100)
        icon = mask.to_surface(setcolor=(*style.MUTED, 255), unsetcolor=(0, 0, 0, 0))
    return icon


def draw_item_icon(
    surface: pygame.Surface,
    item_id: str,
    center: tuple[int, int],
    size: int,
    silhouette: bool = False,
) -> None:
    sprite = item_icon(item_id, size, silhouette)
    surface.blit(sprite, sprite.get_rect(center=center))


def draw_shirt(surface: pygame.Surface, rgb, center: tuple[int, int], width: float) -> None:
    """A T-shirt shape with a navy outline and a cel shade on its right side (a shirt's tile)."""
    cx, cy = center
    u = width / 100
    shape = [(-22, -40), (-50, -28), (-50, -2), (-32, -6), (-32, 40), (32, 40), (32, -6),
             (50, -2), (50, -28), (22, -40), (0, -28)]  # fmt: skip
    points = [(cx + x * u, cy + y * u) for x, y in shape]
    pygame.draw.polygon(surface, rgb, points)
    shaded = [(cx + x * u, cy + y * u) for x, y in ((12, -36), (22, -40), (50, -28), (50, -2),
              (32, -6), (32, 40), (12, 40))]  # fmt: skip
    pygame.draw.polygon(surface, paint.shade(rgb, 0.85), shaded)
    pygame.draw.polygon(surface, style.OUTLINE, points, max(3, round(4 * u)))
