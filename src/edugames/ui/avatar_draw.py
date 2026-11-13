"""The avatar: a chibi kid drawn with shapes (navy outline, one cel shade), so that any colour can
change without image files, wearing the items bought in the shop (`ui/items_draw.py`). Each look
is drawn once per size and cached."""

import math
from functools import lru_cache

import pygame

from edugames.core.avatar import EYE_COLORS, HAIR_COLORS, SHIRT_COLORS, SKIN_TONES, Avatar
from edugames.ui import paint, style
from edugames.ui.items_draw import ITEMS_FRAME, UNDER_THE_EYES, ItemPen, draw_item
from edugames.ui.paint import K, shade

NAVY = style.OUTLINE
PANTS = (60, 70, 140)
SHOES = (240, 80, 70)
FRECKLE = (125, 72, 45)
FRECKLE_SPOTS = ((44, -232), (58, -236), (72, -229), (52, -222), (66, -220), (80, -222))
BLUSH = (240, 125, 120)
MOUTH = (125, 30, 50)
TONGUE = (240, 110, 120)
OUTLINE_W = 4  # in figure units

# The figure is drawn in "units" with the feet at (0, 0): about 400 units tall.
FIGURE = (-150, -425, 150, 20)  # left, top, right, bottom
HEAD = (-128, -418, 128, -138)  # the part shown by draw_head
BUST = (-215, -530, 215, -60)  # the head and shoulders, with a hat and wings: draw_bust
HEAD_CENTER, HEAD_R = (0, -268), 104


def draw_avatar(
    surface: pygame.Surface,
    avatar: Avatar,
    center: tuple[int, int],
    height: int,
    celebrating: bool = False,
) -> None:
    """The whole figure, `height` pixels tall, centred on `center`; arms up when celebrating.
    Items (wings, a tall hat) may reach outside that box: the body keeps its size and place."""
    height = max(8, height)
    sprite = sprite_for(_key(avatar), height, celebrating, ITEMS_FRAME)
    u = height / (FIGURE[3] - FIGURE[1])
    left = center[0] - ((FIGURE[0] + FIGURE[2]) / 2 - ITEMS_FRAME[0]) * u
    top = center[1] - ((FIGURE[1] + FIGURE[3]) / 2 - ITEMS_FRAME[1]) * u
    surface.blit(sprite, (round(left), round(top)))


def draw_head(surface: pygame.Surface, avatar: Avatar, center: tuple[int, int], r: float) -> None:
    """Only the head, with a face radius of about `r` pixels, centred on `center`."""
    height = round(r * (FIGURE[3] - FIGURE[1]) / HEAD_R)
    sprite = sprite_for(_key(avatar), max(8, height), False, HEAD)
    u = r / HEAD_R
    offset_y = ((HEAD[1] + HEAD[3]) / 2 - HEAD_CENTER[1]) * u
    surface.blit(sprite, sprite.get_rect(center=(center[0], round(center[1] + offset_y))))


def draw_bust(surface: pygame.Surface, avatar: Avatar, center: tuple[int, int], r: float) -> None:
    """The head and shoulders with the items worn there (for the mirror), the face's centre on
    `center` with a radius of about `r` pixels."""
    height = round(r * (FIGURE[3] - FIGURE[1]) / HEAD_R)
    sprite = sprite_for(_key(avatar), max(8, height), False, BUST)
    u = r / HEAD_R
    left = center[0] - (HEAD_CENTER[0] - BUST[0]) * u
    top = center[1] - (HEAD_CENTER[1] - BUST[1]) * u
    surface.blit(sprite, (round(left), round(top)))


def _key(avatar: Avatar) -> tuple[str, ...]:
    return tuple(vars(avatar).values())


@lru_cache(maxsize=256)
def sprite_for(
    key: tuple[str, ...],
    height: int,
    celebrating: bool,
    frame: tuple[int, int, int, int],
) -> pygame.Surface:
    """The part of the figure inside `frame`, for a figure `height` pixels tall."""
    left, top, right, bottom = frame
    u = height * K / (FIGURE[3] - FIGURE[1])
    big = pygame.Surface((round((right - left) * u), round((bottom - top) * u)), pygame.SRCALPHA)
    _Figure(big, u, (-left * u, -top * u), OUTLINE_W).draw(Avatar(*key), celebrating)
    return paint.finish(big)


class _Figure(ItemPen):
    """Draws the avatar in figure units onto a supersampled surface."""

    def draw(self, avatar: Avatar, celebrating: bool) -> None:
        skin = SKIN_TONES[avatar.skin]
        hair = HAIR_COLORS[avatar.hair_color]
        shirt = SHIRT_COLORS[avatar.shirt].rgb
        shadow = pygame.Surface((round(150 * self.u), round(30 * self.u)), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (20, 40, 20, 70), shadow.get_rect())
        self.s.blit(shadow, self.p(-75, -14))
        draw_item(self, avatar.back)
        if avatar.hair_style == "long":
            self.rrect(hair, (-112, -300, 224, 160), 60)
        for d in (-1, 1):
            self.rrect(PANTS, (d * 22 - 15, -70, 30, 56), 10)
            if not avatar.feet:  # its own red shoes, unless it wears shoes from the shop
                self.ellipse(SHOES, (d * 26 - 26, -26, 52, 28))
        draw_item(self, avatar.feet)
        arms = [
            ((d * 46, -150), (d * 104, -268) if celebrating else (d * 74, -78)) for d in (-1, 1)
        ]
        if celebrating:
            self._arms(arms, shirt, skin)
        self._body(shirt)
        if not celebrating:
            self._arms(arms, shirt, skin)
        self._head(avatar, skin, hair, celebrating)
        draw_item(self, avatar.pet)  # beside the avatar, in front of everything

    def _arms(self, arms, shirt, skin) -> None:
        for shoulder, hand in arms:
            self.limb(shirt, shoulder, hand, 28)
            self.circle(skin, hand, 17)

    def _body(self, shirt) -> None:
        body = (-58, -168, 116, 112)
        self.rrect(shirt, body, 38)
        old = self.s.get_clip()
        self.s.set_clip(self.rect(18, -168, 60, 112))
        pygame.draw.rect(
            self.s, shade(shirt, 0.82), self.rect(*body), border_radius=round(38 * self.u)
        )
        self.s.set_clip(old)
        self.polygon(style.WHITE, [(-26, -166), (0, -138), (26, -166)])
        badge = paint.star_points((0, -110), 16)
        self.polygon(style.GOLD, badge)

    def _head(self, avatar: Avatar, skin, hair, celebrating: bool) -> None:
        style_ = avatar.hair_style
        if style_ == "bun":
            self.circle(hair, (0, -380), 40)
        if style_ != "spiky":
            self.circle(hair, HEAD_CENTER, HEAD_R)
        for d in (-1, 1):
            self.circle(skin, (d * 94, -250), 20)
        self.circle(shade(skin, 0.84), (0, -258), 96)  # the cel shade, seen as a crescent
        pygame.draw.circle(self.s, skin, self.p(-9, -260), 87 * self.u)
        self._hair(style_, hair)
        if avatar.eyes in UNDER_THE_EYES:
            draw_item(self, avatar.eyes)
        self._face(avatar, skin, celebrating)
        if avatar.eyes not in UNDER_THE_EYES:
            draw_item(self, avatar.eyes)
        draw_item(self, avatar.head)

    def _hair(self, style_: str, hair) -> None:
        light = paint.mix(hair, style.WHITE, 0.45)
        if style_ == "spiky":
            spikes = [(-104, -262), (-118, -330), (-80, -322), (-74, -392), (-34, -350), (0, -410),
                      (34, -350), (74, -392), (80, -322), (118, -330), (104, -262), (70, -300),
                      (0, -312), (-70, -300)]  # fmt: skip
            self.polygon(hair, spikes)
            pygame.draw.line(self.s, light, self.p(-44, -340), self.p(-60, -372), round(6 * self.u))
            return
        if style_ == "curly":
            curls = [(-92, -300, 30), (-70, -338, 32), (-30, -362, 34), (14, -366, 34),
                     (56, -350, 32), (88, -318, 30), (102, -280, 24), (-104, -270, 22)]  # fmt: skip
        else:  # short, long, bun: a soft fringe
            curls = [(-66, -312, 40), (-24, -336, 44), (24, -336, 44), (66, -312, 40),
                     (88, -282, 24), (-88, -282, 24)]  # fmt: skip
        self.blobs(hair, curls)
        pygame.draw.arc(self.s, light, self.rect(-70, -360, 70, 50), 1.9, 2.9, round(7 * self.u))
        pygame.draw.arc(self.s, light, self.rect(10, -372, 50, 40), 1.9, 2.9, round(6 * self.u))

    def _face(self, avatar: Avatar, skin, celebrating: bool) -> None:
        face = avatar.face
        if avatar.freckles:
            freckle = shade(paint.mix(skin, FRECKLE, 0.4), 0.7)  # visible on every skin
            for d in (-1, 1):
                for x, y in FRECKLE_SPOTS:
                    pygame.draw.circle(self.s, freckle, self.p(d * x, y), 4.2 * self.u)
        for d in (-1, 1):
            ex = d * 34
            if celebrating or (face == "wink" and d == 1):
                pygame.draw.arc(
                    self.s,
                    NAVY,
                    self.rect(ex - 16, -262, 32, 28),
                    0.25,
                    math.pi - 0.25,
                    round(6 * self.u),
                )
            else:
                iris = 10 if face == "calm" else 12
                self.ellipse(style.WHITE, (ex - 17, -268, 34, 42), outline=True)
                iris_box = self.rect(ex - iris + d * 2, -258, iris * 2, 30)
                pygame.draw.ellipse(self.s, EYE_COLORS[avatar.eye_color], iris_box)
                pygame.draw.ellipse(self.s, NAVY, self.rect(ex - 7 + d * 2, -250, 14, 18))
                pygame.draw.circle(self.s, style.WHITE, self.p(ex - 3 + d * 2, -252), 6 * self.u)
                pygame.draw.circle(self.s, style.WHITE, self.p(ex + 5 + d * 2, -238), 3 * self.u)
            pygame.draw.ellipse(self.s, BLUSH, self.rect(d * 60 - 15, -218, 30, 15))
        if celebrating or face == "grin":
            pts = [
                (26 * math.cos(a / 12 * math.pi), -214 + 34 * math.sin(a / 12 * math.pi))
                for a in range(13)
            ]
            pygame.draw.polygon(self.s, MOUTH, [self.p(*q) for q in pts])
            pygame.draw.ellipse(self.s, TONGUE, self.rect(-14, -196, 28, 16))
            pygame.draw.rect(self.s, style.WHITE, self.rect(-18, -214, 36, 7))
            pygame.draw.polygon(self.s, NAVY, [self.p(*q) for q in pts], round(4 * self.u))
        elif face == "calm":
            pygame.draw.arc(
                self.s,
                NAVY,
                self.rect(-18, -226, 36, 24),
                math.pi + 0.4,
                2 * math.pi - 0.4,
                round(5 * self.u),
            )
        else:  # smile, wink: a small open smile
            pts = [
                (16 * math.cos(a / 8 * math.pi), -208 + 12 * math.sin(a / 8 * math.pi))
                for a in range(9)
            ]
            pygame.draw.polygon(self.s, MOUTH, [self.p(*q) for q in pts])
            pygame.draw.polygon(self.s, NAVY, [self.p(*q) for q in pts], round(3 * self.u))
