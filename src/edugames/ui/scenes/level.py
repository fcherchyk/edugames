"""What every game level shares: its scenery, the victory pop-up when it is won (with the shop's
items the win has opened), the next level and the way back to the path."""

import pygame

from edugames.core import progress, shop
from edugames.core.avatar import Item
from edugames.core.content import Level
from edugames.core.progress import Win
from edugames.ui import paint, style
from edugames.ui.avatar_draw import draw_avatar
from edugames.ui.items_draw import draw_item_icon
from edugames.ui.scenes.base import Scene
from edugames.ui.widgets import Button, draw_coin, draw_stars, draw_text

PANEL = pygame.Rect(0, 0, 900, 640)
PANEL.center = (style.WIDTH // 2, style.HEIGHT // 2)
VICTORY_AVATAR = (PANEL.left + 200, PANEL.top + 270), 340  # centre and height
NEW_ITEMS_CENTER = (PANEL.left + 590, PANEL.top + 368)  # "New in the shop!"


class LevelScene(Scene):
    """A level of a game. Subclasses set up their game in `start`, and lay out and draw it in
    `layout_play` and `draw_play`; they call `finish(stars)` when the level is won."""

    def __init__(self, app, game_id: str, level_id: str) -> None:
        self.game_id = game_id
        self.level: Level = app.content.level(game_id, level_id)
        self.theme = self.level.theme
        self.win: Win | None = None
        self.new_items: list[Item] = []  # opened in the shop by this win
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
        y = 630 if self.new_items else 610
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
        before = shop.open_items(self.profile, self.content.levels)
        self.win = progress.record_win(self.profile, self.game_id, self.level.id, stars)
        self.new_items = shop.newly_opened(
            before, shop.open_items(self.profile, self.content.levels)
        )
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
        panel = PANEL
        paint.draw_box(surface, panel, style.WHITE, 48, ring=style.GOLD)
        draw_avatar(surface, self.profile.avatar, *VICTORY_AVATAR, celebrating=True)
        right = panel.left + 590
        rows = (85, 200, 305) if self.new_items else (100, 235, 370)  # title, stars, coins
        paint.draw_title_text(
            surface, self.content.text("you_did_it"), 76, (right, panel.top + rows[0])
        )
        draw_stars(surface, win.stars, (right, panel.top + rows[1]), 90 if self.new_items else 100)
        label = self.content.text("plus_coins", coins=win.coins)
        text = draw_text(
            surface, label, 56, (right + 30, panel.top + rows[2]), style.OUTLINE, title=True
        )
        draw_coin(surface, (text.left - 40, text.centery), 26)
        if self.new_items:
            self._draw_new_items(surface, NEW_ITEMS_CENTER)

    def _draw_new_items(self, surface: pygame.Surface, top: tuple[int, int]) -> None:
        """ "New in the shop!" over the items this win has opened, each on a small tile."""
        tiles = new_item_tiles(len(self.new_items))
        x = (tiles[0].left + tiles[-1].right) // 2  # over the row of tiles
        draw_text(
            surface, self.content.text("new_in_shop"), 36, (x, top[1]), style.OUTLINE, title=True
        )
        for item, tile in zip(self.new_items, tiles, strict=True):
            paint.draw_box(surface, tile, style.PANEL, 22, lip=False)
            draw_item_icon(surface, item.id, tile.center, round(tile.w * 0.8))


def new_item_tiles(count: int) -> list[pygame.Rect]:
    """Where the victory pop-up shows the items a win opened: a row under "New in the shop!",
    right of the avatar and its pet."""
    size, gap = (96, 20) if count <= 3 else (84, 14)  # a world opens up to 4 items
    x = NEW_ITEMS_CENTER[0] + (0 if count <= 3 else 20)
    left = x - (count * (size + gap) - gap) // 2
    return [
        pygame.Rect(left + i * (size + gap), NEW_ITEMS_CENTER[1] + 28, size, size)
        for i in range(count)
    ]
