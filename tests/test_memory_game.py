"""S1_AC6, S1_AC7 and S1_AC9: dealing and playing the upper/lowercase memory game."""

import random
from collections import Counter

import pytest

from edugames.core.memory_game import Flip, MemoryGame, pick_letters

PAIRS = [("A", "a"), ("M", "m"), ("O", "o")]


def new_game(seed: int = 1) -> MemoryGame:
    return MemoryGame(PAIRS, random.Random(seed))


def partner(game: MemoryGame, index: int) -> int:
    letter = game.cards[index].letter
    return next(i for i, c in enumerate(game.cards) if c.letter == letter and i != index)


def stranger(game: MemoryGame, index: int) -> int:
    return next(i for i, c in enumerate(game.cards) if c.letter != game.cards[index].letter)


def test_S1_AC6_each_letter_is_dealt_once_in_upper_and_once_in_lower_case() -> None:
    game = new_game()

    assert len(game.cards) == 6 and game.pairs == 3
    assert sorted(card.text for card in game.cards) == ["A", "M", "O", "a", "m", "o"]
    assert Counter(card.letter for card in game.cards) == {"A": 2, "M": 2, "O": 2}


def test_S1_AC6_the_cards_are_shuffled() -> None:
    orders = {tuple(card.text for card in new_game(seed).cards) for seed in range(10)}

    assert len(orders) > 1


def test_S1_AC6_a_level_without_letters_gets_random_ones() -> None:
    alphabet = [chr(c) for c in range(65, 91)]
    picked = pick_letters(None, alphabet, 8, random.Random(3))

    assert len(set(picked)) == 8 and set(picked) <= set(alphabet)
    assert pick_letters(["A", "M"], alphabet, 2, random.Random(3)) == ["A", "M"]


def test_S1_AC7_a_matching_pair_stays_face_up() -> None:
    game = new_game()

    assert game.flip(0) is Flip.FIRST
    assert game.flip(partner(game, 0)) is Flip.MATCH
    assert {0, partner(game, 0)} == game.matched
    assert not game.waiting_turn_back


def test_S1_AC7_a_mismatch_waits_and_then_turns_back() -> None:
    game = new_game()
    other = stranger(game, 0)

    game.flip(0)
    assert game.flip(other) is Flip.MISMATCH
    assert game.waiting_turn_back and game.is_shown(0) and game.is_shown(other)

    game.turn_back()

    assert not game.is_shown(0) and not game.is_shown(other)
    assert game.mismatches == 1


def test_S1_AC7_no_card_turns_while_two_wait_to_turn_back() -> None:
    game = new_game()
    game.flip(0)
    game.flip(stranger(game, 0))
    third = next(i for i in range(6) if not game.is_shown(i))

    assert game.flip(third) is Flip.IGNORED


@pytest.mark.parametrize("index", [-1, 6])
def test_S1_AC7_cards_outside_the_board_are_ignored(index) -> None:
    assert new_game().flip(index) is Flip.IGNORED


def test_S1_AC7_a_face_up_or_matched_card_cannot_be_flipped_again() -> None:
    game = new_game()
    game.flip(0)
    assert game.flip(0) is Flip.IGNORED
    game.flip(partner(game, 0))
    assert game.flip(0) is Flip.IGNORED


def test_S1_AC9_the_game_ends_only_when_every_pair_is_matched() -> None:
    game = new_game()
    for _ in range(20):  # many mistakes: still no way to lose
        game.flip(0)
        game.flip(stranger(game, 0))
        game.turn_back()
    assert not game.done

    for letter in ("A", "M", "O"):
        for index, card in enumerate(game.cards):
            if card.letter == letter:
                game.flip(index)

    assert game.done
    assert game.mismatches == 20
