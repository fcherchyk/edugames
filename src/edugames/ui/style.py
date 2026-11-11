"""Colours, sizes and fonts shared by every screen.

The art style: a navy outline around everything, one flat cel shade per shape, and gloss (a
gradient and a white shine) only on rewards and main actions.
"""

from functools import cache
from pathlib import Path

import pygame

from edugames.core.content import ASSETS_DIR

SIZE = WIDTH, HEIGHT = 1280, 800
MIN_TARGET = 96  # smallest side of anything a child taps

Color = tuple[int, int, int]

OUTLINE = (38, 40, 78)  # navy ink around every shape
INK = OUTLINE
MUTED = (150, 150, 175)
WHITE = (255, 255, 255)
PANEL = WHITE
LOCKED = (205, 208, 222)
PRIMARY = (110, 205, 70)  # the green pill of main actions
ACCENT = (255, 170, 60)
GOOD = (90, 200, 110)
GOLD = (255, 205, 40)
STAR = GOLD
COIN = (245, 185, 30)
CARD_BACK = (80, 145, 240)
VOWEL = (225, 55, 70)  # Montessori colours for the letters on the cards
CONSONANT = (45, 90, 210)
DIM = (20, 22, 50, 130)  # behind a pop-up

FONT_FILE = ASSETS_DIR / "fonts" / "Andika-Regular.ttf"
BOLD_FONT_FILE = ASSETS_DIR / "fonts" / "Andika-Bold.ttf"
TITLE_FONT_FILE = ASSETS_DIR / "fonts" / "Fredoka-SemiBold.ttf"


def load_font(path: Path, size: int) -> pygame.font.Font:
    """The font at `path`, or pygame's own font if the file is missing."""
    return pygame.font.Font(path if path.is_file() else None, size)


@cache
def font(size: int, bold: bool = False) -> pygame.font.Font:
    """Andika, made for early readers (single-storey a and g): letters and names."""
    return load_font(BOLD_FONT_FILE if bold else FONT_FILE, size)


@cache
def title_font(size: int) -> pygame.font.Font:
    """Fredoka, round and playful: titles, buttons and numbers."""
    return load_font(TITLE_FONT_FILE, size)
