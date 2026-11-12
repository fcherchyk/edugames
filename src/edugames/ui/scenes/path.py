"""The goal path: a game's levels along a road, each opened by winning the one before. Up to five
levels zig-zag in one row; more go in two rows of up to five, joined by a bend of the road."""

import pygame

from edugames.core import progress
from edugames.ui import style
from edugames.ui.avatar_draw import draw_avatar
from edugames.ui.scenery import icon, theme
from edugames.ui.scenes.base import Scene
from edugames.ui.widgets import Button, draw_padlock, draw_stars

NODE = 130
ROW = 5  # levels per row
ROAD = (246, 228, 180)
ONE_ROW = {"stars": 40, "avatar": 170}
TWO_ROWS = {"stars": 34, "avatar": 112, "top": 322, "bottom": 640, "left": 250, "step": 190}
BEND_X = 1200  # where the road turns from the first row to the second


def node_centers(count: int) -> list[tuple[int, int]]:
    """One row zig-zagging across the screen, or two rows: left to right, then right to left."""
    if count <= ROW:
        left, right = 170, style.WIDTH - 170
        return [
            (left + (right - left) * i // max(1, count - 1), 360 if i % 2 == 0 else 560)
            for i in range(count)
        ]
    centers = []
    for i in range(count):
        row, col = divmod(i, ROW)
        col = col if row == 0 else ROW - 1 - col
        y = TWO_ROWS["top"] if row == 0 else TWO_ROWS["bottom"]
        centers.append((TWO_ROWS["left"] + col * TWO_ROWS["step"], y))
    return centers


def road_points(centers: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """The road through the stones, bending outside the last column between the two rows."""
    if len(centers) <= ROW:
        return centers
    top, bottom = centers[ROW - 1][1], centers[ROW][1]
    return centers[:ROW] + [(BEND_X, top), (BEND_X, bottom)] + centers[ROW:]


def sizes(count: int) -> dict[str, int]:
    return ONE_ROW if count <= ROW else TWO_ROWS


def stars_rect(center: tuple[int, int], size: int) -> pygame.Rect:
    """Where `draw_stars` puts a level's three stars, under its stone."""
    x, y = center
    rect = pygame.Rect(0, 0, round(size * 1.15 * 2 + size * 1.25), round(size * 1.25) + 6)
    rect.center = (x, y + NODE // 2 + size)
    return rect


def avatar_center(center: tuple[int, int], height: int) -> tuple[int, int]:
    """The avatar stands just above the stone."""
    x, y = center
    return x, y - NODE // 2 - height // 2 - 10


class PathScene(Scene):
    def __init__(self, app, game_id: str) -> None:
        self.game_id = game_id
        super().__init__(app)

    @property
    def levels(self):
        return self.content.levels[self.game_id]

    @property
    def level_ids(self) -> list[str]:
        return [level.id for level in self.levels]

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
        centers = node_centers(len(self.levels))
        for level, center in zip(self.levels, centers, strict=True):
            level_id = level.id
            rect = pygame.Rect(0, 0, NODE, NODE)
            rect.center = center
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
        from edugames.ui.scenes import level_scene

        self.app.go(level_scene(self.app, self.game_id, level_id))

    def to_home(self) -> None:
        from edugames.ui.scenes.home import HomeScene

        self.app.go(HomeScene(self.app))

    def avatar_rect(self) -> pygame.Rect:
        """The space the avatar takes, on the current level."""
        height = sizes(len(self.levels))["avatar"]
        rect = pygame.Rect(0, 0, round(height * 0.75), height)
        rect.center = avatar_center(node_centers(len(self.levels))[self.current_index()], height)
        return rect

    def draw_scene(self, surface: pygame.Surface) -> None:
        self.draw_title(surface, self.content.game(self.game_id).title)
        self.draw_coin_count(surface)
        centers = node_centers(len(self.levels))
        points = road_points(centers)
        for width, color in ((46, style.OUTLINE), (38, ROAD)):  # a sandy road with an outline
            pygame.draw.lines(surface, color, False, points, width)
            for point in points:
                pygame.draw.circle(surface, color, point, width // 2)
        size = sizes(len(self.levels))["stars"]
        for level_id, center in zip(self.level_ids, centers, strict=True):
            stars = progress.best_stars(self.profile, self.game_id, level_id)
            draw_stars(surface, stars, stars_rect(center, size).center, size)

    def draw_overlay(self, surface: pygame.Surface) -> None:
        height = sizes(len(self.levels))["avatar"]
        center = node_centers(len(self.levels))[self.current_index()]
        draw_avatar(surface, self.profile.avatar, avatar_center(center, height), height)
