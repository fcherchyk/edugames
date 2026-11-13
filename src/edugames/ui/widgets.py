"""Buttons and the small drawings every screen uses (text, stars, coins, padlock)."""

from collections.abc import Callable

import pygame

from edugames.ui import paint, style

Point = tuple[int, int]


def draw_text(
    surface: pygame.Surface,
    text: str,
    size: int,
    center: Point,
    color: tuple[int, int, int] = style.INK,
    bold: bool = False,
    title: bool = False,
) -> pygame.Rect:
    """Andika text (letters and names), or Fredoka when `title` (labels and numbers)."""
    font = style.title_font(size) if title else style.font(size, bold)
    image = font.render(text, True, color)
    rect = image.get_rect(center=center)
    surface.blit(image, rect)
    return rect


def draw_stars(
    surface: pygame.Surface, count: int, center: Point, size: int, total: int = 3
) -> None:
    """`total` stars in a row, the first `count` glossy gold; the middle one of three is bigger."""
    cx, cy = center
    gap = size * 1.15
    for i in range(total):
        big = total == 3 and i == 1
        sprite = paint.star(round(size * 1.25) if big else size, i < count)
        x = cx + (i - (total - 1) / 2) * gap
        y = cy - (size * 0.12 if big else 0)
        surface.blit(sprite, sprite.get_rect(center=(round(x), round(y))))


def draw_coin(surface: pygame.Surface, center: Point, radius: int) -> None:
    sprite = paint.coin(radius)
    surface.blit(sprite, sprite.get_rect(center=center))


def draw_coins(surface: pygame.Surface, coins: int, center: Point, size: int = 40) -> None:
    """A white tag with a coin and how many there are."""
    cx, cy = center
    tag = pygame.Rect(0, 0, size * 4, round(size * 1.6))
    tag.center = (cx, cy)
    paint.draw_box(surface, tag, style.WHITE, tag.h // 2, lip=False)
    draw_coin(surface, (tag.left + round(size * 0.85), cy), round(size * 0.5))
    draw_text(surface, str(coins), size, (cx + size // 2, cy), style.OUTLINE, title=True)


def draw_padlock(surface: pygame.Surface, center: Point, size: int) -> None:
    cx, cy = center
    body = pygame.Rect(0, 0, size, size * 0.75)
    body.center = (cx, round(cy + size * 0.2))
    shackle = pygame.Rect(0, 0, size * 0.65, size * 0.8)
    shackle.midbottom = (cx, body.top + size * 0.3)
    width = max(3, size // 8)
    pygame.draw.ellipse(surface, style.OUTLINE, shackle.inflate(4, 4), width + 4)
    pygame.draw.ellipse(surface, style.MUTED, shackle, width)
    pygame.draw.rect(surface, style.OUTLINE, body.inflate(6, 6), border_radius=size // 5)
    pygame.draw.rect(surface, (180, 182, 205), body, border_radius=size // 6)
    pygame.draw.circle(surface, style.OUTLINE, body.center, max(3, size // 10))


class Button:
    """A tappable area: the mouse (and touch, which SDL turns into mouse events) release inside it
    calls `on_click`. Drawn as a rounded box with a lip; `primary` makes it the glossy green pill
    of main actions, `selected` gives it a gold ring."""

    def __init__(
        self,
        rect: pygame.Rect,
        on_click: Callable[[], None],
        *,
        label: str = "",
        name: str = "",
        draw: Callable[[pygame.Surface, pygame.Rect], None] | None = None,
        color: tuple[int, int, int] = style.PANEL,
        enabled: bool = True,
        selected: bool = False,
        primary: bool = False,
        ring: tuple[int, int, int] | None = None,
        radius: int | None = None,
        label_size: int = 40,
    ) -> None:
        self.rect = rect
        self.on_click = on_click
        self.label = label
        self.name = name or label
        self.draw_content = draw
        self.primary = primary
        self.color = style.PRIMARY if primary else color
        self.enabled = enabled
        self.selected = selected
        self.ring = ring
        self.radius = radius
        self.label_size = label_size

    def handle(self, event: pygame.event.Event) -> bool:
        clicked = (
            event.type == pygame.MOUSEBUTTONUP
            and event.button == 1
            and self.enabled
            and self.rect.collidepoint(event.pos)
        )
        if clicked:
            self.on_click()
        return clicked

    def draw(self, surface: pygame.Surface) -> None:
        w, h = self.rect.size
        pill = h <= style.MIN_TARGET + 10
        radius = self.radius if self.radius is not None else h // 2 if pill else min(w, h) // 5
        color = self.color if self.enabled else style.LOCKED
        ring = style.GOLD if self.selected else self.ring
        paint.draw_box(
            surface, self.rect, color, radius, gloss=self.primary and self.enabled, ring=ring
        )
        if self.draw_content:
            self.draw_content(surface, self.rect)
        if self.label:
            center = (self.rect.centerx, self.rect.centery - 2)
            if self.primary and self.enabled:
                paint.draw_title_text(
                    surface,
                    self.label,
                    self.label_size,
                    center,
                    outline=paint.shade(color, 0.55),
                    depth=3,
                )
            else:
                ink = style.OUTLINE if self.enabled else style.MUTED
                draw_text(surface, self.label, self.label_size, center, ink, title=True)


def name_tag(surface: pygame.Surface, name: str, center: Point, size: int = 44) -> None:
    """A player's name on a white tag, readable over any scenery."""
    width = style.font(size, True).size(name)[0] + size * 2
    tag = pygame.Rect(0, 0, max(width, size * 4), round(size * 1.7))
    tag.center = center
    paint.draw_box(surface, tag, style.WHITE, tag.h // 2, lip=False)
    draw_text(surface, name, size, center, bold=True)


def fitting_size(text: str, width: int, size: int) -> int:
    """The largest title font size up to `size` at which `text` fits in `width` pixels."""
    while size > 12 and style.title_font(size).size(text)[0] > width:
        size -= 1
    return size


CHIP_PICTURE_Y = 38  # the picture's centre, from the chip's top; the word sits at the bottom


def draw_chip(
    surface: pygame.Surface, rect: pygame.Rect, picture: pygame.Surface, word: str
) -> None:
    """What a chip shows (a choice of kind, not a thing to buy): a picture, and its word under
    it, in a size that fits."""
    surface.blit(picture, picture.get_rect(center=(rect.centerx, rect.top + CHIP_PICTURE_Y)))
    size = fitting_size(word, rect.w - 14, 22)
    draw_text(surface, word, size, (rect.centerx, rect.bottom - 20), title=True)
