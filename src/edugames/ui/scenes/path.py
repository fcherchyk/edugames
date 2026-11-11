"""The goal path: the memory game's levels in a row, each opened by winning the one before."""

import pygame

from edugames.core import progress
from edugames.ui import style
from edugames.ui.avatar_draw import draw_avatar
from edugames.ui.scenery import icon, theme
from edugames.ui.scenes.base import Scene
from edugames.ui.widgets import Button, draw_padlock, draw_stars

NODE = 130
ROAD = (246, 228, 180)


def node_center(index: int, count: int) -> tuple[int, int]:
    """Zig-zag positions across the screen."""
    left, right = 170, style.WIDTH - 170
    x = left + (right - left) * index // max(1, count - 1)
    return x, 360 if index % 2 == 0 else 560


class PathScene(Scene):
    def __init__(self, app, game_id: str) -> None:
        self.game_id = game_id
        super().__init__(app)

    @property
    def level_ids(self) -> list[str]:
        return [level.id for level in self.content.memory_levels]

    def unlocked(self, level_id: str) -> bool:
        return progress.is_unlocked(self.profile, self.game_id, self.level_ids, level_id)

    def current_index(self) -> int:
        """Where the avatar stands: the first open level not won yet, or the last one."""
        for index, level_id in enumerate(self.level_ids):
            if progress.best_stars(self.profile, self.game_id, level_id) == 0:
                return index
        return len(self.level_ids) - 1

    def layout(self) -> None:
        self.buttons = [self.back_button(self.content.text("home"), self.to_home)]
        for index, level in enumerate(self.content.memory_levels):
            level_id = level.id
            rect = pygame.Rect(0, 0, NODE, NODE)
            rect.center = node_center(index, len(self.level_ids))
            open_ = self.unlocked(level_id)
            self.buttons.append(
                Button(
                    rect,
                    lambda level_id=level_id: self.play(level_id),
                    label=level_id if open_ else "",
                    name=f"level:{level_id}",
                    label_size=72,
                    color=theme(level.theme).accent,
                    radius=NODE // 2,
                    enabled=open_,
                    draw=lambda surface, rect, name=level.theme, open_=open_: self._draw_node(
                        surface, rect, name, open_
                    ),
                )
            )

    def _draw_node(self, surface: pygame.Surface, rect: pygame.Rect, name: str, open_: bool):
        if not open_:
            draw_padlock(surface, rect.center, 50)
        picture = icon(name, 56)
        surface.blit(picture, picture.get_rect(center=(rect.right - 8, rect.top + 8)))

    def play(self, level_id: str) -> None:
        from edugames.ui.scenes.memory import MemoryScene

        self.app.go(MemoryScene(self.app, self.game_id, level_id))

    def to_home(self) -> None:
        from edugames.ui.scenes.home import HomeScene

        self.app.go(HomeScene(self.app))

    def draw_scene(self, surface: pygame.Surface) -> None:
        game = next(game for game in self.content.games if game.id == self.game_id)
        self.draw_title(surface, game.title)
        self.draw_coin_count(surface)
        count = len(self.level_ids)
        points = [node_center(i, count) for i in range(count)]
        for width, color in ((46, style.OUTLINE), (38, ROAD)):  # a sandy road with an outline
            pygame.draw.lines(surface, color, False, points, width)
            for point in points:
                pygame.draw.circle(surface, color, point, width // 2)
        for index, level_id in enumerate(self.level_ids):
            x, y = points[index]
            stars = progress.best_stars(self.profile, self.game_id, level_id)
            draw_stars(surface, stars, (x, y + NODE // 2 + 40), 40)

    def draw_overlay(self, surface: pygame.Surface) -> None:
        x, y = node_center(self.current_index(), len(self.level_ids))
        draw_avatar(surface, self.profile.avatar, (x, y - NODE // 2 - 95), 170)
