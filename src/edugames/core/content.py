"""Game content per locale: letters, games, memory game levels, UI strings and letter audio.

Everything a translation changes lives in `content/<locale>/` and `assets/audio/<locale>/`, so a new
language is new content, not new code.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PACKAGE_DIR = Path(__file__).resolve().parent.parent
CONTENT_DIR = PACKAGE_DIR / "content"
ASSETS_DIR = PACKAGE_DIR / "assets"
DEFAULT_LOCALE = "en"
RANDOM_LETTERS = "*"
DEFAULT_THEME = "meadow"


class ContentError(ValueError):
    pass


@dataclass(frozen=True)
class Letter:
    upper: str
    lower: str
    spoken: str  # what the text-to-speech voice reads to say the letter's name
    vowel: bool = False  # each language says which of its letters are vowels


@dataclass(frozen=True)
class Game:
    id: str
    title: str
    icon: str
    min_age: int
    max_age: int
    playable: bool

    def suits(self, age: int) -> bool:
        return self.min_age <= age <= self.max_age


@dataclass(frozen=True)
class MemoryLevel:
    id: str
    pairs: int
    letters: tuple[str, ...] | None  # None: `pairs` random letters of the alphabet
    theme: str = DEFAULT_THEME  # the scenery drawn behind the level (a name the UI knows)


@dataclass(frozen=True)
class Content:
    locale: str
    letters: dict[str, Letter]
    games: tuple[Game, ...]
    memory_levels: tuple[MemoryLevel, ...]
    strings: dict[str, str]
    audio_dir: Path

    def text(self, key: str, **values: object) -> str:
        return self.strings.get(key, key).format(**values)

    def letter_audio(self, upper: str) -> Path:
        return self.audio_dir / "letters" / f"{self.letters[upper].lower}.wav"

    def games_for_age(self, age: int) -> list[Game]:
        """The games for this age, playable ones first (the others show as "coming soon")."""
        suitable = [game for game in self.games if game.suits(age)]
        return sorted(suitable, key=lambda game: not game.playable)

    def memory_level(self, level_id: str) -> MemoryLevel:
        for level in self.memory_levels:
            if level.id == level_id:
                return level
        raise ContentError(f"No memory level {level_id!r}")


def _read(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ContentError(f"Cannot read {path}: {error}") from error


def _memory_level(item: dict[str, Any]) -> MemoryLevel:
    letters = item["letters"]
    return MemoryLevel(
        id=str(item["id"]),
        pairs=int(item["pairs"]),
        letters=None if letters == RANDOM_LETTERS else tuple(letters),
        theme=item.get("theme", DEFAULT_THEME),
    )


def _check(content: Content) -> None:
    for level in content.memory_levels:
        if not isinstance(level.theme, str) or not level.theme:
            raise ContentError(f"Level {level.id}: the theme must be a name")
        if level.letters is None:
            if level.pairs > len(content.letters):
                raise ContentError(f"Level {level.id}: more pairs than letters")
            continue
        unknown = [letter for letter in level.letters if letter not in content.letters]
        if unknown:
            raise ContentError(f"Level {level.id}: unknown letters {unknown}")
        if len(set(level.letters)) != level.pairs:
            raise ContentError(f"Level {level.id}: needs {level.pairs} different letters")
    missing = [upper for upper in content.letters if not content.letter_audio(upper).is_file()]
    if missing:
        raise ContentError(f"No audio for letters {missing} in {content.audio_dir}")


def load_content(
    locale: str = DEFAULT_LOCALE, content_dir: Path = CONTENT_DIR, assets_dir: Path = ASSETS_DIR
) -> Content:
    base = content_dir / locale
    try:
        content = Content(
            locale=locale,
            letters={
                item["upper"]: Letter(
                    item["upper"], item["lower"], item["spoken"], bool(item.get("vowel"))
                )
                for item in _read(base / "letters.json")["letters"]
            },
            games=tuple(Game(**item) for item in _read(base / "games.json")["games"]),
            memory_levels=tuple(
                _memory_level(item) for item in _read(base / "memory_levels.json")["levels"]
            ),
            strings=dict(_read(base / "strings.json")),
            audio_dir=assets_dir / "audio" / locale,
        )
    except (KeyError, TypeError) as error:
        raise ContentError(f"Malformed content in {base}: {error!r}") from error
    _check(content)
    return content
