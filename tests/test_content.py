"""S1_AC5, S1_AC16, S2_AC1 and S3_AC1 to S3_AC6: content per locale, the games offered for each
age, themes, levels per game, rain levels, pictures and the keyboard."""

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
        (4, ["memory", "rain", "letter-sounds"]),
        (5, ["memory", "rain", "letter-sounds", "draw-letters"]),
        (8, ["draw-letters"]),
    ],
)
def test_S1_AC5_games_are_filtered_by_age(content, age, games) -> None:
    assert [game.id for game in content.games_for_age(age)] == games


def test_S1_AC5_playable_games_come_before_the_coming_soon_ones(content) -> None:
    playable = [game.playable for game in content.games_for_age(5)]

    assert playable == sorted(playable, reverse=True)
    assert playable.count(True) == 2


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


# S3_AC1: levels per game


def test_S3_AC1_each_playable_game_loads_its_own_levels(content) -> None:
    playable = [game.id for game in content.games if game.playable]

    assert sorted(content.levels) == sorted(playable) == ["memory", "rain"]
    assert content.memory_levels == content.levels["memory"]
    assert content.level("rain", "6").has_pictures
    assert content.game("rain").title == "Letter Rain"
    with pytest.raises(ContentError):
        content.level("rain", "11")
    with pytest.raises(ContentError):
        content.game("chess")


def test_S3_AC1_a_playable_game_without_levels_is_refused(copy) -> None:
    root, load, edit = copy
    game = {"id": "chess", "title": "Chess", "icon": "K", "min_age": 4, "max_age": 8}
    edit("games.json", lambda d: {"games": d["games"] + [{**game, "playable": True}]})
    with pytest.raises(ContentError, match="No levels"):
        load()

    edit("games.json", lambda d: {"games": d["games"][:-1]})
    edit("rain_levels.json", lambda d: {"levels": []})
    with pytest.raises(ContentError, match="No levels"):
        load()


# S3_AC2: Letter Rain on the home


def test_S3_AC2_letter_rain_is_offered_from_age_4_to_7(content) -> None:
    ages = [age for age in range(3, 9) if "rain" in [g.id for g in content.games_for_age(age)]]

    assert ages == [4, 5, 6, 7]
    assert [game.id for game in content.games_for_age(5)][:2] == ["memory", "rain"]
    assert "first-letter" not in [game.id for game in content.games]


# S3_AC3: rain levels


def test_S3_AC3_english_rain_levels_load(content) -> None:
    levels = content.levels["rain"]

    assert [level.id for level in levels] == [str(n) for n in range(1, 11)]
    assert [level.has_pictures for level in levels] == [False] * 5 + [True] * 5
    assert [level.case for level in levels[:5]] == ["upper", "upper", "lower", "both", "both"]
    assert levels[0].letters == ("A", "M", "O", "S", "T")
    assert levels[4].letters == tuple(content.letters)  # "*": every letter
    assert levels[9].pictures == tuple(content.pictures)  # "*": every picture
    assert [level.at_once for level in levels] == [1, 1, 1, 2, 2, 1, 1, 1, 2, 2]
    assert [level.theme for level in levels[5:]] == ["meadow", "beach", "forest", "snow", "space"]


LETTER_LEVEL = {"id": "1", "letters": ["A", "B"], "goal": 5, "at_once": 1, "fall_seconds": 9}


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ({"pictures": ["cat"]}, "either letters or pictures"),
        ({"letters": None}, "either letters or pictures"),
        ({"letters": ["A", "Ж"]}, "unknown"),
        ({"letters": ["A", "A"]}, "repeated"),
        ({"letters": None, "pictures": ["cat", "unicorn"]}, "unknown"),
        ({"case": "title"}, "case"),
        ({"goal": 0}, "goal"),
        ({"at_once": 0}, "at_once"),
        ({"letters": ["A", "B", "C", "D", "E"], "at_once": 4}, "at_once"),
        ({"letters": ["A"], "at_once": 2}, "at_once"),
        ({"letters": None, "pictures": ["cat"], "at_once": 2}, "at_once"),
        ({"fall_seconds": 0}, "fall_seconds"),
        ({"goal": "many"}, "Malformed"),
    ],
)
def test_S3_AC3_a_wrong_rain_level_is_refused(copy, change, message) -> None:
    _, load, edit = copy
    level = {key: value for key, value in {**LETTER_LEVEL, **change}.items() if value is not None}
    edit("rain_levels.json", lambda d: {"levels": [level]})

    with pytest.raises(ContentError, match=message):
        load()


# S3_AC4: pictures


def test_S3_AC4_english_pictures_load_with_their_first_letter(content) -> None:
    assert len(content.pictures) == 22
    assert content.pictures["cat"].word == "cat" and content.pictures["cat"].letter == "C"
    assert content.pictures["yoyo"].word == "yo-yo"
    for picture in content.pictures.values():
        assert picture.letter == picture.word[0].upper()  # true in English, not in every language
        assert content.word_audio(picture.id).stat().st_size > 1000
    assert not {"N", "Q", "X", "Z"} & {picture.letter for picture in content.pictures.values()}


@pytest.mark.parametrize(
    ("change", "message"),
    [
        (lambda pictures: pictures + [{"id": "cat", "word": "kitty", "letter": "K"}], "Repeated"),
        (lambda pictures: [{**pictures[0], "letter": "Ж"}] + pictures[1:], "unknown letter"),
        (lambda pictures: [{**pictures[0], "word": ""}] + pictures[1:], "needs a word"),
        (lambda pictures: pictures + [{"id": "zebra", "word": "zebra", "letter": "Z"}], "No audio"),
    ],
)
def test_S3_AC4_a_wrong_picture_is_refused(copy, change, message) -> None:
    _, load, edit = copy
    edit("pictures.json", lambda d: {"pictures": change(d["pictures"])})

    with pytest.raises(ContentError, match=message):
        load()


# S3_AC6: the keyboard


def test_S3_AC6_the_keyboard_has_every_letter_once(content) -> None:
    assert ["".join(row) for row in content.keyboard] == ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]
    keys = [key for row in content.keyboard for key in row]
    assert sorted(keys) == sorted(content.letters)


@pytest.mark.parametrize(
    "rows",
    [
        ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBN"],  # no M
        ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNMM"],  # M twice
        ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM", "Ñ"],  # not a letter of this language
    ],
)
def test_S3_AC6_a_wrong_keyboard_is_refused(copy, rows) -> None:
    _, load, edit = copy
    edit("keyboard.json", lambda d: {"rows": [list(row) for row in rows]})

    with pytest.raises(ContentError, match="keyboard"):
        load()
