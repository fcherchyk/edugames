"""Game content per locale: letters, games, levels per game, pictures, the keyboard, UI strings
and audio.

Everything a translation changes lives in `content/<locale>/` and `assets/audio/<locale>/`, so a new
language is new content, not new code.
"""

import json
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PACKAGE_DIR = Path(__file__).resolve().parent.parent
CONTENT_DIR = PACKAGE_DIR / "content"
ASSETS_DIR = PACKAGE_DIR / "assets"
DEFAULT_LOCALE = "en"
RANDOM_LETTERS = "*"
EVERY = "*"  # a rain level's letters or pictures: all of them
DEFAULT_THEME = "meadow"
CASES = ("upper", "lower", "both")
MAX_AT_ONCE = 3


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
class Picture:
    """A language-neutral concept (its id, drawn in code) with this language's word for it."""

    id: str
    word: str
    letter: str  # the uppercase first letter, as this language says it


@dataclass(frozen=True)
class MemoryLevel:
    id: str
    pairs: int
    letters: tuple[str, ...] | None  # None: `pairs` random letters of the alphabet
    theme: str = DEFAULT_THEME  # the scenery drawn behind the level (a name the UI knows)


@dataclass(frozen=True)
class RainLevel:
    """A Letter Rain level: letters fall (in `case`), or pictures fall (their first letter)."""

    id: str
    goal: int  # right answers that end the level
    at_once: int  # how many items fall at the same time
    fall_seconds: float  # from the top to the ground, at normal speed
    letters: tuple[str, ...] = ()  # uppercase letters, for a letter level
    pictures: tuple[str, ...] = ()  # picture ids, for a picture level
    case: str = "upper"
    theme: str = DEFAULT_THEME

    @property
    def has_pictures(self) -> bool:
        return bool(self.pictures)


Level = MemoryLevel | RainLevel


@dataclass(frozen=True)
class Content:
    locale: str
    letters: dict[str, Letter]
    games: tuple[Game, ...]
    levels: dict[str, tuple[Level, ...]]  # game id -> its levels, in the order of the path
    pictures: dict[str, Picture]
    keyboard: tuple[tuple[str, ...], ...]  # the rows of the on-screen keyboard
    strings: dict[str, str]
    audio_dir: Path

    @property
    def memory_levels(self) -> tuple[MemoryLevel, ...]:
        return self.levels["memory"]  # type: ignore[return-value]

    def text(self, key: str, **values: object) -> str:
        return self.strings.get(key, key).format(**values)

    def letter_audio(self, upper: str) -> Path:
        return self.audio_dir / "letters" / f"{self.letters[upper].lower}.wav"

    def word_audio(self, picture_id: str) -> Path:
        return self.audio_dir / "words" / f"{picture_id}.wav"

    def games_for_age(self, age: int) -> list[Game]:
        """The games for this age, playable ones first (the others show as "coming soon")."""
        suitable = [game for game in self.games if game.suits(age)]
        return sorted(suitable, key=lambda game: not game.playable)

    def game(self, game_id: str) -> Game:
        for game in self.games:
            if game.id == game_id:
                return game
        raise ContentError(f"No game {game_id!r}")

    def level(self, game_id: str, level_id: str) -> Level:
        for level in self.levels.get(game_id, ()):
            if level.id == level_id:
                return level
        raise ContentError(f"No level {level_id!r} in {game_id!r}")

    def memory_level(self, level_id: str) -> MemoryLevel:
        return self.level("memory", level_id)  # type: ignore[return-value]


def _read(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ContentError(f"Cannot read {path}: {error}") from error


def _memory_level(item: dict[str, Any], letters: dict, pictures: dict) -> MemoryLevel:
    chosen = item["letters"]
    return MemoryLevel(
        id=str(item["id"]),
        pairs=int(item["pairs"]),
        letters=None if chosen == RANDOM_LETTERS else tuple(chosen),
        theme=item.get("theme", DEFAULT_THEME),
    )


def _every(chosen: Any, known: dict) -> tuple[str, ...]:
    return tuple(known) if chosen == EVERY else tuple(chosen)


def _rain_level(item: dict[str, Any], letters: dict, pictures: dict) -> RainLevel:
    level_id = str(item["id"])
    if ("letters" in item) == ("pictures" in item):
        raise ContentError(f"Rain level {level_id}: needs either letters or pictures")
    return RainLevel(
        id=level_id,
        goal=int(item["goal"]),
        at_once=int(item["at_once"]),
        fall_seconds=float(item["fall_seconds"]),
        letters=_every(item["letters"], letters) if "letters" in item else (),
        pictures=_every(item["pictures"], pictures) if "pictures" in item else (),
        case=item.get("case", "upper"),
        theme=item.get("theme", DEFAULT_THEME),
    )


LevelParser = Callable[[dict[str, Any], dict, dict], Level]
LEVEL_PARSERS: dict[str, LevelParser] = {"memory": _memory_level, "rain": _rain_level}


def _levels(base: Path, game: Game, letters: dict, pictures: dict) -> tuple[Level, ...]:
    """A playable game's levels, from `<game id>_levels.json`."""
    parse = LEVEL_PARSERS.get(game.id)
    if parse is None:
        raise ContentError(f"No levels for game {game.id!r}")
    items = _read(base / f"{game.id}_levels.json")["levels"]
    if not items:
        raise ContentError(f"No levels for game {game.id!r}")
    return tuple(parse(item, letters, pictures) for item in items)


def _check_memory(content: Content, level: MemoryLevel) -> None:
    if level.letters is None:
        if level.pairs > len(content.letters):
            raise ContentError(f"Level {level.id}: more pairs than letters")
        return
    unknown = [letter for letter in level.letters if letter not in content.letters]
    if unknown:
        raise ContentError(f"Level {level.id}: unknown letters {unknown}")
    if len(set(level.letters)) != level.pairs:
        raise ContentError(f"Level {level.id}: needs {level.pairs} different letters")


def _check_rain(content: Content, level: RainLevel) -> None:
    name = f"Rain level {level.id}"
    chosen, known = (
        (level.pictures, content.pictures)
        if level.has_pictures
        else (level.letters, content.letters)
    )
    unknown = [key for key in chosen if key not in known]
    if unknown:
        raise ContentError(f"{name}: unknown {unknown}")
    if len(set(chosen)) != len(chosen):
        raise ContentError(f"{name}: repeated letters or pictures")
    if not level.has_pictures and level.case not in CASES:
        raise ContentError(f"{name}: the case must be one of {CASES}")
    if level.goal < 1:
        raise ContentError(f"{name}: the goal must be at least 1")
    answers = {content.pictures[key].letter for key in chosen} if level.has_pictures else chosen
    if not 1 <= level.at_once <= min(MAX_AT_ONCE, len(set(answers))):
        raise ContentError(f"{name}: at_once must be 1 to {MAX_AT_ONCE}, and no more than letters")
    if level.fall_seconds <= 0:
        raise ContentError(f"{name}: fall_seconds must be positive")


def _check_pictures(content: Content, ids: list[str]) -> None:
    if len(set(ids)) != len(ids):
        raise ContentError("Repeated picture ids")
    for picture in content.pictures.values():
        if picture.letter not in content.letters:
            raise ContentError(f"Picture {picture.id}: unknown letter {picture.letter!r}")
        if not isinstance(picture.word, str) or not picture.word:
            raise ContentError(f"Picture {picture.id}: needs a word")
    missing = [key for key in content.pictures if not content.word_audio(key).is_file()]
    if missing:
        raise ContentError(f"No audio for pictures {missing} in {content.audio_dir}")


def _check_keyboard(content: Content) -> None:
    keys = [key for row in content.keyboard for key in row]
    if sorted(keys) != sorted(content.letters):
        raise ContentError("The keyboard must have every letter exactly once")


def _check(content: Content, picture_ids: list[str]) -> None:
    for game_levels in content.levels.values():
        for level in game_levels:
            if not isinstance(level.theme, str) or not level.theme:
                raise ContentError(f"Level {level.id}: the theme must be a name")
            if isinstance(level, MemoryLevel):
                _check_memory(content, level)
            else:
                _check_rain(content, level)
    _check_pictures(content, picture_ids)
    _check_keyboard(content)
    missing = [upper for upper in content.letters if not content.letter_audio(upper).is_file()]
    if missing:
        raise ContentError(f"No audio for letters {missing} in {content.audio_dir}")


def load_content(
    locale: str = DEFAULT_LOCALE, content_dir: Path = CONTENT_DIR, assets_dir: Path = ASSETS_DIR
) -> Content:
    base = content_dir / locale
    try:
        letters = {
            item["upper"]: Letter(
                item["upper"], item["lower"], item["spoken"], bool(item.get("vowel"))
            )
            for item in _read(base / "letters.json")["letters"]
        }
        picture_items = _read(base / "pictures.json")["pictures"]
        pictures = {
            item["id"]: Picture(str(item["id"]), item["word"], item["letter"])
            for item in picture_items
        }
        games = tuple(Game(**item) for item in _read(base / "games.json")["games"])
        content = Content(
            locale=locale,
            letters=letters,
            games=games,
            levels={
                game.id: _levels(base, game, letters, pictures) for game in games if game.playable
            },
            pictures=pictures,
            keyboard=tuple(tuple(row) for row in _read(base / "keyboard.json")["rows"]),
            strings=dict(_read(base / "strings.json")),
            audio_dir=assets_dir / "audio" / locale,
        )
    except ContentError:
        raise
    except (KeyError, TypeError, ValueError) as error:
        raise ContentError(f"Malformed content in {base}: {error!r}") from error
    _check(content, [str(item["id"]) for item in picture_items])
    return content
