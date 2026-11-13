"""S4: the avatar shop's rules (no window): the catalogue, opening items by world, buying, wearing,
and saving what is owned and worn."""

import json

import pytest

from edugames.core import progress, shop, storage
from edugames.core.avatar import (
    ACCESSORY_SLOTS,
    ITEMS,
    PET_KINDS,
    SHIRT_COLORS,
    SLOTS,
    Avatar,
    AvatarError,
    item,
    items_for,
    pets_of,
)
from edugames.core.profiles import ProfileStore, new_profile

WORLDS = ("meadow", "beach", "forest", "snow", "space")


def rich(coins: int = 100):
    profile = new_profile("Sam", 5)
    profile.coins = coins
    return profile


# S4_AC2: the catalogue


def test_S4_AC2_the_catalogue_has_hats_glasses_and_wings() -> None:
    counts = {slot: len(items_for(slot)) for slot in SLOTS}

    assert SLOTS == ("head", "eyes", "back", "feet", "pet", "shirt")
    assert counts == {"head": 8, "eyes": 6, "back": 5, "feet": 7, "pet": 18, "shirt": 8}
    # a tab's grid holds two rows of four; pets are shown one kind at a time (S4_AC20)
    assert all(count <= 8 for slot, count in counts.items() if slot != "pet")
    assert not set(ITEMS) & set(SHIRT_COLORS)  # ids are unique across slots
    assert {"crown", "space_helmet", "dragon_wings", "rocket_boots", "kitten"} <= set(ITEMS)


def test_S4_AC2_prices_are_small_round_numbers() -> None:
    prices = [thing.price for thing in ITEMS.values()]

    assert all(0 <= price <= 30 and price % 5 == 0 for price in prices)
    free = [thing.id for thing in ITEMS.values() if thing.price == 0]
    assert free == ["cap", "round_glasses", "sneakers"]  # something to wear from the start
    assert max(prices) == 30 and ITEMS["crown"].price == 30


def test_S4_AC2_each_world_of_the_path_opens_three_or_four_items(content) -> None:
    themes = {level.theme for levels in content.levels.values() for level in levels}
    by_world = {world: [i.id for i in ITEMS.values() if i.world == world] for world in WORLDS}

    assert set(WORLDS) <= themes  # every world can be reached in this locale
    assert {thing.world for thing in ITEMS.values()} - {None} == set(WORLDS)
    assert all(3 <= len(ids) <= 4 for ids in by_world.values()), by_world
    pet_worlds = [i.world for i in ITEMS.values() if i.slot == "pet" and i.world]
    assert sorted(pet_worlds) == sorted(WORLDS)  # each world brings one animal
    assert all(ITEMS[i].price > 0 for ids in by_world.values() for i in ids)


# S4_AC4: items that open with a win in their world


def test_S4_AC4_a_world_item_opens_with_a_win_in_its_world_in_any_game(content) -> None:
    profile = rich()
    snowy = ITEMS["woolly_hat"]

    assert shop.is_open(profile, ITEMS["crown"], content.levels)  # no world: open from the start
    assert not shop.is_open(profile, snowy, content.levels)
    assert shop.worlds_won(profile, content.levels) == set()

    progress.record_win(profile, "rain", "4", 1)  # Letter Rain's level 4 is in the snow

    assert shop.worlds_won(profile, content.levels) == {"snow"}
    assert shop.is_open(profile, snowy, content.levels)
    assert "woolly_hat" in shop.open_items(profile, content.levels)
    progress.record_win(profile, "memory", "4", 1)  # the same world in another game
    assert shop.worlds_won(profile, content.levels) == {"snow"}


def test_S4_AC4_a_closed_item_cannot_be_bought(content) -> None:
    profile = rich()

    with pytest.raises(AvatarError):
        shop.buy(profile, ITEMS["jetpack"], content.levels)

    assert profile.coins == 100 and profile.owned_items == []
    progress.record_win(profile, "memory", "5", 3)  # space
    coins = profile.coins
    shop.buy(profile, ITEMS["jetpack"], content.levels)
    assert profile.coins == coins - 30 and profile.avatar.back == "jetpack"


# S4_AC6: buying


def test_S4_AC6_an_item_is_bought_with_enough_coins_and_worn(content) -> None:
    profile = rich(12)

    shop.buy(profile, ITEMS["bunny_ears"], content.levels)

    assert profile.coins == 2
    assert profile.owns(ITEMS["bunny_ears"]) and profile.owned_items == ["bunny_ears"]
    assert profile.avatar.head == "bunny_ears"


def test_S4_AC6_an_item_is_refused_without_enough_coins_or_when_owned(content) -> None:
    profile = rich(9)

    assert not profile.can_buy(ITEMS["bunny_ears"])
    with pytest.raises(AvatarError):
        shop.buy(profile, ITEMS["bunny_ears"], content.levels)
    assert profile.coins == 9 and profile.avatar.head == ""

    assert profile.owns(ITEMS["cap"]) and not profile.can_buy(ITEMS["cap"])  # free
    with pytest.raises(AvatarError):
        profile.buy(ITEMS["cap"])
    profile.buy(ITEMS["party_hat"])
    with pytest.raises(AvatarError):
        profile.buy(ITEMS["party_hat"])
    assert profile.coins == 4


# S4_AC7: wearing and taking off


def test_S4_AC7_one_item_per_slot_and_only_owned_items_are_worn() -> None:
    profile = rich()
    for thing in ("party_hat", "crown", "hero_mask", "cape"):
        profile.buy(ITEMS[thing])

    for thing in ("party_hat", "crown", "hero_mask", "cape", "round_glasses"):
        profile.wear(ITEMS[thing])

    assert (profile.avatar.head, profile.avatar.eyes, profile.avatar.back) == (
        "crown",
        "round_glasses",
        "cape",
    )
    with pytest.raises(AvatarError):
        profile.wear(ITEMS["bird_wings"])
    assert profile.avatar.wearing(ITEMS["bird_wings"]).back == "bird_wings"  # a try, a copy
    assert profile.avatar.back == "cape"


def test_S4_AC7_hats_glasses_and_wings_come_off_but_a_shirt_does_not() -> None:
    profile = rich()
    profile.wear(ITEMS["cap"])

    profile.take_off("head")

    assert profile.avatar.head == ""
    with pytest.raises(AvatarError):
        profile.take_off("shirt")
    assert profile.avatar.shirt == "red"
    profile.wear(item("shirt", "blue"))
    assert profile.avatar.shirt == "blue"


# S4_AC8: saved on this computer


def test_S4_AC8_items_and_the_outfit_survive_a_restart(tmp_path) -> None:
    store = ProfileStore(tmp_path)
    profile = store.add(rich())
    for thing in ("crown", "cape"):
        profile.buy(ITEMS[thing])
        profile.wear(ITEMS[thing])
    profile.wear(ITEMS["round_glasses"])
    store.save()

    again = ProfileStore(tmp_path).get(profile.id)

    assert again.owned_items == ["crown", "cape"]
    assert again.avatar.outfit() == ("crown", "round_glasses", "cape", "", "", "red")
    assert again.coins == 100 - 40


def test_S4_AC8_old_profiles_load_and_damaged_items_are_dropped(tmp_path) -> None:
    old = {"id": "a", "name": "Old", "age": 5, "avatar": {"face": "grin"}, "owned_shirts": []}
    damaged = {
        "id": "b",
        "name": "Mia",
        "age": 4,
        "avatar": {"head": "top_hat", "eyes": "crown", "back": "cape"},  # unknown, wrong slot
        "owned_items": ["top_hat", "crown", "crown"],
    }
    not_owned = {"id": "c", "name": "Leo", "age": 6, "avatar": {"head": "crown", "eyes": "cap"}}
    broken = {"id": "d", "name": "Ana", "age": 6, "owned_items": 7, "avatar": {"back": "cape"}}
    storage.save_json(tmp_path / "profiles.json", {"profiles": [old, damaged, not_owned, broken]})

    store = ProfileStore(tmp_path)

    by_name = {profile.name: profile for profile in store.profiles}
    assert sorted(by_name) == ["Ana", "Leo", "Mia", "Old"]
    assert by_name["Old"].avatar.outfit() == ("", "", "", "", "", "red")
    assert by_name["Old"].owned_items == [] and by_name["Old"].avatar.face == "grin"
    assert by_name["Mia"].owned_items == ["crown"]
    assert by_name["Mia"].avatar.outfit() == ("", "", "", "", "", "red")  # no cape bought
    assert by_name["Leo"].avatar.head == "" and by_name["Leo"].avatar.eyes == ""
    assert by_name["Ana"].owned_items == [] and by_name["Ana"].avatar.back == ""
    store.save()
    saved = json.loads((tmp_path / "profiles.json").read_text())["profiles"][0]
    assert saved["owned_items"] == [] and saved["avatar"]["head"] == ""


def test_S4_AC8_a_new_look_refuses_an_item_in_the_wrong_slot() -> None:
    for slot in ACCESSORY_SLOTS:
        assert Avatar(**{slot: ""}).validate()
    with pytest.raises(AvatarError):
        Avatar(head="cape").validate()
    with pytest.raises(AvatarError):
        Avatar(eyes="monocle").validate()
    with pytest.raises(AvatarError):
        item("head", "monocle")


# S4_AC9: what a win opens


def test_S4_AC9_newly_opened_lists_what_a_win_opened(content) -> None:
    profile = rich()
    before = shop.open_items(profile, content.levels)

    progress.record_win(profile, "memory", "1", 3)  # the meadow
    after = shop.open_items(profile, content.levels)
    progress.record_win(profile, "rain", "1", 3)  # the meadow again: nothing new

    assert [thing.id for thing in shop.newly_opened(before, after)] == [
        "flower_crown",
        "butterfly_wings",
        "chick",
    ]
    assert shop.newly_opened(after, shop.open_items(profile, content.levels)) == []


# S4_AC20: pets come in kinds


def test_S4_AC20_every_pet_has_a_kind_with_three_or_four_pets() -> None:
    pets = items_for("pet")

    assert PET_KINDS == ("cat", "dog", "bird", "monster", "robot")
    assert all(pet.kind in PET_KINDS for pet in pets)
    assert {kind: len(pets_of(kind)) for kind in PET_KINDS} == {
        "cat": 4, "dog": 4, "bird": 4, "monster": 3, "robot": 3
    }  # fmt: skip
    assert all(item.kind is None for item in ITEMS.values() if item.slot != "pet")
    assert [pet.id for pet in pets_of("bird")] == ["chick", "parrot", "owl", "penguin"]
    assert min(p.price for p in pets) == 10 and all(p.price > 0 for p in pets)  # a pet is a wish
