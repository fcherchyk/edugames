"""S1_AC2 to S1_AC4, S3_AC7, S3_AC15, S4_AC14 and S4_AC16: creating, choosing and saving player
profiles, with their settings, answers and looks."""

import json

import pytest

from edugames.core import progress, storage
from edugames.core.avatar import Avatar, AvatarError
from edugames.core.profiles import (
    MAX_AGE,
    MAX_PROFILES,
    ProfileError,
    ProfileStore,
    clean_name,
    new_profile,
)


@pytest.mark.parametrize("name", ["Sam", "  Ana  María ", "O'Neil", "Jean-Luc", "Ñandú", "A" * 12])
def test_S1_AC2_valid_names_are_accepted_and_trimmed(name) -> None:
    assert clean_name(name) == " ".join(name.split())


@pytest.mark.parametrize("name", ["", "   ", "A" * 13, "Sam3", "<b>", "Sam!"])
def test_S1_AC2_invalid_names_are_refused(name) -> None:
    with pytest.raises(ProfileError):
        clean_name(name)


@pytest.mark.parametrize("age", [3, 5, 7])
def test_S1_AC2_ages_3_to_7_are_accepted(age) -> None:  # 3 to 8 before S4
    assert new_profile("Sam", age).age == age


@pytest.mark.parametrize("age", [2, 8, 9, -1])
def test_S1_AC2_other_ages_are_refused(age) -> None:
    with pytest.raises(ProfileError):
        new_profile("Sam", age)


def test_S1_AC2_an_unknown_avatar_option_is_refused() -> None:
    with pytest.raises(AvatarError):
        new_profile("Sam", 5, Avatar(face="angry"))


def test_S1_AC3_each_profile_keeps_its_own_coins_and_progress(tmp_path) -> None:
    store = ProfileStore(tmp_path)
    sam = store.add(new_profile("Sam", 5))
    ana = store.add(new_profile("Ana", 4))
    sam.coins = 7
    sam.progress["memory"] = {"1": 3}
    store.save()

    loaded = ProfileStore(tmp_path)

    assert loaded.get(sam.id).coins == 7
    assert loaded.get(sam.id).progress == {"memory": {"1": 3}}
    assert loaded.get(ana.id).coins == 0
    assert loaded.get(ana.id).progress == {}


def test_S1_AC3_there_is_a_limit_of_profiles(tmp_path) -> None:
    store = ProfileStore(tmp_path)
    for i in range(MAX_PROFILES):
        store.add(new_profile(f"Kid {'abcdef'[i]}", 5))

    assert store.is_full()
    with pytest.raises(ProfileError):
        store.add(new_profile("One more", 5))


def test_S1_AC3_an_unknown_profile_id_is_an_error(store) -> None:
    with pytest.raises(ProfileError):
        store.get("nope")


def test_S1_AC4_profiles_survive_a_restart(tmp_path) -> None:
    profile = new_profile("Sam", 6, Avatar(face="wink", hair_style="bun", shirt="blue"))
    ProfileStore(tmp_path).add(profile)

    (loaded,) = ProfileStore(tmp_path).profiles

    assert loaded == profile


def test_S1_AC4_the_default_data_dir_is_the_users_data_folder() -> None:
    assert storage.default_data_dir().name == "EduGames"


def test_S1_AC4_saving_replaces_the_file_atomically(tmp_path) -> None:
    store = ProfileStore(tmp_path)
    store.add(new_profile("Sam", 5))

    assert [p.name for p in tmp_path.iterdir()] == ["profiles.json"]  # no temp files left
    assert json.loads((tmp_path / "profiles.json").read_text())["version"] == storage.SCHEMA_VERSION


def test_S1_AC4_a_failed_write_keeps_the_previous_file(tmp_path, monkeypatch) -> None:
    store = ProfileStore(tmp_path)
    store.add(new_profile("Sam", 5))
    before = (tmp_path / "profiles.json").read_text()

    def fail(*args):
        raise OSError("disk full")

    monkeypatch.setattr(storage.os, "replace", fail)
    with pytest.raises(OSError):
        store.add(new_profile("Ana", 5))

    assert (tmp_path / "profiles.json").read_text() == before
    assert [p.name for p in tmp_path.iterdir()] == ["profiles.json"]


@pytest.mark.parametrize("text", ["{not json", '{"profiles": []}', "[]", "\xff\xfe"])
def test_S1_AC4_a_corrupt_file_is_set_aside_instead_of_crashing(tmp_path, text) -> None:
    (tmp_path / "profiles.json").write_text(text, encoding="latin-1")

    store = ProfileStore(tmp_path)

    assert store.profiles == []
    assert (tmp_path / "profiles.json.corrupt").exists()


def test_S1_AC4_a_damaged_profile_is_skipped_and_the_others_load(tmp_path) -> None:
    good = new_profile("Sam", 5).to_dict()
    storage.save_json(tmp_path / "profiles.json", {"profiles": [{"name": "x"}, good]})

    assert [p.name for p in ProfileStore(tmp_path).profiles] == ["Sam"]


def test_S3_AC7_settings_survive_a_restart_and_bad_ones_are_dropped(tmp_path) -> None:
    store = ProfileStore(tmp_path)
    sam = store.add(new_profile("Sam", 5))
    assert sam.setting("keyboard") is True  # shown unless the player hid it

    sam.settings["keyboard"] = False
    store.save()
    assert ProfileStore(tmp_path).get(sam.id).setting("keyboard") is False

    data = json.loads(store.path.read_text())
    data["profiles"][0]["settings"] = {"keyboard": "no", "volume": 11}
    store.path.write_text(json.dumps(data))
    loaded = ProfileStore(tmp_path).get(sam.id)
    assert loaded.settings == {} and loaded.setting("keyboard") is True


def test_S3_AC15_old_profiles_load_and_damaged_answers_are_dropped(tmp_path) -> None:
    store = ProfileStore(tmp_path)
    sam = store.add(new_profile("Sam", 5))
    progress.record_answer(sam, "B", "D", picture="ball")
    store.save()
    assert ProfileStore(tmp_path).get(sam.id).answers == sam.answers

    data = json.loads(store.path.read_text())
    old = {
        key: value
        for key, value in data["profiles"][0].items()
        if key not in ("answers", "settings")
    }
    damaged = {
        "letters": {"A": {"right": 2}, "B": {"right": -1}, "C": "lots", "D": {"wrong": {"B": 1}}},
        "pictures": [1, 2],
        "numbers": {"1": {"right": 1}},
    }
    data["profiles"] = [old, {**old, "id": "two", "name": "Ana", "answers": damaged}]
    store.path.write_text(json.dumps(data))
    loaded = ProfileStore(tmp_path)

    assert [p.name for p in loaded.profiles] == ["Sam", "Ana"]
    assert loaded.get(sam.id).answers == {} and loaded.get(sam.id).settings == {}
    assert list(loaded.get("two").answers) == ["letters"]
    assert list(loaded.get("two").answers["letters"]) == ["A"]  # the damaged ones are dropped


def test_S4_AC14_a_player_saved_as_8_loads_as_7(tmp_path) -> None:
    players = [
        {"id": "a", "name": "Eight", "age": 8},
        {"id": "b", "name": "Nine", "age": 9},
        {"id": "c", "name": "Six", "age": 6},
    ]
    storage.save_json(tmp_path / "profiles.json", {"profiles": players})

    store = ProfileStore(tmp_path)

    assert [(p.name, p.age) for p in store.profiles] == [("Eight", 7), ("Six", 6)]
    assert MAX_AGE == 7


def test_S4_AC16_old_or_damaged_eye_colours_and_freckles_get_the_default(tmp_path) -> None:
    players = [
        {"id": "a", "name": "Old", "age": 5, "avatar": {"face": "wink"}},
        {"id": "b", "name": "Odd", "age": 5, "avatar": {"eye_color": "purple", "freckles": "yes"}},
        {"id": "c", "name": "New", "age": 5, "avatar": {"eye_color": "green", "freckles": True}},
    ]
    storage.save_json(tmp_path / "profiles.json", {"profiles": players})

    looks = {p.name: p.avatar for p in ProfileStore(tmp_path).profiles}

    assert (looks["Old"].eye_color, looks["Old"].freckles) == ("brown", False)
    assert (looks["Odd"].eye_color, looks["Odd"].freckles) == ("brown", False)
    assert (looks["New"].eye_color, looks["New"].freckles) == ("green", True)
    for wrong in ({"eye_color": "purple"}, {"freckles": "yes"}):
        with pytest.raises(AvatarError):
            Avatar(**wrong).validate()
