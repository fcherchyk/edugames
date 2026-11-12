"""Stars (progress along the goal path), coins (spent in the wardrobe) and the answers given for
each letter and picture."""

from collections.abc import Sequence
from dataclasses import dataclass

from edugames.core.profiles import Profile, Record

MAX_STARS = 3
BASE_COINS = 2


def stars_for(chances: int, mistakes: int) -> int:
    """3 stars with at most one mistake per chance (a pair of cards, a right answer), 2 with at
    most two, else 1 (never 0)."""
    if mistakes <= chances:
        return 3
    if mistakes <= 2 * chances:
        return 2
    return 1


def coins_for(stars: int) -> int:
    return BASE_COINS + stars


def best_stars(profile: Profile, game_id: str, level_id: str) -> int:
    """0 if the level was never won."""
    return profile.progress.get(game_id, {}).get(level_id, 0)


def is_unlocked(profile: Profile, game_id: str, level_ids: Sequence[str], level_id: str) -> bool:
    """The first level is always open; each other one opens when the previous one is won."""
    position = list(level_ids).index(level_id)
    return position == 0 or best_stars(profile, game_id, level_ids[position - 1]) > 0


@dataclass(frozen=True)
class Win:
    stars: int
    coins: int
    new_best: bool


def record_win(profile: Profile, game_id: str, level_id: str, stars: int) -> Win:
    """Add the coins and keep the level's best stars."""
    stars = max(1, min(MAX_STARS, stars))
    previous = best_stars(profile, game_id, level_id)
    if stars > previous:
        profile.progress.setdefault(game_id, {})[level_id] = stars
    coins = coins_for(stars)
    profile.coins += coins
    return Win(stars=stars, coins=coins, new_best=stars > previous)


def record_answer(profile: Profile, letter: str, pressed: str, picture: str | None = None) -> bool:
    """Count an answer about `letter` (and `picture`, on picture levels): right when `pressed` is
    that letter, else counted as `pressed` instead. True if it was right."""
    right = pressed == letter
    keys = [("letters", letter)] + ([("pictures", picture)] if picture else [])
    for kind, key in keys:
        record = profile.answers.setdefault(kind, {}).setdefault(key, Record())
        if right:
            record.right += 1
        else:
            record.wrong[pressed] = record.wrong.get(pressed, 0) + 1
    return right
