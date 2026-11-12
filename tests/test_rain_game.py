"""S3_AC5, S3_AC8 and S3_AC10 to S3_AC13: the rules of Letter Rain, without a window."""

import random

import pytest

from edugames.core.rain_game import (
    CHOICES,
    LANES,
    MAX_SPEED,
    MIN_SPEED,
    NEXT_MS,
    RISE_SHARE,
    SLOW_DOWN,
    SPEED_UP,
    Drop,
    Item,
    Press,
    RainGame,
    choices_for,
    letter_items,
    picture_items,
)

LETTERS = [("A", "a"), ("M", "m"), ("O", "o"), ("S", "s"), ("T", "t")]
PICTURES = [("apple", "A"), ("ball", "B"), ("moon", "M"), ("sun", "S"), ("fish", "F"), ("egg", "E")]
ALPHABET = [chr(c) for c in range(ord("A"), ord("Z") + 1)]


def new_game(case="upper", at_once=1, goal=8, seed=1, items=None, **options) -> RainGame:
    items = items if items is not None else letter_items(LETTERS, case)
    return RainGame(items, goal, at_once, 9, random.Random(seed), alphabet=ALPHABET, **options)


def falling(game: RainGame, count: int = 1) -> list[Drop]:
    """Let the rain run until `count` items are falling."""
    for _ in range(10_000):
        if len(game.drops) >= count:
            return game.drops
        game.advance(16)
    raise AssertionError("nothing fell")


def seen(game: RainGame, ms: int = 600_000) -> list[Drop]:
    """Every item that appears in `ms`, finding each one as soon as it appears."""
    drops = []
    for _ in range(ms // 50):
        changes = game.advance(50)
        drops += changes.appeared
        for drop in changes.appeared:
            game.press(drop.item.answer)
    return drops


@pytest.mark.parametrize(
    ("case", "shown"), [("upper", {"AMOST"}), ("lower", {"amost"}), ("both", {"AMOST", "amost"})]
)
def test_S3_AC5_letters_fall_in_the_levels_case(case, shown) -> None:
    drops = seen(new_game(case, goal=10_000))
    texts = {drop.item.shows for drop in drops}

    assert all(not drop.item.picture for drop in drops)
    if case == "both":
        assert texts == set("AMOSTamost")  # each letter comes in both cases over time
    else:
        assert texts == set(next(iter(shown)))
    assert all(drop.item.shows.upper() == drop.item.answer for drop in drops)


def test_S3_AC5_pictures_fall_and_their_answer_is_the_first_letter() -> None:
    drops = seen(new_game(items=picture_items(PICTURES), goal=10_000))

    assert {(drop.item.shows, drop.item.answer) for drop in drops} == set(PICTURES)
    assert all(drop.item.picture for drop in drops)


@pytest.mark.parametrize("at_once", [1, 2, 3])
def test_S3_AC5_no_more_than_at_once_fall_and_never_the_same_answer_twice(at_once) -> None:
    game = new_game("both", at_once=at_once, goal=10_000)
    most = 0
    for step in range(20_000):
        game.advance(16)
        answers = [drop.item.answer for drop in game.drops]
        lanes = [drop.lane for drop in game.drops]
        most = max(most, len(answers))
        assert len(answers) == len(set(answers)) and len(lanes) == len(set(lanes))
        assert all(0 <= lane < LANES for lane in lanes)
        if step % 400 == 0 and game.drops:
            game.press(game.lowest().item.answer)

    assert most == at_once


def test_S3_AC5_a_new_item_arrives_after_one_is_found() -> None:
    game = new_game()
    (drop,) = falling(game)
    assert game.press(drop.item.answer).result is Press.HIT
    assert game.drops == []

    assert game.advance(NEXT_MS - 1).appeared == []
    assert len(game.advance(1).appeared) == 1


def test_S3_AC8_the_right_key_clears_the_lowest_item_with_that_letter() -> None:
    game = new_game()
    high, low, other = (
        Drop(Item("A", "A"), 0, 0.2),
        Drop(Item("A", "a"), 1, 0.7),
        Drop(Item("M", "M"), 2, 0.9),
    )
    game.drops = [high, low, other]

    answer = game.press("A")

    assert answer.result is Press.HIT and answer.drop is low
    assert game.drops == [high, other] and game.hits == 1 and game.misses == 0


def test_S3_AC8_a_wrong_key_is_a_miss_and_a_key_with_nothing_falling_is_ignored() -> None:
    game = new_game()
    assert game.press("A").result is Press.IGNORED  # nothing falls yet
    (drop,) = falling(game)
    wrong = next(letter for letter in "AMOST" if letter != drop.item.answer)

    answer = game.press(wrong)

    assert answer.result is Press.MISS and answer.drop is drop  # the item most likely aimed at
    assert game.drops == [drop] and game.misses == 1 and game.hits == 0


def test_S3_AC10_the_choices_are_the_answer_and_two_other_letters() -> None:
    pool = [letter for _, letter in PICTURES]
    orders = set()
    for seed in range(30):
        choices = choices_for("M", pool, ALPHABET, random.Random(seed))
        assert len(choices) == CHOICES == len(set(choices)) and "M" in choices
        assert set(choices) <= set(pool)  # the others come from the level's pictures
        orders.add(choices.index("M"))
    assert orders == {0, 1, 2}  # shuffled

    few = choices_for("A", ["A", "B"], ALPHABET, random.Random(1))
    assert "A" in few and "B" in few and len(set(few)) == 3  # filled from the alphabet

    game = new_game(items=picture_items(PICTURES), at_once=2, choices=True)
    for _ in range(5):
        (drop,) = falling(game)
        assert drop.item.answer in drop.choices and len(drop.choices) == CHOICES
        game.press(drop.item.answer)
    assert game.at_once == 1  # one picture at a time for the youngest


def test_S3_AC11_an_item_that_reaches_the_ground_bounces_back_up() -> None:
    game = new_game()
    (drop,) = falling(game)

    changes = game.advance(game.fall_ms)

    assert changes.bounced == [drop] and drop.rising and drop.y == 1.0
    assert game.bounces == 1 and game.misses == 1 and drop in game.drops
    game.advance(game.fall_ms * RISE_SHARE)
    assert drop.y == 0.0 and not drop.rising  # back at the top, falling again
    game.advance(1000)
    assert 0 < drop.y < 1 and not game.done


def test_S3_AC12_three_right_in_a_row_speed_up_to_a_limit() -> None:
    game = new_game(goal=100)
    speeds = []
    for _ in range(30):
        (drop,) = falling(game)
        game.press(drop.item.answer)
        speeds.append(game.speed)

    assert speeds[:3] == [1.0, 1.0, SPEED_UP]
    assert speeds[5] == pytest.approx(SPEED_UP**2)
    assert max(speeds) == speeds[-1] == MAX_SPEED
    assert game.fall_ms == pytest.approx(9000 / MAX_SPEED)


def test_S3_AC12_a_miss_or_a_bounce_slows_down_to_a_limit() -> None:
    game = new_game(goal=100)
    (drop,) = falling(game)
    game.press("Z")
    assert game.speed == SLOW_DOWN and game.streak == 0

    game.advance(game.fall_ms)  # a bounce
    assert game.speed == pytest.approx(SLOW_DOWN**2)
    for _ in range(10):
        game.press("Z")
    assert game.speed == MIN_SPEED


def test_S3_AC13_the_level_ends_after_its_goal_of_right_answers() -> None:
    game = new_game(goal=3, at_once=2)
    for _ in range(3):
        assert not game.done
        drops = falling(game)
        game.press(drops[0].item.answer)

    assert game.done and game.hits == 3 and game.drops == []
    assert game.advance(60_000).appeared == []  # nothing falls any more
    assert game.press("A").result is Press.IGNORED
