"""Player profiles: name, age, avatar, coins, wardrobe and progress, saved on this computer."""

import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from edugames.core import storage
from edugames.core.avatar import SHIRT_COLORS, Avatar, AvatarError

NAME_MAX_LENGTH = 12
MIN_AGE, MAX_AGE = 3, 8
MAX_PROFILES = 6
PROFILES_FILE = "profiles.json"


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


def check_age(age: int) -> int:
    if not MIN_AGE <= age <= MAX_AGE:
        raise ProfileError(f"Age must be {MIN_AGE} to {MAX_AGE}")
    return age


@dataclass
class Profile:
    name: str
    age: int
    avatar: Avatar = field(default_factory=Avatar)
    coins: int = 0
    owned_shirts: list[str] = field(default_factory=list)
    # game id -> level id -> best stars (1 to 3); a level is here once it was won
    progress: dict[str, dict[str, int]] = field(default_factory=dict)
    id: str = field(default_factory=lambda: uuid.uuid4().hex)

    def owns_shirt(self, color: str) -> bool:
        return SHIRT_COLORS[color].price == 0 or color in self.owned_shirts

    def can_buy_shirt(self, color: str) -> bool:
        return not self.owns_shirt(color) and self.coins >= SHIRT_COLORS[color].price

    def buy_shirt(self, color: str) -> None:
        if self.owns_shirt(color):
            raise AvatarError(f"Already owned: {color}")
        price = SHIRT_COLORS[color].price
        if self.coins < price:
            raise AvatarError(f"Not enough coins for {color}: {self.coins} < {price}")
        self.coins -= price
        self.owned_shirts.append(color)

    def wear_shirt(self, color: str) -> None:
        if not self.owns_shirt(color):
            raise AvatarError(f"Not owned: {color}")
        self.avatar.shirt = color

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Profile":
        return cls(
            id=str(data["id"]),
            name=clean_name(data["name"]),
            age=check_age(int(data["age"])),
            avatar=Avatar(**data.get("avatar", {})).validate(),
            coins=max(0, int(data.get("coins", 0))),
            owned_shirts=[c for c in data.get("owned_shirts", []) if c in SHIRT_COLORS],
            progress={
                game: {level: int(stars) for level, stars in levels.items()}
                for game, levels in data.get("progress", {}).items()
            },
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
        for item in data.get("profiles", []):
            try:
                profiles.append(Profile.from_dict(item))
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
