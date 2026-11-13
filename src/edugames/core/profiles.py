"""Player profiles: name, age, avatar, coins, the items they own, progress, answers and settings,
saved on this computer."""

import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from edugames.core import storage
from edugames.core.avatar import (
    ACCESSORY_SLOTS,
    EYE_COLORS,
    ITEMS,
    NOTHING,
    SHIRT,
    SHIRT_COLORS,
    Avatar,
    AvatarError,
    Item,
    item,
)

NAME_MAX_LENGTH = 12
MIN_AGE, MAX_AGE = 3, 7  # 8 until S4: no game was playable at 8
OLD_MAX_AGE = 8
MAX_PROFILES = 6
PROFILES_FILE = "profiles.json"
ANSWER_KINDS = ("letters", "pictures")
DEFAULT_SETTINGS = {"keyboard": True}  # the on-screen keyboard is shown


class ProfileError(ValueError):
    pass


def clean_name(name: str) -> str:
    """The name without surrounding spaces; 1 to 12 letters, spaces, hyphens or apostrophes."""
    name = " ".join(name.split())
    if not 1 <= len(name) <= NAME_MAX_LENGTH:
        raise ProfileError(f"A name has 1 to {NAME_MAX_LENGTH} characters")
    if not all(char.isalpha() or char in " -'" for char in name):
        raise ProfileError("A name has only letters, spaces, hyphens and apostrophes")
    return name


def load_age(age: int) -> int:
    """A saved age; a player saved as 8 (before S4) is now 7, the oldest age, and keeps playing."""
    return check_age(MAX_AGE if MAX_AGE < age <= OLD_MAX_AGE else age)


def check_age(age: int) -> int:
    if not MIN_AGE <= age <= MAX_AGE:
        raise ProfileError(f"Age must be {MIN_AGE} to {MAX_AGE}")
    return age


@dataclass
class Record:
    """The answers about one letter or picture: how often it was found, and which letter was
    pressed instead of it, how many times."""

    right: int = 0
    wrong: dict[str, int] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Record":
        right = int(data["right"])
        wrong = {str(letter): int(count) for letter, count in data.get("wrong", {}).items()}
        if right < 0 or any(count < 1 for count in wrong.values()):
            raise ValueError("Answer counts cannot be negative, nor a wrong count zero")
        return cls(right, wrong)


def load_answers(data: Any) -> dict[str, dict[str, Record]]:
    """Saved answers; a damaged entry is dropped, the others are kept."""
    answers: dict[str, dict[str, Record]] = {}
    if not isinstance(data, dict):
        return answers
    for kind, records in data.items():
        if kind not in ANSWER_KINDS or not isinstance(records, dict):
            continue
        for key, record in records.items():
            try:
                answers.setdefault(kind, {})[str(key)] = Record.from_dict(record)
            except (AttributeError, KeyError, TypeError, ValueError):
                continue
    return answers


def load_settings(data: Any) -> dict[str, bool]:
    """Saved settings; only known names with a value of the right type are kept."""
    if not isinstance(data, dict):
        return {}
    return {
        name: value
        for name, value in data.items()
        if name in DEFAULT_SETTINGS and isinstance(value, type(DEFAULT_SETTINGS[name]))
    }


def load_owned_items(data: Any) -> list[str]:
    """The items bought; unknown ids (an item no longer in the shop) and repeats are dropped."""
    if not isinstance(data, list):
        return []
    return list(dict.fromkeys(i for i in data if isinstance(i, str) and i in ITEMS))


def load_avatar(data: dict[str, Any], owned_items: list[str]) -> Avatar:
    """A saved look. An item that is unknown (removed from the shop), in the wrong slot or not
    owned is taken off, and an unknown eye colour or freckles value gets the default, so the
    profile still loads; the rest of the look must be valid."""
    data = dict(data)
    if data.get("eye_color", "brown") not in EYE_COLORS:
        data.pop("eye_color")
    if not isinstance(data.get("freckles", False), bool):
        data.pop("freckles")
    for slot in ACCESSORY_SLOTS:
        worn = data.get(slot, NOTHING)
        known = worn in ITEMS and ITEMS[worn].slot == slot
        if not known or (ITEMS[worn].price > 0 and worn not in owned_items):
            data[slot] = NOTHING
    return Avatar(**data).validate()


@dataclass
class Profile:
    name: str
    age: int
    avatar: Avatar = field(default_factory=Avatar)
    coins: int = 0
    owned_shirts: list[str] = field(default_factory=list)
    owned_items: list[str] = field(default_factory=list)  # hats, glasses, wings bought
    # game id -> level id -> best stars (1 to 3); a level is here once it was won
    progress: dict[str, dict[str, int]] = field(default_factory=dict)
    # "letters" or "pictures" -> letter or picture id -> its answers
    answers: dict[str, dict[str, Record]] = field(default_factory=dict)
    settings: dict[str, bool] = field(default_factory=dict)
    id: str = field(default_factory=lambda: uuid.uuid4().hex)

    def owns(self, thing: Item) -> bool:
        owned = self.owned_shirts if thing.slot == SHIRT else self.owned_items
        return thing.price == 0 or thing.id in owned

    def can_buy(self, thing: Item) -> bool:
        return not self.owns(thing) and self.coins >= thing.price

    def buy(self, thing: Item) -> None:
        if self.owns(thing):
            raise AvatarError(f"Already owned: {thing.id}")
        if self.coins < thing.price:
            raise AvatarError(f"Not enough coins for {thing.id}: {self.coins} < {thing.price}")
        self.coins -= thing.price
        (self.owned_shirts if thing.slot == SHIRT else self.owned_items).append(thing.id)

    def wear(self, thing: Item) -> None:
        if not self.owns(thing):
            raise AvatarError(f"Not owned: {thing.id}")
        setattr(self.avatar, thing.slot, thing.id)

    def take_off(self, slot: str) -> None:
        """Take off the item worn in `slot`; a shirt is always worn."""
        if slot not in ACCESSORY_SLOTS:
            raise AvatarError(f"Cannot take off the {slot}")
        setattr(self.avatar, slot, NOTHING)

    def owns_shirt(self, color: str) -> bool:
        return self.owns(item(SHIRT, color))

    def can_buy_shirt(self, color: str) -> bool:
        return self.can_buy(item(SHIRT, color))

    def buy_shirt(self, color: str) -> None:
        self.buy(item(SHIRT, color))

    def wear_shirt(self, color: str) -> None:
        self.wear(item(SHIRT, color))

    def setting(self, name: str) -> bool:
        return self.settings.get(name, DEFAULT_SETTINGS[name])

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Profile":
        owned_items = load_owned_items(data.get("owned_items"))
        return cls(
            id=str(data["id"]),
            name=clean_name(data["name"]),
            age=load_age(int(data["age"])),
            avatar=load_avatar(data.get("avatar", {}), owned_items),
            coins=max(0, int(data.get("coins", 0))),
            owned_shirts=[c for c in data.get("owned_shirts", []) if c in SHIRT_COLORS],
            owned_items=owned_items,
            progress={
                game: {level: int(stars) for level, stars in levels.items()}
                for game, levels in data.get("progress", {}).items()
            },
            answers=load_answers(data.get("answers")),
            settings=load_settings(data.get("settings")),
        )


def new_profile(name: str, age: int, avatar: Avatar | None = None) -> Profile:
    return Profile(
        name=clean_name(name), age=check_age(age), avatar=(avatar or Avatar()).validate()
    )


class ProfileStore:
    """All the profiles of this computer, in `<data dir>/profiles.json`."""

    def __init__(self, data_dir: Path) -> None:
        self.path = data_dir / PROFILES_FILE
        self.profiles = self._load()

    def _load(self) -> list[Profile]:
        data = storage.load_json(self.path) or {}
        profiles = []
        for entry in data.get("profiles", []):
            try:
                profiles.append(Profile.from_dict(entry))
            except (KeyError, TypeError, ValueError):
                continue  # skip a damaged profile, keep the others
        return profiles

    def is_full(self) -> bool:
        return len(self.profiles) >= MAX_PROFILES

    def get(self, profile_id: str) -> Profile:
        for profile in self.profiles:
            if profile.id == profile_id:
                return profile
        raise ProfileError(f"No profile {profile_id}")

    def add(self, profile: Profile) -> Profile:
        if self.is_full():
            raise ProfileError(f"At most {MAX_PROFILES} profiles")
        self.profiles.append(profile)
        self.save()
        return profile

    def save(self) -> None:
        storage.save_json(self.path, {"profiles": [p.to_dict() for p in self.profiles]})
