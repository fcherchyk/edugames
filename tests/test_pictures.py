"""S3_AC4: the picture library, drawn in code in the art style."""

import pygame
import pytest

from edugames.ui import style
from edugames.ui.pictures import DRAWINGS, draw_picture, picture


def count_color(surface: pygame.Surface, color, tolerance: int = 12) -> int:
    threshold = (tolerance, tolerance, tolerance, 255)
    return pygame.mask.from_threshold(surface, color, threshold).count()


@pytest.fixture(autouse=True)
def display(app) -> None:
    """Fonts and surfaces need pygame started (the `app` fixture does it)."""


def test_S3_AC4_every_picture_is_drawn_with_the_navy_outline(content) -> None:
    assert set(content.pictures) <= set(DRAWINGS)  # every English picture has its own drawing
    fallback = pygame.image.tobytes(picture("no-such-picture", 120), "RGBA")
    for picture_id in DRAWINGS:
        sprite = picture(picture_id, 120)
        box = sprite.get_bounding_rect()

        assert sprite.get_size() == (120, 120)
        assert box.w > 60 and box.h > 50, picture_id
        assert count_color(sprite, style.OUTLINE) > 150, picture_id
        assert pygame.image.tobytes(sprite, "RGBA") != fallback, picture_id


def test_S3_AC4_an_unknown_picture_draws_a_fallback() -> None:
    surface = pygame.Surface((200, 200), pygame.SRCALPHA)

    draw_picture(surface, "unicorn", (100, 100), 120)

    assert surface.get_bounding_rect().w > 60
    assert count_color(surface, style.OUTLINE) > 150


def test_S3_AC4_a_picture_is_drawn_once_and_then_reused() -> None:
    surface = pygame.Surface((200, 200), pygame.SRCALPHA)
    draw_picture(surface, "volcano", (100, 100), 131)
    hits = picture.cache_info().hits

    draw_picture(surface, "volcano", (100, 100), 131)

    assert picture.cache_info().hits == hits + 1
