"""Choosing a look, for free, one thing at a time: face, skin, hair, hair colour, eyes, freckles.
Used when a player is created (in order, with "Next") and in the shop's "Me" tab.

- A row of chips, each a picture with its word under it, says what can be changed; the open one
  is orange, like the shop's tabs.
- Under its title, the open chip's choices are big tiles that show only what changes: a face, a
  head with each hair, an eye of each colour, a face without and with freckles.
- A mirror shows the player's head and shoulders large, without the items that would hide what
  is being chosen (a hat while choosing hair, glasses while choosing eyes), and sparkles where
  the look has just changed.
"""

import math
from collections.abc import Callable
from functools import lru_cache

import pygame

from edugames.core import avatar as options
from edugames.core.avatar import NOTHING, Avatar
from edugames.core.content import Content
from edugames.ui import paint, style
from edugames.ui.avatar_draw import HEAD_CENTER, HEAD_R, draw_bust, draw_head
from edugames.ui.items_draw import ItemPen, oval
from edugames.ui.paint import K, shade
from edugames.ui.widgets import Button, draw_chip

CATEGORIES = ("face", "skin", "hair_style", "hair_color", "eye_color", "freckles")
CHOICES: dict[str, tuple] = {
    "face": options.FACES,
    "skin": tuple(options.SKIN_TONES),
    "hair_style": options.HAIR_STYLES,
    "hair_color": tuple(options.HAIR_COLORS),
    "eye_color": tuple(options.EYE_COLORS),
    "freckles": options.FRECKLES,
}
WORDS = {  # the key of each chip's word in the strings
    "face": "face",
    "skin": "skin",
    "hair_style": "hair",
    "hair_color": "hair_color",
    "eye_color": "eye_color",
    "freckles": "freckles",
}
# Items that hide a part of the look: the mirror takes them off while that part is chosen.
HIDES = {
    "face": ("eyes",),
    "eye_color": ("eyes",),
    "freckles": ("eyes",),
    "hair_style": ("head",),
    "hair_color": ("head",),
    "skin": (),
}
COVERS_THE_HEAD = frozenset({"space_helmet"})  # its glass tints the whole head: always taken off
# Where each choice shows on the head (avatar units): the mirror sparkles there after a change.
PARTS: dict[str, tuple[tuple[float, float], ...]] = {
    "face": ((0, -214), (-34, -247), (34, -247)),
    "skin": ((-64, -220), (64, -220), (0, -300)),
    "hair_style": ((-70, -340), (0, -380), (70, -340)),
    "hair_color": ((-70, -340), (0, -380), (70, -340)),
    "eye_color": ((-34, -247), (34, -247)),
    "freckles": ((-60, -228), (60, -228)),
}
CHIP_W, CHIP_H, CHIP_GAP = 112, 100, 8
TILE, TILE_GAP = 128, 20
TITLE_Y, TILES_Y = 152, 204  # below the top of the chips
PANEL_COLOR = (236, 244, 255)
OPEN_COLOR = style.ACCENT  # as the shop's open tab
SPARKLE_MS = 900
WIDTH = len(CATEGORIES) * (CHIP_W + CHIP_GAP) - CHIP_GAP


def option_name(field: str, value: object) -> str:
    """The button's name, for example `hair_style:bun` or `freckles:yes`."""
    if isinstance(value, bool):
        value = "yes" if value else "no"
    return f"{field}:{value}"


def mirror_look(avatar: Avatar, category: str) -> Avatar:
    """The look shown in the mirror: without the items that hide `category`."""
    hidden = {slot: NOTHING for slot in HIDES[category]}
    if avatar.head in COVERS_THE_HEAD:
        hidden["head"] = NOTHING
    return Avatar(**{**vars(avatar), **hidden})


class LookPicker:
    """The chips, the open chip's choices and the mirror, for the screen that holds them. Its
    top-left corner is the first chip's."""

    def __init__(self, content: Content, left: int, top: int) -> None:
        self.content = content
        self.left, self.top = left, top
        self.category = CATEGORIES[0]
        self.sparkle_ms = 0

    @property
    def index(self) -> int:
        return CATEGORIES.index(self.category)

    @property
    def is_last(self) -> bool:
        return self.index == len(CATEGORIES) - 1

    @property
    def center_x(self) -> int:
        return self.left + WIDTH // 2

    def open(self, category: str) -> None:
        self.category = category

    def next(self) -> None:
        self.category = CATEGORIES[min(self.index + 1, len(CATEGORIES) - 1)]

    def previous(self) -> None:
        self.category = CATEGORIES[max(self.index - 1, 0)]

    def update(self, dt_ms: int) -> None:
        self.sparkle_ms = max(0, self.sparkle_ms - dt_ms)

    # --- Buttons ----------------------------------------------------------------------------

    def buttons(self, avatar: Avatar, changed: Callable[[], None], reopen: Callable[[], None]):
        """The chips (`look:<category>`) and the open chip's choices (`<field>:<value>`). A
        choice changes `avatar` and calls `changed`; a chip calls `reopen` to lay out again."""

        def open_chip(category: str) -> None:
            self.open(category)
            reopen()

        def choose(value: object) -> None:
            setattr(avatar, self.category, value)
            avatar.validate()
            self.sparkle_ms = SPARKLE_MS
            changed()

        buttons = []
        for index, category in enumerate(CATEGORIES):
            rect = pygame.Rect(self.left + index * (CHIP_W + CHIP_GAP), self.top, CHIP_W, CHIP_H)
            buttons.append(
                Button(
                    rect,
                    lambda category=category: open_chip(category),
                    name=f"look:{category}",
                    draw=lambda surface, rect, category=category: self._draw_chip(
                        surface, rect, category
                    ),
                    color=OPEN_COLOR if category == self.category else style.PANEL,
                    radius=24,
                )
            )
        choices = CHOICES[self.category]
        left = self.center_x - (len(choices) * (TILE + TILE_GAP) - TILE_GAP) // 2
        for index, value in enumerate(choices):
            rect = pygame.Rect(left + index * (TILE + TILE_GAP), self.top + TILES_Y, TILE, TILE)
            buttons.append(
                Button(
                    rect,
                    lambda value=value: choose(value),
                    name=option_name(self.category, value),
                    draw=lambda surface, rect, value=value: draw_choice(
                        surface, rect, avatar, self.category, value
                    ),
                    selected=getattr(avatar, self.category) == value,
                    radius=30,
                )
            )
        return buttons

    # --- Drawing ----------------------------------------------------------------------------

    def _draw_chip(self, surface: pygame.Surface, rect: pygame.Rect, category: str) -> None:
        draw_chip(surface, rect, chip_icon(category, 54), self.content.text(WORDS[category]))

    def draw(self, surface: pygame.Surface) -> None:
        """The panel behind the chips, and the title of the open chip over its choices."""
        panel = pygame.Rect(self.left - 8, self.top - 8, WIDTH + 16, CHIP_H + 16)
        paint.draw_box(surface, panel, PANEL_COLOR, 28, lip=False)
        title = self.content.text(WORDS[self.category])
        paint.draw_title_text(surface, title, 52, (self.center_x, self.top + TITLE_Y))

    def draw_mirror(
        self, surface: pygame.Surface, avatar: Avatar, center: tuple[int, int], radius: int
    ) -> None:
        """The mirror, and its sparkles for a moment after a change."""
        look = mirror_look(avatar, self.category)
        sprite = mirror(tuple(vars(look).values()), radius)
        surface.blit(sprite, sprite.get_rect(midtop=(center[0], center[1] - radius - RIM)))
        if self.sparkle_ms:
            grow = math.sin(math.pi * self.sparkle_ms / SPARKLE_MS)
            for part in PARTS[self.category]:
                point = mirror_point(center, radius, part)
                paint.sparkle(surface, point, 8 + 22 * grow, style.OUTLINE)
                paint.sparkle(surface, point, 5 + 18 * grow, style.GOLD)


# --- The choices: each shows what it changes ----------------------------------------------------


def draw_choice(
    surface: pygame.Surface, rect: pygame.Rect, avatar: Avatar, field: str, value: object
) -> None:
    """A choice's picture, on the player's look without the shop's items."""
    preview = Avatar(**{**vars(avatar.bare()), field: value})
    if field == "eye_color":
        sprite = eye_icon(options.EYE_COLORS[str(value)], round(rect.w * 0.78))
        surface.blit(sprite, sprite.get_rect(center=rect.center))
    elif field in ("face", "freckles"):
        surface.blit(close_up(tuple(vars(preview).values()), rect.w), rect.topleft)
    else:
        draw_head(surface, preview, (rect.centerx, rect.centery + 8), rect.w * 0.36)


@lru_cache(maxsize=128)
def close_up(key: tuple, size: int) -> pygame.Surface:
    """The eyes, mouth and cheeks of a look, large, in a circle inside a `size` tile."""
    layer = pygame.Surface((size, size), pygame.SRCALPHA)
    r = size * 0.62
    draw_head(layer, Avatar(*key), (size // 2, round(size / 2 - r * 0.26)), r)
    circle = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(circle, (255, 255, 255, 255), (size // 2, size // 2), size // 2 - 6)
    layer.blit(circle, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return layer


@lru_cache(maxsize=32)
def eye_icon(iris, width: int) -> pygame.Surface:
    """One big eye with an iris of that colour."""
    u = width * K / 100
    big = pygame.Surface((round(100 * u) + 8, round(64 * u) + 8), pygame.SRCALPHA)
    pen = ItemPen(big, u, (big.get_width() / 2, big.get_height() / 2), 3)
    pen.polygon(style.WHITE, oval(0, 0, 46, 28, n=48))
    pen.circle(iris, (0, 0), 22)
    pen.circle(shade(iris, 0.75), (0, 0), 22, outline=False)
    pen.circle(iris, (-1, -1), 18, outline=False)
    pen.circle(style.OUTLINE, (0, 0), 9, outline=False)
    pen.circle(style.WHITE, (-6, -7), 5, outline=False)
    pen.circle(style.WHITE, (7, 7), 2.5, outline=False)
    return paint.finish(big)


# --- The chips' pictures ------------------------------------------------------------------------


@lru_cache(maxsize=32)
def chip_icon(category: str, size: int) -> pygame.Surface:
    """A small picture of what a chip changes, in the art style."""
    u = size * K / 100
    big = pygame.Surface((size * K, size * K), pygame.SRCALPHA)
    pen = ItemPen(big, u, (size * K / 2, size * K / 2), 4)
    ICONS[category](pen)
    return paint.finish(big)


def _smiley(d: ItemPen) -> None:
    d.circle(style.GOLD, (0, 0), 44)
    for x in (-16, 16):
        d.circle(style.OUTLINE, (x, -10), 6, outline=False)
    pygame.draw.arc(d.s, style.OUTLINE, d.rect(-26, -20, 52, 46), math.pi + 0.45, -0.45, d.lw + 2)


def _skins(d: ItemPen) -> None:
    """The skin tones as slices of one round."""
    colors = list(options.SKIN_TONES.values())
    d.circle(style.WHITE, (0, 0), 44)
    for i, color in enumerate(colors):
        start = -math.pi / 2 + i * 2 * math.pi / len(colors)
        end = start + 2 * math.pi / len(colors)
        angles = [start + (end - start) * k / 10 for k in range(11)]
        arc = [(44 * math.cos(a), 44 * math.sin(a)) for a in angles]
        d.polygon(color, [(0, 0), *arc], outline=False)
    pygame.draw.circle(d.s, style.OUTLINE, d.p(0, 0), 44 * d.u + d.lw, d.lw)


def _comb(d: ItemPen) -> None:
    pink = (240, 120, 170)
    for i in range(9):
        x = -36 + i * 9
        d.limb(pink, (x, 22), (x, -2), 5)
    d.rrect(pink, (-44, -26, 88, 26), 10)


def teardrop(cx: float, cy: float, r: float, n: int = 40) -> list[tuple[float, float]]:
    """A drop with its tip up, `r` wide at its round bottom, centred on (cx, cy)."""
    return [
        (cx + r * math.sin(t) * math.sin(t / 2), cy - 1.3 * r * math.cos(t))
        for t in (2 * math.pi * i / n for i in range(n))
    ]


def _drops(d: ItemPen) -> None:
    """Drops of paint in hair colours."""
    for (x, y), color in zip(((-27, 10), (0, -8), (27, 10)), ("red", "blond", "blue"), strict=True):
        d.polygon(options.HAIR_COLORS[color], teardrop(x, y, 19))
        d.circle(style.WHITE, (x - 7, y + 6), 4, outline=False)


def _eye(d: ItemPen) -> None:
    d.polygon(style.WHITE, oval(0, 0, 46, 28, n=48))
    d.circle(options.EYE_COLORS["blue"], (0, 0), 20)
    d.circle(style.OUTLINE, (0, 0), 9, outline=False)
    d.circle(style.WHITE, (-6, -7), 5, outline=False)


def _freckles(d: ItemPen) -> None:
    skin = options.SKIN_TONES["peach"]
    d.circle(skin, (0, 0), 44)
    freckle = shade(paint.mix(skin, (125, 72, 45), 0.4), 0.7)
    for x, y in ((-18, -14), (0, -22), (18, -14), (-26, 6), (-8, 4), (10, 4), (28, 6)):
        d.circle(freckle, (x, y), 5, outline=False)
    for x in (-22, 22):
        d.polygon((240, 125, 120), oval(x, 24, 12, 6), outline=False)


ICONS: dict[str, Callable[[ItemPen], None]] = {
    "face": _smiley,
    "skin": _skins,
    "hair_style": _comb,
    "hair_color": _drops,
    "eye_color": _eye,
    "freckles": _freckles,
}


# --- The mirror ---------------------------------------------------------------------------------

RIM = 14  # the mirror's golden rim
HANDLE = 90  # how far its handle reaches under the glass
GLASS = (222, 240, 252)
FACE_SHARE = 0.56  # the face's radius, as a share of the mirror's
HEAD_DROP = 0.08  # the head sits a little low, to leave room for a hat


def mirror_scale(radius: int) -> float:
    """Pixels per avatar unit in a mirror of `radius`."""
    return radius * FACE_SHARE / HEAD_R


def mirror_point(center: tuple[int, int], radius: int, part: tuple[float, float]):
    """Where a point of the head (avatar units) shows in the mirror."""
    u = mirror_scale(radius)
    x, y = part
    return (
        round(center[0] + (x - HEAD_CENTER[0]) * u),
        round(center[1] + radius * HEAD_DROP + (y - HEAD_CENTER[1]) * u),
    )


@lru_cache(maxsize=32)
def mirror(key: tuple, radius: int) -> pygame.Surface:
    """A round hand mirror showing the head and shoulders of a look: glass, golden rim, handle."""
    side = 2 * (radius + RIM)
    sprite = pygame.Surface((side, side + HANDLE), pygame.SRCALPHA)
    c = side // 2
    handle = pygame.Rect(0, 0, 44, HANDLE + RIM * 2)
    handle.midtop = (c, side - RIM * 3)
    pygame.draw.rect(sprite, style.OUTLINE, handle.inflate(8, 8), border_radius=22)
    pygame.draw.rect(sprite, style.GOLD, handle, border_radius=20)
    pygame.draw.rect(
        sprite, shade(style.GOLD, 0.85), handle.move(14, 0).clip(handle), border_radius=20
    )
    glass = pygame.Surface((2 * radius, 2 * radius), pygame.SRCALPHA)
    glass.fill(GLASS)
    draw_bust(glass, Avatar(*key), (radius, round(radius * (1 + HEAD_DROP))), radius * FACE_SHARE)
    circle = pygame.Surface(glass.get_size(), pygame.SRCALPHA)
    pygame.draw.circle(circle, (255, 255, 255, 255), (radius, radius), radius)
    glass.blit(circle, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    pygame.draw.circle(sprite, style.OUTLINE, (c, c), radius + RIM + 3)
    pygame.draw.circle(sprite, style.GOLD, (c, c), radius + RIM)
    pygame.draw.circle(sprite, style.OUTLINE, (c, c), radius + 3)
    sprite.blit(glass, (c - radius, c - radius))
    shine = pygame.Surface(sprite.get_size(), pygame.SRCALPHA)
    pygame.draw.arc(
        shine, (255, 255, 255, 150), (c - radius + 14, c - radius + 14, 2 * radius - 28,
        2 * radius - 28), 1.95, 2.75, 10,
    )  # fmt: skip
    sprite.blit(shine, (0, 0))
    return sprite
