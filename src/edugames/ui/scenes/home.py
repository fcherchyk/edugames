"""Home: the player's avatar and coins, and the games for their age."""

import pygame

from edugames.core.content import Game
from edugames.ui import style
from edugames.ui.avatar_draw import draw_avatar
from edugames.ui.scenes.base import MARGIN, Scene
from edugames.ui.widgets import Button, draw_padlock, draw_text, name_tag

TILE_W, TILE_H = 360, 250


class HomeScene(Scene):
    def layout(self) -> None:
        self.buttons = [self.back_button(self.content.text("players"), self.to_players)]
        wardrobe = pygame.Rect(MARGIN + 40, style.HEIGHT - 150, 280, style.MIN_TARGET)
        self.buttons.append(
            Button(wardrobe, self.to_wardrobe, label=self.content.text("wardrobe"), name="wardrobe")
        )
        for index, game in enumerate(self.content.games_for_age(self.profile.age)):
            row, col = divmod(index, 2)
            rect = pygame.Rect(440 + col * (TILE_W + 40), 170 + row * (TILE_H + 40), TILE_W, TILE_H)
            self.buttons.append(
                Button(
                    rect,
                    lambda game=game: self.open_game(game),
                    name=f"game:{game.id}",
                    draw=lambda surface, rect, game=game: self._draw_game(surface, rect, game),
                    color=style.PANEL if game.playable else style.LOCKED,
                    enabled=game.playable,
                )
            )

    def _draw_game(self, surface: pygame.Surface, rect: pygame.Rect, game: Game) -> None:
        ink = style.INK if game.playable else style.MUTED
        icon = style.CONSONANT if game.playable else ink
        draw_text(surface, game.icon, 110, (rect.centerx, rect.centery - 30), icon, bold=True)
        draw_text(surface, game.title, 38, (rect.centerx, rect.bottom - 60), ink, title=True)
        if not game.playable:
            draw_padlock(surface, (rect.right - 45, rect.top + 45), 40)
            draw_text(
                surface,
                self.content.text("coming_soon"),
                28,
                (rect.centerx, rect.bottom - 25),
                style.MUTED,
                title=True,
            )

    def open_game(self, game: Game) -> None:
        from edugames.ui.scenes.path import PathScene

        self.app.go(PathScene(self.app, game.id))

    def to_players(self) -> None:
        from edugames.ui.scenes.profiles import ProfileSelectScene

        self.app.profile = None
        self.app.go(ProfileSelectScene(self.app))

    def to_wardrobe(self) -> None:
        from edugames.ui.scenes.wardrobe import WardrobeScene

        self.app.go(WardrobeScene(self.app))

    def draw_scene(self, surface: pygame.Surface) -> None:
        draw_avatar(surface, self.profile.avatar, (210, 470), 380)
        name_tag(surface, self.profile.name, (210, 235))
        self.draw_coin_count(surface)
