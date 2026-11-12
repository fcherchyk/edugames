"""The Letter Rain screen: letters or pictures fall, and the child finds their letter on the real
keyboard, on the on-screen keyboard, or (the youngest, on picture levels) among three letters."""

import math
from functools import lru_cache

import pygame

from edugames.core import progress
from edugames.core.content import RainLevel
from edugames.core.rain_game import (
    CHOICES_BELOW_AGE,
    LANES,
    Drop,
    Press,
    RainGame,
    letter_items,
    picture_items,
)
from edugames.ui import paint, style
from edugames.ui.keyboard import (
    GAP,
    KEY_H,
    MUTED_KEY,
    draw_key_label,
    draw_keyboard_icon,
    key_rects,
    keyboard_top,
)
from edugames.ui.pictures import draw_picture
from edugames.ui.scenery import GROUND_TOP
from edugames.ui.scenes.level import LevelScene
from edugames.ui.scenes.memory import letter_color
from edugames.ui.widgets import Button

LETTER_CARD = 120
PICTURE_CARD = 150
PICTURE_SIZE = 122
TOP_Y = 40  # where an item's centre starts: half hidden under the top bar
SKY_LEFT, SKY_RIGHT = 256, style.WIDTH - 256  # clear of the back button and the coins
FLASH_MS = 250
POP_MS = 350
HIT_FLASH, MISS_FLASH = style.GOOD, style.ACCENT
CHOICE_W, CHOICE_H, CHOICE_GAP = 200, 150, 48
GOAL_Y = 152
KEY_RADIUS = 20
GOAL_STEP = 32


def lane_x(lane: int) -> int:
    return round(SKY_LEFT + (lane + 0.5) * (SKY_RIGHT - SKY_LEFT) / LANES)


def toggle_rect(row_count: int) -> pygame.Rect:
    """The keyboard button: at the right end of the keyboard's last row."""
    top = keyboard_top(row_count) + (row_count - 1) * (KEY_H + GAP)
    return pygame.Rect(style.WIDTH - 60 - 150, top, 150, KEY_H)


def choice_rects(count: int) -> list[pygame.Rect]:
    width = count * CHOICE_W + (count - 1) * CHOICE_GAP
    left = (style.WIDTH - width) // 2
    top = style.HEIGHT - 24 - CHOICE_H
    return [
        pygame.Rect(left + i * (CHOICE_W + CHOICE_GAP), top, CHOICE_W, CHOICE_H)
        for i in range(count)
    ]


@lru_cache(maxsize=128)
def letter_sprite(text: str, color: tuple[int, int, int], size: int) -> pygame.Surface:
    return style.font(size, True).render(text, True, color)


class RainScene(LevelScene):
    level: RainLevel

    def start(self) -> None:
        content, level = self.app.content, self.level
        assert isinstance(level, RainLevel)
        if level.has_pictures:
            items = picture_items((key, content.pictures[key].letter) for key in level.pictures)
        else:
            pairs = ((upper, content.letters[upper].lower) for upper in level.letters)
            items = letter_items(pairs, level.case)
        self.choosing = level.has_pictures and self.app.profile.age < CHOICES_BELOW_AGE
        self.game = RainGame(
            items,
            level.goal,
            level.at_once,
            level.fall_seconds,
            self.app.rng,
            choices=self.choosing,
            alphabet=list(content.letters),
        )
        self.lit = {item.answer for item in items}  # the letters that can fall in this level
        self.flashes: dict[str, tuple[tuple[int, int, int], int]] = {}  # letter -> colour, ms
        self.pops: list[tuple[tuple[int, int], int]] = []  # where an item was found, ms left

    # --- State --------------------------------------------------------------------------------

    @property
    def keyboard_shown(self) -> bool:
        return not self.choosing and self.profile.setting("keyboard")

    @property
    def ground_y(self) -> int:
        """Where a falling item touches the ground and bounces."""
        if self.choosing:
            return choice_rects(3)[0].top - 12
        if self.keyboard_shown:
            return keyboard_top(len(self.content.keyboard)) - 12
        return GROUND_TOP + 90

    def drop_rect(self, drop: Drop) -> pygame.Rect:
        size = PICTURE_CARD if drop.item.picture else LETTER_CARD
        bottom = self.ground_y - size / 2
        rect = pygame.Rect(0, 0, size, size)
        rect.center = (lane_x(drop.lane), round(TOP_Y + drop.y * (bottom - TOP_Y)))
        return rect

    # --- Layout -------------------------------------------------------------------------------

    def layout_play(self) -> None:
        if self.choosing:
            self._layout_choices()
            return
        if self.keyboard_shown:
            for letter, rect in key_rects(self.content.keyboard).items():
                self.buttons.append(self._key_button(letter, rect))
        self.buttons.append(
            Button(
                toggle_rect(len(self.content.keyboard)),
                self.toggle_keyboard,
                name="keyboard",
                draw=lambda surface, rect: draw_keyboard_icon(
                    surface, rect.center, self.keyboard_shown
                ),
            )
        )

    def _key_button(self, letter: str, rect: pygame.Rect) -> Button:
        """A key of the on-screen keyboard: lit if its letter can fall in this level."""
        return self._letter_button(letter, rect, f"key:{letter}", letter in self.lit, 46)

    def _layout_choices(self) -> None:
        """The three big letters of the picture that is falling (none between two pictures)."""
        if not self.game.drops:
            return
        choices = self.game.drops[0].choices
        for letter, rect in zip(choices, choice_rects(len(choices)), strict=True):
            self.buttons.append(self._letter_button(letter, rect, f"choice:{letter}", True, 72))

    def _letter_button(
        self, letter: str, rect: pygame.Rect, name: str, lit: bool, size: int
    ) -> Button:
        """A button that presses `letter`, showing its capital and small letter; it flashes
        green or orange for a moment when pressed."""
        flash = self.flashes.get(letter)
        color = flash[0] if flash else style.PANEL if lit else MUTED_KEY
        ink = letter_color(self.content.letters[letter]) if lit else style.MUTED
        lower = self.content.letters[letter].lower
        return Button(
            rect,
            lambda: self.press(letter),
            name=name,
            color=color,
            radius=KEY_RADIUS,
            draw=lambda surface, rect: draw_key_label(surface, rect, letter, lower, ink, size),
        )

    # --- Events -------------------------------------------------------------------------------

    def handle(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            upper = getattr(event, "unicode", "").upper()
            if len(upper) == 1 and upper in self.content.letters:
                self.press(upper)
            return
        for button in list(self.buttons):
            if button.handle(event):
                return
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and not self.win:
            for drop in reversed(self.game.drops):
                if self.drop_rect(drop).collidepoint(event.pos):
                    self.say_name(drop)
                    return

    def press(self, letter: str) -> None:
        """The child pressed `letter` (uppercase), on any keyboard."""
        answer = self.game.press(letter)
        if answer.result is Press.IGNORED or answer.drop is None:
            return
        drop = answer.drop
        picture = drop.item.shows if drop.item.picture else None
        progress.record_answer(self.profile, drop.item.answer, letter, picture)
        if answer.result is Press.HIT:
            self.flashes[letter] = (HIT_FLASH, FLASH_MS)
            self.pops.append((self.drop_rect(drop).center, POP_MS))
            self.app.audio.cancel(drop)  # its word, if it has not been said yet
            if picture:
                self.app.audio.say_letter_and_word(letter, picture)
            else:
                self.app.audio.say_letter(letter)
        else:
            self.flashes[letter] = (MISS_FLASH, FLASH_MS)
        if self.game.done:
            self.pops.clear()
            self.finish(progress.stars_for(self.game.goal, self.game.misses))
        else:
            self.layout()

    def say_name(self, drop: Drop) -> None:
        """A hint (on a bounce or a tap): the letter's name, or the picture's word. It is skipped
        when the voice is already speaking."""
        if drop.item.picture:
            self.app.audio.say_word(drop.item.shows, hint=True, key=drop)
        else:
            self.app.audio.say_letter(drop.item.answer, hint=True, key=drop)

    def toggle_keyboard(self) -> None:
        self.profile.settings["keyboard"] = not self.keyboard_shown
        self.app.save()
        self.layout()

    def leave(self) -> None:
        self.app.save()  # keeps the answers given so far

    def update(self, dt_ms: int) -> None:
        if self.win:
            return
        changes = self.game.advance(dt_ms)
        for drop in changes.appeared:
            if drop.item.picture:
                self.app.audio.say_word(drop.item.shows, key=drop)
        for drop in changes.bounced:
            self.say_name(drop)
        relayout = bool(changes.appeared) and self.choosing
        for letter, (color, left) in list(self.flashes.items()):
            if left - dt_ms <= 0:
                del self.flashes[letter]
                relayout = True
            else:
                self.flashes[letter] = (color, left - dt_ms)
        self.pops = [(center, left - dt_ms) for center, left in self.pops if left > dt_ms]
        if relayout:
            self.layout()

    # --- Drawing ------------------------------------------------------------------------------

    def draw_play(self, surface: pygame.Surface) -> None:
        for drop in self.game.drops:
            self._draw_drop(surface, drop)
        for center, left in self.pops:
            self._draw_pop(surface, center, 1 - left / POP_MS)
        self._draw_goal(surface)

    def _draw_drop(self, surface: pygame.Surface, drop: Drop) -> None:
        rect = self.drop_rect(drop)
        paint.draw_box(surface, rect, style.WHITE, 28)
        if drop.item.picture:
            draw_picture(surface, drop.item.shows, rect.center, PICTURE_SIZE)
            return
        color = letter_color(self.content.letters[drop.item.answer])
        sprite = letter_sprite(drop.item.shows, color, round(LETTER_CARD * 0.7))
        surface.blit(sprite, sprite.get_rect(center=(rect.centerx, rect.centery - 4)))

    def _draw_pop(self, surface: pygame.Surface, center, t: float) -> None:
        """Sparkles flying out where an item was found."""
        cx, cy = center
        for i in range(8):
            angle = i * math.pi / 4
            r = 20 + 70 * t
            point = (cx + r * math.cos(angle), cy + r * math.sin(angle))
            paint.sparkle(surface, point, 16 * (1 - t) + 4, style.GOLD)

    def _draw_goal(self, surface: pygame.Surface) -> None:
        """One dot per right answer of the goal, gold once found."""
        goal = self.game.goal
        for i in range(goal):
            x = round(style.WIDTH / 2 + (i - (goal - 1) / 2) * GOAL_STEP)
            pygame.draw.circle(surface, style.OUTLINE, (x, GOAL_Y), 12)
            fill = style.GOLD if i < self.game.hits else style.WHITE
            pygame.draw.circle(surface, fill, (x, GOAL_Y), 9)
