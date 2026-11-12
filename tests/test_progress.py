"""S1_AC10 to S1_AC12, S1_AC15, S3_AC1, S3_AC13 and S3_AC15: stars, the goal path, coins, the
wardrobe, progress per game and answers per letter and picture."""

import pytest

from edugames.core import progress
from edugames.core.avatar import FREE_SHIRTS, SHIRT_COLORS, AvatarError
from edugames.core.profiles import new_profile

LEVELS = ["1", "2", "3"]


@pytest.mark.parametrize(
    ("pairs", "mismatches", "stars"),
    [(3, 0, 3), (3, 3, 3), (3, 4, 2), (3, 6, 2), (3, 7, 1), (3, 100, 1), (8, 8, 3)],
)
def test_S1_AC10_stars_come_from_the_mismatches(pairs, mismatches, stars) -> None:
    assert progress.stars_for(pairs, mismatches) == stars


def test_S1_AC10_the_best_stars_are_kept() -> None:
    profile = new_profile("Sam", 5)

    progress.record_win(profile, "memory", "1", 2)
    worse = progress.record_win(profile, "memory", "1", 1)
    assert progress.best_stars(profile, "memory", "1") == 2
    assert not worse.new_best

    better = progress.record_win(profile, "memory", "1", 3)
    assert progress.best_stars(profile, "memory", "1") == 3
    assert better.new_best


@pytest.mark.parametrize(("given", "kept"), [(0, 1), (5, 3)])
def test_S1_AC10_a_win_gives_1_to_3_stars(given, kept) -> None:
    assert progress.record_win(new_profile("Sam", 5), "memory", "1", given).stars == kept


def test_S1_AC11_only_the_first_level_starts_open() -> None:
    profile = new_profile("Sam", 5)

    assert [progress.is_unlocked(profile, "memory", LEVELS, level) for level in LEVELS] == [
        True,
        False,
        False,
    ]


def test_S1_AC11_winning_a_level_opens_the_next_one() -> None:
    profile = new_profile("Sam", 5)

    progress.record_win(profile, "memory", "1", 1)

    assert progress.is_unlocked(profile, "memory", LEVELS, "2")
    assert not progress.is_unlocked(profile, "memory", LEVELS, "3")


def test_S1_AC12_every_win_gives_coins_replays_included() -> None:
    profile = new_profile("Sam", 5)

    first = progress.record_win(profile, "memory", "1", 3)
    replay = progress.record_win(profile, "memory", "1", 1)

    assert (first.coins, replay.coins) == (5, 3)
    assert profile.coins == 8


def test_S1_AC15_free_shirts_are_owned_from_the_start() -> None:
    profile = new_profile("Sam", 5)

    assert all(profile.owns_shirt(color) for color in FREE_SHIRTS)
    assert profile.avatar.shirt in FREE_SHIRTS


def test_S1_AC15_a_shirt_is_bought_with_enough_coins_and_worn() -> None:
    profile = new_profile("Sam", 5)
    profile.coins = 7

    profile.buy_shirt("green")
    profile.wear_shirt("green")

    assert profile.coins == 7 - SHIRT_COLORS["green"].price
    assert profile.owns_shirt("green") and profile.avatar.shirt == "green"


def test_S1_AC15_a_shirt_is_refused_without_enough_coins() -> None:
    profile = new_profile("Sam", 5)
    profile.coins = 4

    assert not profile.can_buy_shirt("green")
    with pytest.raises(AvatarError):
        profile.buy_shirt("green")
    assert profile.coins == 4


def test_S1_AC15_owned_shirts_are_not_bought_twice_and_unowned_ones_cannot_be_worn() -> None:
    profile = new_profile("Sam", 5)

    with pytest.raises(AvatarError):
        profile.buy_shirt(FREE_SHIRTS[0])
    with pytest.raises(AvatarError):
        profile.wear_shirt("green")


def test_S3_AC1_progress_is_kept_per_game() -> None:
    profile = new_profile("Sam", 5)

    progress.record_win(profile, "rain", "1", 3)

    assert progress.is_unlocked(profile, "rain", LEVELS, "2")
    assert not progress.is_unlocked(profile, "memory", LEVELS, "2")
    assert profile.progress == {"rain": {"1": 3}}


@pytest.mark.parametrize(
    ("goal", "misses", "stars"),
    [(8, 0, 3), (8, 8, 3), (8, 9, 2), (8, 16, 2), (8, 17, 1), (12, 99, 1)],
)
def test_S3_AC13_stars_come_from_the_misses(goal, misses, stars) -> None:
    assert progress.stars_for(goal, misses) == stars


def test_S3_AC15_answers_are_counted_per_letter_with_the_key_pressed_instead() -> None:
    profile = new_profile("Sam", 5)

    assert progress.record_answer(profile, "B", "B")
    assert progress.record_answer(profile, "B", "B")
    assert not progress.record_answer(profile, "B", "D")
    progress.record_answer(profile, "B", "D")
    progress.record_answer(profile, "B", "P")

    record = profile.answers["letters"]["B"]
    assert (record.right, record.wrong) == (2, {"D": 2, "P": 1})
    assert "pictures" not in profile.answers


def test_S3_AC15_picture_answers_are_counted_per_picture() -> None:
    profile = new_profile("Sam", 5)

    progress.record_answer(profile, "C", "K", picture="cat")
    progress.record_answer(profile, "C", "C", picture="cat")

    assert profile.answers["pictures"]["cat"].right == 1
    assert profile.answers["pictures"]["cat"].wrong == {"K": 1}
    assert profile.answers["letters"]["C"].wrong == {"K": 1}  # counted for the letter too
