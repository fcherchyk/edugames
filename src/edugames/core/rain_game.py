"""Letter Rain: letters or pictures fall, and the child presses the letter that clears them.

The gentle fall: nothing is lost. An item that reaches the ground bounces back up, there are no
lives and no game over, the speed adapts to the child, and a level ends after a number of right
answers. Positions are shares of the fall (0 is the top, 1 the ground), never pixels.
"""

import random
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from enum import Enum, auto

LANES = 5
STREAK = 3  # right answers in a row that make the rain faster
SPEED_UP, MAX_SPEED = 1.15, 1.6
SLOW_DOWN, MIN_SPEED = 0.8, 0.5
RISE_SHARE = 0.5  # going back up takes half the fall time
FIRST_MS = 500  # before the first item of a level
NEXT_MS = 600  # after an item is found, before the next one
SPACING = 0.45  # share of the fall time between two items falling together
CHOICES = 3  # letters to choose from, for the youngest on picture levels
CHOICES_BELOW_AGE = 5


@dataclass(frozen=True)
class Item:
    """Something that can fall: a letter as shown ("b"), or a picture id."""

    answer: str  # the uppercase letter that clears it
    shows: str
    picture: bool = False


@dataclass
class Drop:
    """An item in flight."""

    item: Item
    lane: int
    y: float = 0.0
    rising: bool = False
    choices: tuple[str, ...] = ()  # the letters to choose from, in choices mode


class Press(Enum):
    HIT = auto()
    MISS = auto()
    IGNORED = auto()  # nothing is falling, or the level is over


@dataclass(frozen=True)
class Answer:
    result: Press
    drop: Drop | None = None  # the drop cleared (HIT) or the one most likely aimed at (MISS)


@dataclass
class Changes:
    """What happened during `advance`."""

    appeared: list[Drop] = field(default_factory=list)
    bounced: list[Drop] = field(default_factory=list)


def letter_items(letters: Iterable[tuple[str, str]], case: str) -> list[Item]:
    """Items for (upper, lower) letters in `case`: `upper`, `lower` or `both` (each, half the
    time)."""
    forms = {"upper": (0,), "lower": (1,), "both": (0, 1)}[case]
    return [Item(pair[0], pair[form]) for pair in letters for form in forms]


def picture_items(pictures: Iterable[tuple[str, str]]) -> list[Item]:
    """Items for (picture id, first letter) pairs: the first letter clears the picture."""
    return [Item(letter, picture_id, picture=True) for picture_id, letter in pictures]


def choices_for(
    answer: str, pool: Sequence[str], alphabet: Sequence[str], rng: random.Random
) -> tuple[str, ...]:
    """The answer and two other letters, from `pool` when it has enough (else from the
    alphabet), shuffled."""
    from_pool = sorted(set(pool) - {answer})
    if len(from_pool) >= CHOICES - 1:
        picked = rng.sample(from_pool, CHOICES - 1)
    else:
        rest = [letter for letter in alphabet if letter != answer and letter not in from_pool]
        picked = from_pool + rng.sample(rest, CHOICES - 1 - len(from_pool))
    letters = [answer, *picked]
    rng.shuffle(letters)
    return tuple(letters)


class RainGame:
    def __init__(
        self,
        items: Sequence[Item],
        goal: int,
        at_once: int,
        fall_seconds: float,
        rng: random.Random,
        *,
        choices: bool = False,
        alphabet: Sequence[str] = (),
    ) -> None:
        """`choices`: the youngest choose among three letters, with one item at a time."""
        self.items = list(items)
        self.goal = goal
        self.at_once = 1 if choices else at_once
        self.fall_seconds = fall_seconds
        self.rng = rng
        self.choices = choices
        self.alphabet = list(alphabet)
        self.drops: list[Drop] = []
        self.hits = 0
        self.misses = 0  # wrong letters and bounces
        self.bounces = 0
        self.streak = 0
        self.speed = 1.0
        self.spawn_in = FIRST_MS
        self.last_answer: str | None = None

    @property
    def done(self) -> bool:
        return self.hits >= self.goal

    @property
    def fall_ms(self) -> float:
        return self.fall_seconds * 1000 / self.speed

    def advance(self, dt_ms: float) -> Changes:
        """Move the items, bounce those on the ground, and let new ones appear."""
        changes = Changes()
        if self.done:
            return changes
        for drop in self.drops:
            if drop.rising:
                drop.y -= dt_ms / (self.fall_ms * RISE_SHARE)
                if drop.y <= 0:
                    drop.y, drop.rising = 0.0, False
            else:
                drop.y += dt_ms / self.fall_ms
                if drop.y >= 1:
                    drop.y, drop.rising = 1.0, True
                    changes.bounced.append(drop)
        for _ in changes.bounced:
            self.bounces += 1
            self._miss()
        self.spawn_in -= dt_ms
        if len(self.drops) < self.at_once and self.spawn_in <= 0:
            drop = self._spawn()
            if drop:
                changes.appeared.append(drop)
                self.spawn_in = self.fall_ms * SPACING
        return changes

    def press(self, letter: str) -> Answer:
        """The child pressed `letter` (uppercase): clear the lowest item it answers, or miss."""
        if self.done or not self.drops:
            return Answer(Press.IGNORED)
        matching = [drop for drop in self.drops if drop.item.answer == letter]
        if not matching:
            self._miss()
            return Answer(Press.MISS, self.lowest())
        drop = max(matching, key=lambda d: d.y)
        self.drops.remove(drop)
        self.hits += 1
        self.streak += 1
        if self.streak % STREAK == 0:
            self.speed = min(MAX_SPEED, self.speed * SPEED_UP)
        self.spawn_in = NEXT_MS
        if self.done:
            self.drops.clear()
        return Answer(Press.HIT, drop)

    def lowest(self) -> Drop:
        return max(self.drops, key=lambda d: d.y)

    def _miss(self) -> None:
        self.misses += 1
        self.streak = 0
        self.speed = max(MIN_SPEED, self.speed * SLOW_DOWN)

    def _spawn(self) -> Drop | None:
        falling = {drop.item.answer for drop in self.drops}
        candidates = [item for item in self.items if item.answer not in falling]
        fresh = [item for item in candidates if item.answer != self.last_answer]
        lanes = [lane for lane in range(LANES) if lane not in {d.lane for d in self.drops}]
        if not candidates or not lanes:
            return None
        item = self.rng.choice(fresh or candidates)
        drop = Drop(item, self.rng.choice(lanes))
        if self.choices:
            pool = [other.answer for other in self.items]
            drop.choices = choices_for(item.answer, pool, self.alphabet, self.rng)
        self.drops.append(drop)
        self.last_answer = item.answer
        return drop
