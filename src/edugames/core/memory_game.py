"""The upper/lowercase memory game: turn two cards over and match `A` with `a`.

There is no timer and no way to lose: the game ends only when every pair is matched.
"""

import random
from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum, auto


@dataclass(frozen=True)
class Card:
    letter: str  # the pair's key: the uppercase letter
    text: str  # what the card shows: the uppercase or the lowercase letter


class Flip(Enum):
    IGNORED = auto()  # not allowed now: already up, matched, or two cards waiting to turn back
    FIRST = auto()
    MATCH = auto()
    MISMATCH = auto()  # both stay up until turn_back()


class MemoryGame:
    def __init__(self, pairs: Sequence[tuple[str, str]], rng: random.Random) -> None:
        """`pairs` are (uppercase, lowercase) letters; each gives two cards."""
        cards = [Card(upper, text) for upper, lower in pairs for text in (upper, lower)]
        rng.shuffle(cards)
        self.cards = cards
        self.face_up: list[int] = []
        self.matched: set[int] = set()
        self.mismatches = 0

    @property
    def pairs(self) -> int:
        return len(self.cards) // 2

    @property
    def waiting_turn_back(self) -> bool:
        return len(self.face_up) == 2

    @property
    def done(self) -> bool:
        return len(self.matched) == len(self.cards)

    def is_shown(self, index: int) -> bool:
        return index in self.matched or index in self.face_up

    def flip(self, index: int) -> Flip:
        if self.waiting_turn_back or self.is_shown(index) or not 0 <= index < len(self.cards):
            return Flip.IGNORED
        self.face_up.append(index)
        if len(self.face_up) == 1:
            return Flip.FIRST
        first, second = self.face_up
        if self.cards[first].letter == self.cards[second].letter:
            self.matched.update(self.face_up)
            self.face_up.clear()
            return Flip.MATCH
        self.mismatches += 1
        return Flip.MISMATCH

    def turn_back(self) -> None:
        self.face_up.clear()


def pick_letters(
    letters: Sequence[str] | None, alphabet: Sequence[str], pairs: int, rng: random.Random
) -> list[str]:
    """The level's letters, or `pairs` random letters of the alphabet when it has none."""
    return list(letters) if letters is not None else rng.sample(list(alphabet), pairs)
