"""The on-screen keyboard: the rows of the real keyboard (from the content), each key showing its
capital and small letter, plus the drawn keyboard icon of the button that hides it."""

from collections.abc import Sequence
from functools import lru_cache

import pygame

from edugames.ui import style

KEY_H = style.MIN_TARGET
MAX_KEY_W = 104
GAP = 10
SIDE = 40  # the least room on each side of the widest row
BOTTOM = 24  # room under the last row
STAGGER = (0.0, 0.3, 0.8, 1.3)  # how far each row starts to the right, in keys (as on a real one)
MUTED_KEY = (226, 229, 239)


def keyboard_top(row_count: int) -> int:
    return style.HEIGHT - BOTTOM - row_count * KEY_H - (row_count - 1) * GAP


def key_rects(rows: Sequence[Sequence[str]]) -> dict[str, pygame.Rect]:
    """Where each key goes: staggered rows at the bottom of the screen, centred."""
    stagger = [STAGGER[min(i, len(STAGGER) - 1)] for i in range(len(rows))]
    units = max(offset + len(row) for offset, row in zip(stagger, rows, strict=True))
    key_w = min(MAX_KEY_W, int((style.WIDTH - 2 * SIDE + GAP) / units) - GAP)
    step = key_w + GAP
    left = (style.WIDTH - (units * step - GAP)) / 2
    top = keyboard_top(len(rows))
    rects = {}
    for index, (offset, row) in enumerate(zip(stagger, rows, strict=True)):
        y = top + index * (KEY_H + GAP)
        for col, letter in enumerate(row):
            rects[letter] = pygame.Rect(round(left + (offset + col) * step), y, key_w, KEY_H)
    return rects


@lru_cache(maxsize=256)
def key_label(upper: str, lower: str, color: tuple[int, int, int], size: int) -> pygame.Surface:
    """The capital and the small letter side by side ("Aa"), in Andika."""
    return style.font(size, True).render(upper + lower, True, color)


def draw_key_label(
    surface: pygame.Surface, rect: pygame.Rect, upper: str, lower: str, color, size: int = 46
) -> None:
    label = key_label(upper, lower, tuple(color), size)
    surface.blit(label, label.get_rect(center=(rect.centerx, rect.centery - 3)))


def draw_keyboard_icon(surface: pygame.Surface, center: tuple[int, int], shown: bool) -> None:
    """A little keyboard, with an arrow that says what the button does: down hides it, up shows
    it."""
    cx, cy = center
    body = pygame.Rect(0, 0, 76, 44)
    body.center = (cx, cy - 10)
    pygame.draw.rect(surface, style.OUTLINE, body.inflate(6, 6), border_radius=10)
    pygame.draw.rect(surface, style.WHITE, body, border_radius=8)
    for row, (count, shift) in enumerate(((6, 0), (5, 5), (4, 10))):
        for col in range(count):
            key = pygame.Rect(body.left + 6 + shift + col * 11, body.top + 6 + row * 11, 8, 8)
            if row == 2 and col == 1:
                key.w = 30  # the space bar
            pygame.draw.rect(surface, style.OUTLINE, key, border_radius=2)
            if row == 2 and col == 1:
                break
    tip = cy + 34 if shown else cy + 20
    base = cy + 20 if shown else cy + 34
    pygame.draw.polygon(surface, style.OUTLINE, [(cx - 12, base), (cx + 12, base), (cx, tip)])
