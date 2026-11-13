"""The avatar shop's rules: which items are open to a player, and buying them.

An item with a `world` opens when the player wins a level of that world (its theme), in any game,
and stays open. Everything is bought with coins earned by winning levels: nothing is random,
nothing is for a limited time, and there is no real money.
"""

from collections.abc import Mapping, Sequence

from edugames.core.avatar import ITEMS, SLOTS, AvatarError, Item, items_for
from edugames.core.content import Level
from edugames.core.profiles import Profile

Levels = Mapping[str, Sequence[Level]]  # game id -> its levels, as in `Content.levels`


def worlds_won(profile: Profile, levels: Levels) -> set[str]:
    """The themes of the levels this player has won, in every game."""
    won = set()
    for game_id, game_levels in levels.items():
        stars = profile.progress.get(game_id, {})
        won.update(level.theme for level in game_levels if stars.get(level.id, 0) > 0)
    return won


def is_open(profile: Profile, item: Item, levels: Levels) -> bool:
    return item.world is None or item.world in worlds_won(profile, levels)


def open_items(profile: Profile, levels: Levels) -> set[str]:
    """The ids of the items (shirts included) this player can see, try on and buy."""
    won = worlds_won(profile, levels)
    return {
        item.id
        for slot in SLOTS
        for item in items_for(slot)
        if item.world is None or item.world in won
    }


def newly_opened(before: set[str], after: set[str]) -> list[Item]:
    """The items a win has just opened (for the victory pop-up), in the shop's order."""
    return [item for item in ITEMS.values() if item.id in after - before]


def buy(profile: Profile, item: Item, levels: Levels) -> None:
    """Buy `item` and put it on. A closed item cannot be bought."""
    if not is_open(profile, item, levels):
        raise AvatarError(f"Not open yet: {item.id} (win a level of the {item.world})")
    profile.buy(item)
    profile.wear(item)
