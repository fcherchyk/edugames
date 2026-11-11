"""S2: the art style. Scenery per level, the chibi avatar, card colours, buttons, fonts, speed."""

import time
from dataclasses import fields

import pygame
import pytest

from edugames.core import avatar as options
from edugames.core.avatar import Avatar
from edugames.core.content import Letter
from edugames.core.profiles import new_profile
from edugames.demo import click, type_text, win_memory_game
from edugames.ui import style
from edugames.ui.avatar_draw import draw_avatar, draw_head, sprite_for
from edugames.ui.scenery import THEMES, background, icon, theme
from edugames.ui.scenes.memory import MemoryScene, letter_color
from edugames.ui.scenes.profiles import ProfileSelectScene
from edugames.ui.widgets import Button


def count_color(surface: pygame.Surface, color, tolerance: int = 12) -> int:
    """How many pixels are close to `color`."""
    threshold = (tolerance, tolerance, tolerance, 255)
    return pygame.mask.from_threshold(surface, color, threshold).count()


def start_as(app, name: str = "Sam") -> None:
    app.store.add(new_profile(name, 5))
    app.scene = ProfileSelectScene(app)
    click(app, f"profile:{name}")


# S2_AC1: scenery per level


def test_S2_AC1_every_level_has_a_theme_that_draws_a_full_screen_scenery(content) -> None:
    themes = [level.theme for level in content.memory_levels]

    assert themes == ["meadow", "beach", "forest", "snow", "space"]
    for name in themes:
        assert name in THEMES
        assert background(name).get_size() == style.SIZE


def test_S2_AC1_an_unknown_theme_falls_back_to_the_meadow() -> None:
    assert theme("volcano") is THEMES["meadow"]
    assert background("volcano").get_at((10, 10)) == background("meadow").get_at((10, 10))


def test_S2_AC1_the_memory_screen_draws_its_level_scenery(app) -> None:
    start_as(app)
    app.go(MemoryScene(app, "memory", "2"))
    app.step([], 16)

    assert app.scene.theme == "beach"
    assert app.surface.get_at((640, 790)) == background("beach").get_at((640, 790))
    assert background("beach").get_at((640, 790)) != background("meadow").get_at((640, 790))


def test_S2_AC1_every_theme_has_an_icon_for_the_path() -> None:
    for name in THEMES:
        assert icon(name, 56).get_bounding_rect().w > 20


# S2_AC2: the avatar


def looks() -> list[Avatar]:
    """Every option of every field at least once (one field changed at a time)."""
    choices = {
        "face": options.FACES,
        "skin": options.SKIN_TONES,
        "hair_style": options.HAIR_STYLES,
        "hair_color": options.HAIR_COLORS,
        "shirt": options.SHIRT_COLORS,
    }
    return [Avatar(**{f.name: value}) for f in fields(Avatar) for value in choices[f.name]]


@pytest.mark.parametrize("celebrating", [False, True])
def test_S2_AC2_every_look_is_drawn_with_the_navy_outline(app, celebrating) -> None:
    for look in looks():
        surface = pygame.Surface((320, 360), pygame.SRCALPHA)
        draw_avatar(surface, look, (160, 180), 340, celebrating)

        assert surface.get_bounding_rect().h > 300, look
        assert count_color(surface, style.OUTLINE) > 500, look


def test_S2_AC2_the_head_alone_is_drawn_for_the_look_buttons(app) -> None:
    surface = pygame.Surface((120, 120), pygame.SRCALPHA)
    draw_head(surface, Avatar(hair_style="bun"), (60, 64), 34)

    box = surface.get_bounding_rect()
    assert box.h > 70 and box.w > 60


def test_S2_AC2_a_look_is_drawn_once_and_then_reused(app) -> None:
    surface = pygame.Surface((200, 200))
    look = Avatar(face="wink", hair_style="spiky", shirt="teal")
    draw_avatar(surface, look, (100, 100), 151)
    hits = sprite_for.cache_info().hits

    draw_avatar(surface, look, (100, 100), 151)

    assert sprite_for.cache_info().hits == hits + 1


# S2_AC3: card colours


def test_S2_AC3_vowels_are_red_and_consonants_blue_as_the_content_says(content) -> None:
    vowels = [upper for upper, letter in content.letters.items() if letter.vowel]

    assert vowels == ["A", "E", "I", "O", "U"]
    assert letter_color(content.letters["A"]) == style.VOWEL
    assert letter_color(content.letters["M"]) == style.CONSONANT
    # another language may count other letters as vowels: the colour follows its content
    assert letter_color(Letter("Y", "y", "i griega", vowel=True)) == style.VOWEL


def test_S2_AC3_a_turned_card_shows_its_letter_in_its_colour(app) -> None:
    start_as(app)
    app.go(MemoryScene(app, "memory", "1"))
    scene = app.scene
    click(app, "card:0")
    app.step([], 16)

    card = scene.game.cards[0]
    color = letter_color(app.content.letters[card.letter])
    rect = scene.button("card:0").rect
    assert count_color(app.surface.subsurface(rect), color, 30) > 300


# S2_AC4: buttons


def test_S2_AC4_main_actions_are_the_green_pill(app) -> None:
    surface = pygame.Surface((400, 200))
    button = Button(pygame.Rect(50, 50, 300, 96), lambda: None, label="Go", primary=True)
    button.draw(surface)

    assert button.color == style.PRIMARY
    assert count_color(surface, style.PRIMARY, 25) > 3000


def test_S2_AC4_next_done_and_next_level_are_main_actions_and_every_target_is_big(app) -> None:
    start_as(app, "Ann")
    seen = {}
    click(app, "back")
    click(app, "new_player")
    type_text(app, "Sam")
    seen["next"] = app.scene.button("next")
    click(app, "next")
    click(app, "age:5")
    seen["done"] = app.scene.button("done")
    targets = list(app.scene.buttons)
    click(app, "done")
    targets += app.scene.buttons
    click(app, "game:memory")
    targets += app.scene.buttons
    click(app, "level:1")
    targets += app.scene.buttons
    win_memory_game(app)
    seen["next_level"] = app.scene.button("next_level")
    targets += app.scene.buttons

    assert all(button.primary for button in seen.values())
    assert min(min(b.rect.size) for b in targets) >= style.MIN_TARGET


# S2_AC5: fonts


def test_S2_AC5_titles_use_fredoka_and_letters_use_andika() -> None:
    assert style.TITLE_FONT_FILE.is_file()
    assert "Fredoka" in style.title_font(40).name
    assert "Andika" in style.font(40).name


def test_S2_AC5_a_missing_font_falls_back_to_pygames_own(tmp_path) -> None:
    font = style.load_font(tmp_path / "missing.ttf", 40)

    assert font.render("Aa", True, style.INK).get_width() > 0


# S2_AC6: drawing stays fast


def test_S2_AC6_sixty_frames_of_the_memory_game_draw_in_under_a_second(app) -> None:
    start_as(app)
    app.go(MemoryScene(app, "memory", "5"))
    click(app, "card:0")
    app.step([], 16)  # the first frame draws and caches the sprites

    start = time.perf_counter()
    for _ in range(60):
        app.step([], 16)

    assert time.perf_counter() - start < 1.0
