"""The memory game screen, and the victory pop-up when every pair is matched."""

import pygame

from edugames.core import progress
from edugames.core.content import Letter
from edugames.core.memory_game import Flip, MemoryGame, pick_letters
from edugames.core.progress import Win
from edugames.ui import paint, style
from edugames.ui.avatar_draw import draw_avatar
from edugames.ui.scenes.base import Scene
from edugames.ui.widgets import Button, draw_coin, draw_stars, draw_text

TURN_BACK_MS = 1000  # how long two different cards stay up
BOARD = pygame.Rect(90, 150, style.WIDTH - 180, style.HEIGHT - 180)
GAP = 24


def letter_color(letter: Letter) -> tuple[int, int, int]:
    """Vowels in red, consonants in blue (Montessori); the content says which are vowels."""
    return style.VOWEL if letter.vowel else style.CONSONANT


def card_rects(count: int) -> list[pygame.Rect]:
    columns = 3 if count <= 6 else 4
    rows = -(-count // columns)
    width = min(190, (BOARD.w - GAP * (columns - 1)) // columns)
    height = min(round(width * 1.25), (BOARD.h - GAP * (rows - 1)) // rows)
    width = min(width, round(height / 1.25)) if rows > 2 else width
    left = BOARD.centerx - (columns * width + (columns - 1) * GAP) // 2
    top = BOARD.centery - (rows * height + (rows - 1) * GAP) // 2
    return [
        pygame.Rect(left + col * (width + GAP), top + row * (height + GAP), width, height)
        for row, col in (divmod(i, columns) for i in range(count))
    ]


class MemoryScene(Scene):
    def __init__(self, app, game_id: str, level_id: str) -> None:
        self.game_id = game_id
        self.level = app.content.memory_level(level_id)
        self.theme = self.level.theme
        letters = pick_letters(
            self.level.letters, list(app.content.letters), self.level.pairs, app.rng
        )
        pairs = [(upper, app.content.letters[upper].lower) for upper in letters]
        self.game = MemoryGame(pairs, app.rng)
        self.turn_back_in = 0
        self.win: Win | None = None
        super().__init__(app)

    @property
    def next_level_id(self) -> str | None:
        ids = [level.id for level in self.content.memory_levels]
        position = ids.index(self.level.id)
        return ids[position + 1] if position + 1 < len(ids) else None

    def layout(self) -> None:
        if self.win:
            self._layout_victory()
            return
        self.buttons = [self.back_button(self.content.text("path"), self.to_path)]
        for index, rect in enumerate(card_rects(len(self.game.cards))):
            self.buttons.append(
                Button(
                    rect,
                    lambda index=index: self.flip(index),
                    name=f"card:{index}",
                    draw=lambda surface, rect, index=index: self._draw_card(surface, rect, index),
                    color=self._card_color(index),
                    ring=style.GOOD if index in self.game.matched else None,
                )
            )

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

    def _card_color(self, index: int) -> tuple[int, int, int]:
        return style.PANEL if self.game.is_shown(index) else style.CARD_BACK

    def _draw_card(self, surface: pygame.Surface, rect: pygame.Rect, index: int) -> None:
        if self.game.is_shown(index):
            card = self.game.cards[index]
            color = letter_color(self.content.letters[card.letter])
            draw_text(surface, card.text, round(rect.h * 0.6), rect.center, color, bold=True)
            if index in self.game.matched:
                paint.sparkle(surface, (rect.right - 22, rect.top + 22), 14, style.GOLD)
        else:
            star = paint.star(round(rect.w * 0.5), True)
            surface.blit(star, star.get_rect(center=rect.center))

    def flip(self, index: int) -> None:
        result = self.game.flip(index)
        if result is Flip.IGNORED:
            return
        self.app.audio.say_letter(self.game.cards[index].letter)
        if result is Flip.MISMATCH:
            self.turn_back_in = TURN_BACK_MS
        if self.game.done:
            self.finish()
        self.layout()

    def update(self, dt_ms: int) -> None:
        if self.game.waiting_turn_back:
            self.turn_back_in -= dt_ms
            if self.turn_back_in <= 0:
                self.game.turn_back()
                self.layout()

    def finish(self) -> None:
        stars = progress.stars_for(self.game.pairs, self.game.mismatches)
        self.win = progress.record_win(self.profile, self.game_id, self.level.id, stars)
        self.app.save()

    def to_path(self) -> None:
        from edugames.ui.scenes.path import PathScene

        self.app.go(PathScene(self.app, self.game_id))

    def to_next_level(self) -> None:
        assert self.next_level_id is not None
        self.app.go(MemoryScene(self.app, self.game_id, self.next_level_id))

    def draw_scene(self, surface: pygame.Surface) -> None:
        if not self.win:
            self.draw_title(surface, self.content.text("level", number=self.level.id))
            self.draw_coin_count(surface)
            return
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
        draw_stars(surface, self.win.stars, (right, panel.top + 235), 100)
        label = self.content.text("plus_coins", coins=self.win.coins)
        text = draw_text(
            surface, label, 56, (right + 30, panel.top + 370), style.OUTLINE, title=True
        )
        draw_coin(surface, (text.left - 40, text.centery), 26)
