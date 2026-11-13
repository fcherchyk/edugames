"""S4: the avatar shop's screen (with the "Me" tab), the items' drawings, the look's new options
and the outfit on every screen, driven headless with taps as a child would."""

import time

import pygame
import pytest

from edugames.core import progress
from edugames.core.avatar import (
    ACCESSORY_SLOTS,
    EYE_COLORS,
    HAIR_STYLES,
    ITEMS,
    PET_KINDS,
    SLOTS,
    Avatar,
    items_for,
    pets_of,
)
from edugames.core.profiles import ProfileStore, new_profile
from edugames.demo import choose_look, click, finish_look, type_text, win_memory_game
from edugames.ui import style
from edugames.ui.avatar_draw import FIGURE, SHOES, draw_avatar, draw_head, sprite_for
from edugames.ui.items_draw import DRAWINGS, item_icon
from edugames.ui.look_picker import (
    CATEGORIES,
    CHOICES,
    OPEN_COLOR,
    PARTS,
    SPARKLE_MS,
    mirror,
    mirror_look,
    mirror_point,
    option_name,
)
from edugames.ui.scenes import path as path_module
from edugames.ui.scenes.home import HomeScene
from edugames.ui.scenes.level import VICTORY_AVATAR, new_item_tiles
from edugames.ui.scenes.memory import MemoryScene
from edugames.ui.scenes.path import PathScene
from edugames.ui.scenes.profiles import ProfileSelectScene, tile_rect
from edugames.ui.scenes.shop import (
    CHEER_MS,
    MIRROR_CENTER,
    MIRROR_RADIUS,
    OPEN_TAB_COLOR,
    TABS,
    ShopScene,
    tag_rect,
)
from edugames.ui.widgets import fitting_size, name_tag

DRESSED = Avatar(
    hair_style="spiky",
    head="wizard_hat",  # the tallest
    eyes="ski_goggles",
    back="dragon_wings",  # among the widest
    feet="rocket_boots",  # flames under the feet
    pet="baby_dragon",  # the pet reaching furthest right
)


def start_as(app, coins: int = 0, age: int = 5, look: Avatar | None = None) -> None:
    profile = app.store.add(new_profile("Sam", age, look))
    profile.coins = coins
    if look:
        profile.owned_items = [getattr(look, slot) for slot in ACCESSORY_SLOTS]
    app.scene = ProfileSelectScene(app)
    click(app, "profile:Sam")


def open_shop(app, coins: int = 0) -> ShopScene:
    start_as(app, coins)
    click(app, "shop")
    assert isinstance(app.scene, ShopScene)
    return app.scene


def count_color(surface: pygame.Surface, color, tolerance: int = 12) -> int:
    threshold = (tolerance, tolerance, tolerance, 255)
    return pygame.mask.from_threshold(surface, color, threshold).count()


def drawn_box(draw) -> pygame.Rect:
    """Where `draw(surface)` puts something on an empty screen."""
    surface = pygame.Surface(style.SIZE, pygame.SRCALPHA)
    draw(surface)
    return surface.get_bounding_rect()


# S4_AC1: the shop replaces the wardrobe


def test_S4_AC1_home_opens_the_shop_and_home_goes_back(app) -> None:
    start_as(app)
    button = app.scene.button("shop")

    assert min(button.rect.size) >= style.MIN_TARGET and button.label == ""  # drawn: crown, word
    click(app, "shop")
    assert isinstance(app.scene, ShopScene) and app.scene.tab == "head"
    click(app, "back")
    assert isinstance(app.scene, HomeScene)


def test_S4_AC1_the_tabs_show_the_items_of_their_slot(app) -> None:
    scene = open_shop(app)
    tabs = [b.name for b in scene.buttons if b.name.startswith("tab:")]

    assert tabs == [
        "tab:me",
        "tab:head",
        "tab:eyes",
        "tab:back",
        "tab:feet",
        "tab:pet",
        "tab:shirt",
    ]

    for slot in SLOTS:
        click(app, f"tab:{slot}")
        names = [b.name for b in scene.buttons]
        assert scene.tab == slot and scene.button(f"tab:{slot}").color == OPEN_TAB_COLOR
        things = pets_of(scene.pet_kind) if slot == "pet" else items_for(slot)  # S4_AC20
        assert [n for n in names if n.startswith(f"{slot}:")] == [
            f"{slot}:{thing.id}" for thing in things
        ]
        others = set(SLOTS) - {slot}
        assert not [n for n in names if ":" in n and n.split(":")[0] in others]
        assert all(not b.selected for b in scene.buttons if b.name.startswith("tab:"))


def test_S4_AC1_every_tile_is_big_and_fits_on_screen(app) -> None:
    scene = open_shop(app)
    screen = pygame.Rect((0, 0), style.SIZE)

    pages = [(tab, None) for tab in TABS] + [("pet", kind) for kind in PET_KINDS]
    for tab, kind in pages:
        click(app, f"tab:{tab}")
        if kind:
            click(app, f"kind:{kind}")
        tiles = [b.rect for b in scene.buttons if b.name != "back"]
        assert all(min(rect.size) >= style.MIN_TARGET for rect in tiles)
        assert all(screen.contains(rect) for rect in tiles)
        assert all(a.collidelist([b for b in tiles if b is not a]) == -1 for a in tiles)


# S4_AC3: every item is drawn in the art style


@pytest.mark.parametrize("item_id", sorted(ITEMS))
def test_S4_AC3_every_item_changes_the_avatar_with_the_navy_outline(app, item_id) -> None:
    slot = ITEMS[item_id].slot
    for hair in HAIR_STYLES[::2]:
        for celebrating in (False, True):
            plain, dressed = (pygame.Surface((440, 500), pygame.SRCALPHA) for _ in range(2))
            draw_avatar(plain, Avatar(hair_style=hair), (220, 290), 340, celebrating)
            draw_avatar(
                dressed, Avatar(hair_style=hair, **{slot: item_id}), (220, 290), 340, celebrating
            )

            assert count_color(dressed, style.OUTLINE) > 500
            assert pygame.image.tobytes(plain, "RGBA") != pygame.image.tobytes(dressed, "RGBA")


def test_S4_AC3_every_item_has_an_icon_for_its_tile(app) -> None:
    assert set(DRAWINGS) == set(ITEMS)
    for item_id in ITEMS:
        icon = item_icon(item_id, 100)
        box = icon.get_bounding_rect()
        assert max(box.size) >= 95 and max(icon.get_size()) <= 100, item_id
        assert count_color(icon, style.OUTLINE, 40) > 20, item_id
        shape = item_icon(item_id, 100, silhouette=True)
        flat = pygame.mask.from_threshold(shape, (*style.MUTED, 255), (1, 1, 1, 1)).count()
        assert flat == pygame.mask.from_surface(shape).count() > 0, item_id  # one flat colour


def test_S4_AC3_the_body_keeps_its_size_and_place(app) -> None:
    plain = drawn_box(lambda s: draw_avatar(s, Avatar(), (640, 400), 380))
    before_the_shop = sprite_for(tuple(vars(Avatar()).values()), 380, False, FIGURE)
    old = drawn_box(lambda s: s.blit(before_the_shop, before_the_shop.get_rect(center=(640, 400))))
    winged = drawn_box(lambda s: draw_avatar(s, Avatar(back="bird_wings"), (640, 400), 380))
    hatted = drawn_box(lambda s: draw_avatar(s, Avatar(head="wizard_hat"), (640, 400), 380))

    assert winged.w > plain.w * 1.25 and winged.centerx == pytest.approx(plain.centerx, abs=2)
    assert hatted.top < plain.top - 60 and hatted.bottom == plain.bottom
    assert abs(plain.x - old.x) <= 1 and abs(plain.y - old.y) <= 1  # where it was before S4
    assert abs(plain.w - old.w) <= 1 and abs(plain.h - old.h) <= 1


def test_S4_AC3_an_item_without_a_drawing_draws_nothing(app) -> None:
    assert item_icon("top_hat", 80).get_bounding_rect().w == 0
    surface = pygame.Surface((300, 300), pygame.SRCALPHA)
    look = Avatar()
    look.head = "top_hat"  # as if an item was dropped from the code but not from a look
    draw_avatar(surface, look, (150, 150), 260)
    assert surface.get_bounding_rect().h > 200


def test_S4_AC3_an_item_is_drawn_once_and_then_reused(app) -> None:
    surface = pygame.Surface((300, 300))
    look = Avatar(head="crown", eyes="heart_glasses", back="cape")
    draw_avatar(surface, look, (150, 150), 153)
    item_icon("crown", 77)
    hits, icon_hits = sprite_for.cache_info().hits, item_icon.cache_info().hits

    draw_avatar(surface, look, (150, 150), 153)
    item_icon("crown", 77)

    assert sprite_for.cache_info().hits == hits + 1
    assert item_icon.cache_info().hits == icon_hits + 1


# S4_AC4: items of a world not won yet


def test_S4_AC4_a_closed_item_is_a_grey_shape_with_a_padlock_and_does_nothing(app) -> None:
    scene = open_shop(app, coins=100)
    hat = scene.button("head:woolly_hat")

    assert not hat.enabled and hat.color == style.PANEL
    click(app, "head:woolly_hat")
    assert scene.trying is None and app.profile.coins == 100
    app.step([], 16)
    assert count_color(app.surface, style.MUTED, 6) > 500  # the grey shapes

    progress.record_win(app.profile, "memory", "4", 2)  # the snow world
    click(app, "back")
    click(app, "shop")
    assert app.scene.button("head:woolly_hat").enabled


# S4_AC5: try before buying


def test_S4_AC5_an_item_is_tried_on_for_free(app, tmp_path) -> None:
    scene = open_shop(app, coins=40)
    saved = app.store.path.read_text()

    click(app, "head:crown")

    assert scene.trying == ITEMS["crown"] and scene.look.head == "crown"
    assert scene.button("head:crown").selected  # the gold ring: it is on the avatar
    assert scene.button("buy").enabled and scene.button("buy").primary
    assert app.profile.avatar.head == "" and app.profile.coins == 40
    assert app.store.path.read_text() == saved  # nothing saved, nothing spent


def test_S4_AC5_tapping_again_changing_tab_or_leaving_ends_the_try(app) -> None:
    scene = open_shop(app, coins=40)

    click(app, "head:crown")
    click(app, "head:crown")
    assert scene.trying is None and "buy" not in [b.name for b in scene.buttons]

    click(app, "head:party_hat")
    click(app, "tab:back")
    assert scene.trying is None and scene.look.head == ""

    click(app, "back:cape")
    click(app, "back")
    click(app, "shop")
    assert app.scene.trying is None and app.profile.avatar.back == ""
    assert app.profile.coins == 40


# S4_AC6: buying


def test_S4_AC6_buy_spends_the_coins_saves_and_the_avatar_cheers(app) -> None:
    scene = open_shop(app, coins=12)

    click(app, "head:bunny_ears")
    click(app, "buy")

    assert app.profile.coins == 2 and app.profile.avatar.head == "bunny_ears"
    assert "bunny_ears" in app.store.path.read_text()
    assert scene.cheer_ms > 0 and scene.trying is None
    assert "buy" not in [b.name for b in scene.buttons]
    app.step([], CHEER_MS)
    assert scene.cheer_ms == 0


def test_S4_AC6_without_enough_coins_buy_shows_how_far_the_coins_are(app) -> None:
    scene = open_shop(app, coins=7)

    click(app, "head:crown")
    buy = scene.button("buy")
    click(app, "buy")

    assert not buy.enabled and app.profile.coins == 7 and app.profile.owned_items == []
    surface = pygame.Surface(style.SIZE)
    surface.fill(style.WHITE)
    buy.draw(surface)
    inner = buy.rect.inflate(-16, -16)
    gold = pygame.mask.from_threshold(
        surface.subsurface(inner), style.GOLD, (8, 8, 8, 255)
    ).get_bounding_rects()
    filled = max(rect.right for rect in gold)
    assert filled == pytest.approx(inner.w * 7 / 30, abs=4)  # 7 of the 30 coins
    app.step([], 16)
    for item_id, color in (("party_hat", style.WHITE), ("crown", style.LOCKED)):
        tag = tag_rect(scene.button(f"head:{item_id}").rect)
        assert app.surface.get_at((tag.right - 8, tag.centery))[:3] == color  # 5 yes, 30 not yet


# S4_AC7: wearing and taking off


def test_S4_AC7_tapping_an_owned_item_wears_it_and_again_takes_it_off(app) -> None:
    scene = open_shop(app)

    click(app, "head:cap")  # free: worn at once, no Buy button
    assert app.profile.avatar.head == "cap" and "buy" not in [b.name for b in scene.buttons]
    assert "cap" in app.store.path.read_text()
    click(app, "head:cap")
    assert app.profile.avatar.head == ""

    click(app, "tab:eyes")
    click(app, "eyes:round_glasses")
    click(app, "tab:shirt")
    click(app, "shirt:red")  # the shirt being worn stays on
    assert app.profile.avatar.shirt == "red" and app.profile.avatar.eyes == "round_glasses"


def test_S4_AC7_the_outfit_shows_wherever_the_avatar_does(app, monkeypatch) -> None:
    start_as(app, look=DRESSED)
    looks = []
    for module in ("home", "path", "profiles", "level"):
        target = f"edugames.ui.scenes.{module}.draw_avatar"
        monkeypatch.setattr(target, lambda s, look, *a, **k: looks.append(look))

    app.step([], 16)  # home
    app.go(PathScene(app, "memory"))
    app.step([], 16)
    app.go(MemoryScene(app, "memory", "1"))
    win_memory_game(app)
    app.go(ProfileSelectScene(app))
    app.step([], 16)

    assert len(looks) == 4 and all(look == DRESSED for look in looks)


# S4_AC9: the victory pop-up shows what a win opened


def test_S4_AC9_a_win_that_opens_a_world_shows_its_new_items(app) -> None:
    start_as(app)
    app.go(MemoryScene(app, "memory", "1"))
    win_memory_game(app)

    scene = app.scene
    assert [thing.id for thing in scene.new_items] == ["flower_crown", "butterfly_wings", "chick"]
    panel = pygame.Rect(0, 0, 900, 640)
    panel.center = (style.WIDTH // 2, style.HEIGHT // 2)
    assert all(panel.contains(b.rect) for b in scene.buttons)
    app.step([], 16)
    click(app, "path")
    click(app, "back")
    click(app, "shop")
    assert app.scene.button("head:flower_crown").enabled


def test_S4_AC9_a_win_that_opens_nothing_shows_no_new_items(app) -> None:
    start_as(app)
    progress.record_win(app.profile, "rain", "1", 3)  # the meadow is already won
    app.go(MemoryScene(app, "memory", "1"))
    win_memory_game(app)

    assert app.scene.win and app.scene.new_items == []


# S4_AC10: tall hats and wide wings fit on every screen


def test_S4_AC10_a_dressed_avatar_stays_inside_its_player_tile(app) -> None:
    tile = tile_rect(0)
    pets = [Avatar(back="dragon_wings", pet=pet.id) for pet in items_for("pet")]
    for look in (DRESSED, Avatar(head="space_helmet", back="bird_wings"), *pets):
        box = drawn_box(
            lambda s, look=look: draw_avatar(s, look, (tile.centerx, tile.centery - 12), 166)
        )
        assert tile.contains(box), look


def test_S4_AC10_on_home_a_tall_hat_leaves_the_name_and_the_shop_button_clear(app) -> None:
    start_as(app, look=DRESSED)
    avatar = drawn_box(lambda s: draw_avatar(s, DRESSED, (210, 482), 330))
    tag = drawn_box(lambda s: name_tag(s, "Alexandrina", (210, 186)))

    assert not avatar.colliderect(tag)
    assert not avatar.colliderect(app.scene.button("shop").rect)
    assert all(not avatar.colliderect(b.rect) for b in app.scene.buttons)


def test_S4_AC10_on_the_path_the_title_is_drawn_over_a_tall_hat(app, monkeypatch) -> None:
    start_as(app, look=DRESSED)
    order = []
    monkeypatch.setattr(path_module, "draw_avatar", lambda *a, **k: order.append("avatar"))
    scene = PathScene(app, "memory")
    monkeypatch.setattr(scene, "draw_title", lambda *a: order.append("title"))

    scene.draw(app.surface)

    assert order == ["avatar", "title"]


# S4_AC11: drawing stays fast


def test_S4_AC11_sixty_frames_of_the_shop_draw_in_under_a_second(app) -> None:
    start_as(app, coins=100, look=DRESSED)
    click(app, "shop")
    click(app, "tab:back")
    click(app, "back:cape")
    app.step([], 16)  # draws and caches

    start = time.perf_counter()
    for _ in range(60):
        app.step([], 16)

    assert time.perf_counter() - start < 1.0
    click(app, "tab:me")
    click(app, "look:eye_color")
    click(app, "eye_color:green")  # the mirror sparkles
    start = time.perf_counter()
    for _ in range(60):
        app.step([], 16)
    assert time.perf_counter() - start < 1.0


def test_S4_AC10_in_the_victory_popup_the_avatar_leaves_the_new_items_clear(app) -> None:
    start_as(app, look=DRESSED)
    app.go(MemoryScene(app, "memory", "1"))
    win_memory_game(app)
    assert len(app.scene.new_items) == 3
    for pet in items_for("pet"):
        look = Avatar(**{**vars(DRESSED), "pet": pet.id})
        avatar = drawn_box(
            lambda s, look=look: draw_avatar(s, look, *VICTORY_AVATAR, celebrating=True)
        )
        for count in (1, 2, 3, 4):  # a world opens up to four items
            assert avatar.collidelist(new_item_tiles(count)) == -1, pet.id
        assert avatar.collidelist([b.rect for b in app.scene.buttons]) == -1, pet.id


# S4_AC7: shoes and pets


def test_S4_AC7_shoes_replace_the_avatars_own_and_a_pet_sits_beside_it(app) -> None:
    def red_shoes(look: Avatar) -> int:
        surface = pygame.Surface(style.SIZE, pygame.SRCALPHA)
        draw_avatar(surface, look, (640, 400), 380)
        return count_color(surface, SHOES, 6)

    plain = drawn_box(lambda s: draw_avatar(s, Avatar(), (640, 400), 380))
    with_pet = drawn_box(lambda s: draw_avatar(s, Avatar(pet="kitten"), (640, 400), 380))

    assert red_shoes(Avatar()) > 300 and red_shoes(Avatar(feet="sneakers")) == 0
    assert with_pet.left == plain.left and with_pet.right > plain.right + 60
    assert with_pet.bottom <= plain.bottom + 2  # on the same ground


# S4_AC13: a replay gives 2 coins


def test_S4_AC13_the_victory_popup_of_a_replay_shows_2_coins(app, monkeypatch) -> None:
    start_as(app)
    progress.record_win(app.profile, "memory", "1", 1)
    said = []

    def text(surface, words, *args, **kwargs):
        said.append(words)
        return pygame.Rect(600, 400, 100, 40)

    monkeypatch.setattr("edugames.ui.scenes.level.draw_text", text)
    app.go(MemoryScene(app, "memory", "1"))
    win_memory_game(app, mistakes=0)

    assert app.scene.win.stars == 3 and app.scene.win.coins == 2
    assert "+2 coins" in said and app.profile.coins == 3 + 2


# S4_AC14: ages 3 to 7


def test_S4_AC14_the_age_step_offers_3_to_7(app) -> None:
    click(app, "new_player")
    type_text(app, "Sam")
    click(app, "next")

    ages = [b.name for b in app.scene.buttons if b.name.startswith("age:")]
    assert ages == ["age:3", "age:4", "age:5", "age:6", "age:7"]


# S4_AC15: the "Me" tab, one thing at a time


def look_names(field: str) -> list[str]:
    return [option_name(field, value) for value in CHOICES[field]]


def test_S4_AC15_the_me_tab_changes_the_look_for_free_and_saves_it(app) -> None:
    scene = open_shop(app)
    click(app, "head:cap")

    click(app, "tab:me")
    for field, value in (("face", "wink"), ("freckles", True), ("skin", "deep"),
                         ("hair_style", "bun"), ("eye_color", "blue")):  # fmt: skip
        choose_look(app, field, value)
        assert scene.button(option_name(field, value)).selected

    look = app.profile.avatar
    assert (look.face, look.freckles, look.skin, look.hair_style) == ("wink", True, "deep", "bun")
    assert look.eye_color == "blue" and look.head == "cap"  # items stay on
    assert app.profile.coins == 0 and "buy" not in [b.name for b in scene.buttons]
    saved = ProfileStore(app.store.path.parent).get(app.profile.id).avatar
    assert saved == look


def test_S4_AC15_each_chip_shows_only_its_own_choices_big_and_on_screen(app) -> None:
    scene = open_shop(app)
    click(app, "tab:me")
    screen = pygame.Rect((0, 0), style.SIZE)

    chips = [b for b in scene.buttons if b.name.startswith("look:")]
    assert [b.name for b in chips] == [f"look:{category}" for category in CATEGORIES]
    assert scene.picker.category == "face" and scene.button("look:face").color == OPEN_COLOR
    for category in CATEGORIES:
        click(app, f"look:{category}")
        names = [b.name for b in scene.buttons]
        shown = [b for b in scene.buttons if ":" in b.name and b.name.split(":")[0] in CATEGORIES]
        assert [b.name for b in shown] == look_names(category), category
        assert [b.name for b in scene.buttons if b.selected] == [
            option_name(category, getattr(app.profile.avatar, category))
        ]
        rects = [b.rect for b in scene.buttons if b.name != "back"]
        assert all(min(r.size) >= style.MIN_TARGET and screen.contains(r) for r in rects)
        assert all(r.collidelist([o for o in rects if o is not r]) == -1 for r in rects)
        assert "look:" + category in names and scene.button(f"look:{category}").color == OPEN_COLOR
    assert sum(len(CHOICES[c]) for c in CATEGORIES) == 4 + 5 + 5 + 5 + 5 + 2


# S4_AC17: the mirror


def test_S4_AC17_the_me_tab_shows_a_mirror_instead_of_the_whole_avatar(app, monkeypatch) -> None:
    start_as(app, look=DRESSED)
    click(app, "shop")
    drawn = []
    monkeypatch.setattr(
        "edugames.ui.scenes.shop.draw_avatar", lambda *a, **k: drawn.append("avatar")
    )
    monkeypatch.setattr(
        "edugames.ui.look_picker.LookPicker.draw_mirror", lambda *a, **k: drawn.append("mirror")
    )

    app.step([], 16)  # each step (and each click) draws a frame
    click(app, "tab:me")
    app.step([], 16)
    click(app, "tab:pet")

    assert drawn == ["avatar", "mirror", "mirror", "avatar"]


def test_S4_AC17_the_mirror_takes_off_what_hides_the_part_being_chosen(app) -> None:
    look = Avatar(head="crown", eyes="sunglasses", back="cape", pet="kitten")
    helmet = Avatar(head="space_helmet", eyes="hero_mask")

    assert mirror_look(look, "hair_style").head == "" and mirror_look(look, "hair_color").head == ""
    assert mirror_look(look, "hair_style").eyes == "sunglasses"
    for category in ("face", "eye_color", "freckles"):
        assert (
            mirror_look(look, category).eyes == "" and mirror_look(look, category).head == "crown"
        )
    assert mirror_look(look, "skin").outfit() == look.outfit()
    assert all(mirror_look(helmet, category).head == "" for category in CATEGORIES)
    assert mirror_look(look, "face").back == "cape"  # wings, capes and pets stay

    start_as(app, look=DRESSED)
    click(app, "shop")
    click(app, "tab:me")
    click(app, "look:hair_style")
    app.step([], 16)
    assert app.profile.avatar.head == "wizard_hat"  # only the mirror takes it off
    sprite = mirror(tuple(vars(mirror_look(DRESSED, "hair_style")).values()), MIRROR_RADIUS)
    with_hat = mirror(tuple(vars(DRESSED).values()), MIRROR_RADIUS)
    assert pygame.image.tobytes(sprite, "RGBA") != pygame.image.tobytes(with_hat, "RGBA")


def test_S4_AC17_a_choice_sparkles_where_it_changes_the_mirror(app) -> None:
    scene = open_shop(app)
    click(app, "tab:me")
    click(app, "look:eye_color")
    eye = mirror_point(MIRROR_CENTER, MIRROR_RADIUS, PARTS["eye_color"][0])
    app.step([], 16)
    around = pygame.Rect(0, 0, 40, 40)
    around.center = eye
    before = count_color(app.surface.subsurface(around), style.GOLD, 10)

    click(app, "eye_color:green")
    app.step([], SPARKLE_MS // 2)

    assert scene.picker.sparkle_ms > 0
    assert count_color(app.surface.subsurface(around), style.GOLD, 10) > before + 20
    app.step([], SPARKLE_MS)
    assert scene.picker.sparkle_ms == 0


# S4_AC18: words under the pictures


def test_S4_AC18_every_chip_has_its_word_under_its_picture(app, monkeypatch, content) -> None:
    scene = open_shop(app)
    click(app, "tab:me")
    words = []

    def text(surface, word, size, center, *args, **kwargs):
        words.append((word, size, center))
        return pygame.Rect(center, (1, 1))

    monkeypatch.setattr("edugames.ui.widgets.draw_text", text)
    app.step([], 16)
    chips = [scene.button(f"look:{category}").rect for category in CATEGORIES]
    words = [(w, size, c) for w, size, c in words if any(r.collidepoint(c) for r in chips)]

    expected = [content.text(key) for key in ("face", "skin", "hair", "hair_color", "eye_color",
                                              "freckles")]  # fmt: skip
    assert [word for word, _, _ in words] == expected == [
        "Face", "Skin", "Hair", "Hair colour", "Eyes", "Freckles"
    ]  # fmt: skip
    for (word, size, center), category in zip(words, CATEGORIES, strict=True):
        chip = scene.button(f"look:{category}").rect
        assert chip.collidepoint(center) and center[1] > chip.centery  # under the picture
        assert style.title_font(size).size(word)[0] <= chip.w - 14  # fits
    assert fitting_size("Hair colour", 98, 22) < 22 and fitting_size("Eyes", 98, 22) == 22


# S4_AC19: a new player chooses the look step by step


def test_S4_AC19_a_new_player_goes_through_the_look_with_next_and_done(app) -> None:
    click(app, "new_player")
    type_text(app, "Mia")
    click(app, "next")
    click(app, "age:4")
    scene = app.scene

    seen = []
    while "done" not in [b.name for b in scene.buttons]:
        seen.append(scene.picker.category)
        assert scene.button("next").primary
        click(app, "next")
    seen.append(scene.picker.category)

    assert seen == list(CATEGORIES)
    click(app, "look:skin")  # the chips jump to any step
    assert scene.picker.category == "skin" and "next" in [b.name for b in scene.buttons]
    click(app, "back")
    assert scene.step == "look" and scene.picker.category == "face"
    click(app, "back")
    assert scene.step == "age"


# S4_AC16: eye colour and freckles


def test_S4_AC16_every_eye_colour_and_freckles_are_drawn(app) -> None:
    for color, rgb in EYE_COLORS.items():
        surface = pygame.Surface((200, 200), pygame.SRCALPHA)
        draw_head(surface, Avatar(eye_color=color), (100, 110), 70)
        assert count_color(surface, rgb, 4) > 40, color
    plain, freckled = (pygame.Surface((200, 200), pygame.SRCALPHA) for _ in range(2))
    draw_head(plain, Avatar(skin="deep"), (100, 110), 70)
    draw_head(freckled, Avatar(skin="deep", freckles=True), (100, 110), 70)
    shape = pygame.mask.from_surface(plain).count()
    assert pygame.image.tobytes(plain, "RGBA") != pygame.image.tobytes(freckled, "RGBA")
    assert shape == pygame.mask.from_surface(freckled).count()  # dots on the face, not beside it


def test_S4_AC16_a_new_player_chooses_eye_colour_and_freckles(app) -> None:
    click(app, "new_player")
    type_text(app, "Mia")
    click(app, "next")
    click(app, "age:4")

    choose_look(app, "eye_color", "green")
    choose_look(app, "freckles", True)
    finish_look(app)

    look = app.store.profiles[0].avatar
    assert (look.eye_color, look.freckles) == ("green", True)
    assert isinstance(app.scene, HomeScene)


# S4_AC20: pets come in kinds


def test_S4_AC20_the_pets_tab_has_a_chip_per_kind_without_a_price(app, monkeypatch) -> None:
    scene = open_shop(app, coins=30)
    click(app, "tab:pet")
    priced = []
    monkeypatch.setattr(scene, "_draw_price", lambda s, tag, item: priced.append(item.id))

    app.step([], 16)

    chips = [b for b in scene.buttons if b.name.startswith("kind:")]
    assert [b.name for b in chips] == ["kind:cat", "kind:dog", "kind:bird", "kind:monster",
                                       "kind:robot"]  # fmt: skip
    assert [scene.kind_word(kind) for kind in PET_KINDS] == ["Cat", "Dog", "Bird", "Monster",
                                                             "Robot"]  # fmt: skip
    assert scene.pet_kind == "cat" and scene.button("kind:cat").color == OPEN_TAB_COLOR
    assert priced == ["kitten", "ginger_cat", "black_cat", "lion_cub"]  # the pets, not the kinds
    assert all(chip.enabled and min(chip.rect.size) >= style.MIN_TARGET for chip in chips)


def test_S4_AC20_each_kind_shows_only_its_own_pets(app) -> None:
    scene = open_shop(app, coins=30)
    click(app, "tab:pet")

    for kind in PET_KINDS:
        click(app, f"kind:{kind}")
        shown = [b.name for b in scene.buttons if b.name.startswith("pet:")]
        assert shown == [f"pet:{pet.id}" for pet in pets_of(kind)] and 3 <= len(shown) <= 4
        rects = [scene.button(name).rect for name in shown]
        assert len({r.y for r in rects}) == 1  # one row
        middle = (rects[0].left + rects[-1].right) // 2
        assert middle == scene.button("kind:bird").rect.centerx  # centred under the kinds
        if kind == "monster":
            assert not scene.button("pet:baby_dragon").enabled  # the forest is not won yet


def test_S4_AC20_the_tab_opens_on_the_kind_of_the_pet_worn_and_a_new_kind_ends_a_try(app) -> None:
    start_as(app, look=Avatar(pet="owl"))
    app.profile.coins = 30
    click(app, "shop")
    click(app, "tab:pet")
    scene = app.scene

    assert scene.pet_kind == "bird" and scene.button("pet:owl").selected
    click(app, "kind:robot")
    click(app, "pet:robot")
    assert scene.trying == ITEMS["robot"] and scene.look.pet == "robot"
    click(app, "kind:dog")
    assert scene.trying is None and scene.look.pet == "owl"
    click(app, "pet:poodle")
    click(app, "buy")
    assert app.profile.avatar.pet == "poodle" and app.profile.coins == 10
