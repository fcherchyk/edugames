"""S1_AC2 to S1_AC4: creating, choosing and saving player profiles."""

import json

import pytest

from edugames.core import storage
from edugames.core.avatar import Avatar, AvatarError
from edugames.core.profiles import (
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


@pytest.mark.parametrize("age", [3, 5, 8])
def test_S1_AC2_ages_3_to_8_are_accepted(age) -> None:
    assert new_profile("Sam", age).age == age


@pytest.mark.parametrize("age", [2, 9, -1])
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
