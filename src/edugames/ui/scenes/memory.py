"""The memory game screen: turn two cards over and match `A` with `a`."""

import pygame

from edugames.core import progress
from edugames.core.content import Letter
from edugames.core.memory_game import Flip, MemoryGame, pick_letters
from edugames.ui import paint, style
from edugames.ui.scenes.level import LevelScene
from edugames.ui.widgets import Button, draw_text

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


class MemoryScene(LevelScene):
    def start(self) -> None:
        letters = pick_letters(
            self.level.letters, list(self.app.content.letters), self.level.pairs, self.app.rng
        )
        pairs = [(upper, self.app.content.letters[upper].lower) for upper in letters]
        self.game = MemoryGame(pairs, self.app.rng)
        self.turn_back_in = 0

    def layout_play(self) -> None:
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
            self.finish(progress.stars_for(self.game.pairs, self.game.mismatches))
        else:
            self.layout()

    def update(self, dt_ms: int) -> None:
        if self.game.waiting_turn_back:
            self.turn_back_in -= dt_ms
            if self.turn_back_in <= 0:
                self.game.turn_back()
                self.layout()
