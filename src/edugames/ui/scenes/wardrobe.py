"""The wardrobe: shirt colours, bought with coins and worn by the avatar."""

import pygame

from edugames.core.avatar import SHIRT_COLORS
from edugames.ui import paint, style
from edugames.ui.avatar_draw import draw_avatar
from edugames.ui.scenes.base import Scene
from edugames.ui.widgets import Button, draw_coin, draw_text

SWATCH = 160


class WardrobeScene(Scene):
    def layout(self) -> None:
        self.buttons = [self.back_button(self.content.text("home"), self.to_home)]
        for index, color in enumerate(SHIRT_COLORS):
            row, col = divmod(index, 4)
            rect = pygame.Rect(500 + col * (SWATCH + 30), 190 + row * (SWATCH + 90), SWATCH, SWATCH)
            owned = self.profile.owns_shirt(color)
            self.buttons.append(
                Button(
                    rect,
                    lambda color=color: self.choose(color),
                    name=f"shirt:{color}",
                    draw=lambda surface, rect, color=color: self._draw_swatch(surface, rect, color),
                    enabled=owned or self.profile.can_buy_shirt(color),
                    selected=self.profile.avatar.shirt == color,
                )
            )

    def _draw_swatch(self, surface: pygame.Surface, rect: pygame.Rect, color: str) -> None:
        draw_shirt(surface, SHIRT_COLORS[color].rgb, rect.center, rect.w * 0.7)
        if not self.profile.owns_shirt(color):
            tag = pygame.Rect(0, 0, 110, 56)
            tag.center = (rect.centerx, rect.bottom + 44)
            paint.draw_box(surface, tag, style.WHITE, 28, lip=False)
            draw_coin(surface, (tag.left + 30, tag.centery), 16)
            price = str(SHIRT_COLORS[color].price)
            draw_text(surface, price, 36, (tag.centerx + 18, tag.centery), title=True)

    def choose(self, color: str) -> None:
        if not self.profile.owns_shirt(color):
            self.profile.buy_shirt(color)
        self.profile.wear_shirt(color)
        self.app.save()
        self.layout()

    def to_home(self) -> None:
        from edugames.ui.scenes.home import HomeScene

        self.app.go(HomeScene(self.app))

    def draw_scene(self, surface: pygame.Surface) -> None:
        self.draw_title(surface, self.content.text("wardrobe"))
        self.draw_coin_count(surface)
        draw_avatar(surface, self.profile.avatar, (240, 450), 440)


def draw_shirt(surface: pygame.Surface, rgb, center: tuple[int, int], width: float) -> None:
    """A T-shirt shape with a navy outline and a cel shade on its right side."""
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
