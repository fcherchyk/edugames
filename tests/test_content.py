"""S1_AC5, S1_AC16 and S2_AC1: content per locale, the games offered for each age, and themes."""

import json
import shutil

import pytest

from edugames.core.content import ASSETS_DIR, CONTENT_DIR, ContentError, load_content


def test_S1_AC16_english_content_loads(content) -> None:
    assert content.locale == "en"
    assert len(content.letters) == 26
    assert content.letters["A"].lower == "a"
    assert [level.id for level in content.memory_levels] == ["1", "2", "3", "4", "5"]
    assert content.text("level", number=2) == "Level 2"
    assert content.text("missing_key") == "missing_key"


def test_S1_AC16_every_letter_has_its_audio_clip(content) -> None:
    for upper in content.letters:
        assert content.letter_audio(upper).stat().st_size > 1000


@pytest.fixture
def copy(tmp_path):
    """A copy of the English content and audio that a test can break."""
    shutil.copytree(CONTENT_DIR / "en", tmp_path / "content" / "en")
    shutil.copytree(ASSETS_DIR / "audio" / "en", tmp_path / "assets" / "audio" / "en")

    def load():
        return load_content("en", tmp_path / "content", tmp_path / "assets")

    def edit(name, change):
        path = tmp_path / "content" / "en" / name
        path.write_text(json.dumps(change(json.loads(path.read_text()))))

    return tmp_path, load, edit


def test_S1_AC16_a_level_with_an_unknown_letter_is_refused(copy) -> None:
    _, load, edit = copy
    edit("memory_levels.json", lambda d: {"levels": [{"id": "1", "pairs": 1, "letters": ["Ж"]}]})

    with pytest.raises(ContentError, match="unknown letters"):
        load()


@pytest.mark.parametrize(
    ("level", "message"),
    [
        ({"id": "1", "pairs": 3, "letters": ["A", "A", "B"]}, "different letters"),
        ({"id": "1", "pairs": 30, "letters": "*"}, "more pairs than letters"),
    ],
)
def test_S1_AC16_a_level_with_wrong_pairs_is_refused(copy, level, message) -> None:
    _, load, edit = copy
    edit("memory_levels.json", lambda d: {"levels": [level]})

    with pytest.raises(ContentError, match=message):
        load()


def test_S1_AC16_a_letter_without_audio_is_refused(copy) -> None:
    root, load, _ = copy
    (root / "assets" / "audio" / "en" / "letters" / "q.wav").unlink()

    with pytest.raises(ContentError, match="No audio"):
        load()


def test_S1_AC16_malformed_or_missing_content_is_an_error(copy) -> None:
    root, load, edit = copy
    edit("games.json", lambda d: {"games": [{"id": "x"}]})
    with pytest.raises(ContentError, match="Malformed"):
        load()

    (root / "content" / "en" / "games.json").unlink()
    with pytest.raises(ContentError, match="Cannot read"):
        load()


def test_S1_AC16_an_unknown_level_is_an_error(content) -> None:
    with pytest.raises(ContentError):
        content.memory_level("99")


@pytest.mark.parametrize(
    ("age", "games"),
    [
        (3, ["memory"]),
        (4, ["memory", "letter-sounds", "first-letter"]),
        (5, ["memory", "letter-sounds", "first-letter", "draw-letters"]),
        (8, ["draw-letters"]),
    ],
)
def test_S1_AC5_games_are_filtered_by_age(content, age, games) -> None:
    assert [game.id for game in content.games_for_age(age)] == games


def test_S1_AC5_playable_games_come_before_the_coming_soon_ones(content) -> None:
    playable = [game.playable for game in content.games_for_age(5)]

    assert playable == sorted(playable, reverse=True)
    assert playable.count(True) == 1


def test_S2_AC1_a_level_whose_theme_is_not_a_name_is_refused(copy) -> None:
    _, load, edit = copy
    edit("memory_levels.json", lambda d: {"levels": [{**d["levels"][0], "theme": 3}]})

    with pytest.raises(ContentError, match="theme"):
        load()


def test_S2_AC1_a_level_without_a_theme_gets_the_meadow(copy) -> None:
    _, load, edit = copy
    level = {"id": "1", "pairs": 1, "letters": ["A"]}
    edit("memory_levels.json", lambda d: {"levels": [level]})

    assert load().memory_levels[0].theme == "meadow"
