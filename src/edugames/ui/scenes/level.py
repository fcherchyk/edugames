"""What every game level shares: its scenery, the victory pop-up when it is won, the next level
and the way back to the path."""

import pygame

from edugames.core import progress
from edugames.core.content import Level
from edugames.core.progress import Win
from edugames.ui import paint, style
from edugames.ui.avatar_draw import draw_avatar
from edugames.ui.scenes.base import Scene
from edugames.ui.widgets import Button, draw_coin, draw_stars, draw_text


class LevelScene(Scene):
    """A level of a game. Subclasses set up their game in `start`, and lay out and draw it in
    `layout_play` and `draw_play`; they call `finish(stars)` when the level is won."""

    def __init__(self, app, game_id: str, level_id: str) -> None:
        self.game_id = game_id
        self.level: Level = app.content.level(game_id, level_id)
        self.theme = self.level.theme
        self.win: Win | None = None
        self.app = app
        self.start()
        super().__init__(app)

    def start(self) -> None:
        """Set up the game (before the first layout)."""

    @property
    def next_level_id(self) -> str | None:
        ids = [level.id for level in self.content.levels[self.game_id]]
        position = ids.index(self.level.id)
        return ids[position + 1] if position + 1 < len(ids) else None

    def layout(self) -> None:
        if self.win:
            self._layout_victory()
        else:
            self.buttons = [self.back_button(self.content.text("path"), self.to_path)]
            self.layout_play()

    def layout_play(self) -> None:
        pass

    def _layout_victory(self) -> None:
        self.buttons = []
        y = 610
        if self.next_level_id:
            rect = pygame.Rect(0, 0, 320, style.MIN_TARGET)
            rect.center = (style.WIDTH // 2 + 180, y)
            self.buttons.append(
                Button(
                    rect,
                    self.to_next_level,
                    label=self.content.text("next_level"),
                    name="next_level",
                    primary=True,
                )
            )
        rect = pygame.Rect(0, 0, 260, style.MIN_TARGET)
        rect.center = (style.WIDTH // 2 - (180 if self.next_level_id else 0), y)
        self.buttons.append(
            Button(rect, self.to_path, label=self.content.text("path"), name="path")
        )

    def finish(self, stars: int) -> None:
        """The level is won: keep the stars, add the coins, save, and show the pop-up."""
        self.win = progress.record_win(self.profile, self.game_id, self.level.id, stars)
        self.app.save()
        self.layout()

    def leave(self) -> None:
        """Called when the child leaves the level (to the path or the next level)."""

    def to_path(self) -> None:
        from edugames.ui.scenes.path import PathScene

        self.leave()
        self.app.go(PathScene(self.app, self.game_id))

    def to_next_level(self) -> None:
        from edugames.ui.scenes import level_scene

        assert self.next_level_id is not None
        self.leave()
        self.app.go(level_scene(self.app, self.game_id, self.next_level_id))

    def draw_scene(self, surface: pygame.Surface) -> None:
        if self.win:
            self.draw_play(surface)
            self._draw_victory(surface, self.win)
            return
        self.draw_play(surface)
        self.draw_title(surface, self.content.text("level", number=self.level.id))
        self.draw_coin_count(surface)

    def draw_play(self, surface: pygame.Surface) -> None:
        pass

    def _draw_victory(self, surface: pygame.Surface, win: Win) -> None:
        dim = pygame.Surface(style.SIZE, pygame.SRCALPHA)
        dim.fill(style.DIM)
        surface.blit(dim, (0, 0))
        panel = pygame.Rect(0, 0, 900, 640)
        panel.center = (style.WIDTH // 2, style.HEIGHT // 2)
        paint.draw_box(surface, panel, style.WHITE, 48, ring=style.GOLD)
        draw_avatar(
            surface, self.profile.avatar, (panel.left + 200, panel.top + 250), 360, celebrating=True
        )
        right = panel.left + 590
        paint.draw_title_text(
            surface, self.content.text("you_did_it"), 76, (right, panel.top + 100)
        )
        draw_stars(surface, win.stars, (right, panel.top + 235), 100)
        label = self.content.text("plus_coins", coins=win.coins)
        text = draw_text(
            surface, label, 56, (right + 30, panel.top + 370), style.OUTLINE, title=True
        )
        draw_coin(surface, (text.left - 40, text.centery), 26)
