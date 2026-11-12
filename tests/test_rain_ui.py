"""S3: the Letter Rain screens, driven headless with key presses and taps as a child would."""

import time

import pygame

from edugames.core.profiles import ProfileStore, new_profile
from edugames.core.rain_game import MIN_SPEED, NEXT_MS
from edugames.demo import click, press_key, wait_for_item, win_rain_game
from edugames.ui import style
from edugames.ui.app import App
from edugames.ui.audio import Audio
from edugames.ui.keyboard import MUTED_KEY, key_label
from edugames.ui.scenes import level_scene
from edugames.ui.scenes.home import HomeScene
from edugames.ui.scenes.memory import MemoryScene
from edugames.ui.scenes.path import NODE, PathScene, avatar_center, node_centers, sizes, stars_rect
from edugames.ui.scenes.profiles import ProfileSelectScene
from edugames.ui.scenes.rain import FLASH_MS, HIT_FLASH, MISS_FLASH, RainScene

SCREEN = pygame.Rect((0, 0), style.SIZE)


class Recorder(Audio):
    """Keeps what the game asked to say, and still says it."""

    def __init__(self, content) -> None:
        super().__init__(content)
        self.said: list[tuple[str, ...]] = []

    def say_letter(self, upper: str, **options) -> bool:
        self.said.append(("letter", upper))
        return super().say_letter(upper, **options)

    def say_word(self, picture_id: str, **options) -> bool:
        self.said.append(("word", picture_id))
        return super().say_word(picture_id, **options)

    def say_letter_and_word(self, upper: str, picture_id: str) -> bool:
        self.said.append(("letter+word", upper, picture_id))
        return super().say_letter_and_word(upper, picture_id)


def start_as(app: App, age: int = 5, name: str = "Sam") -> None:
    app.store.add(new_profile(name, age))
    app.scene = ProfileSelectScene(app)
    click(app, f"profile:{name}")


def play(app: App, level: str, age: int = 5) -> RainScene:
    start_as(app, age)
    app.go(RainScene(app, "rain", level))
    return app.scene


def tap(app: App, pos) -> None:
    app.step([pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=pos)], 16)


def key_down(app: App, text: str) -> None:
    app.step([pygame.event.Event(pygame.KEYDOWN, key=0, unicode=text)], 16)


def names(scene, prefix: str) -> list[str]:
    return [button.name for button in scene.buttons if button.name.startswith(prefix)]


def not_falling(scene: RainScene) -> str:
    falling = {drop.item.answer for drop in scene.game.drops}
    return next(letter for letter in scene.content.letters if letter not in falling)


# S3_AC1: levels per game


def test_S3_AC1_each_path_shows_its_game_levels_and_opens_its_game(app) -> None:
    start_as(app)
    for game_id, scene_type in (("memory", MemoryScene), ("rain", RainScene)):
        app.go(PathScene(app, game_id))
        levels = app.content.levels[game_id]
        assert names(app.scene, "level:") == [f"level:{level.id}" for level in levels]

        click(app, "level:1")

        assert isinstance(app.scene, scene_type) and app.scene.game_id == game_id
        assert isinstance(level_scene(app, game_id, "2"), scene_type)


# S3_AC2: Letter Rain on the home


def test_S3_AC2_home_opens_the_letter_rain_path(app) -> None:
    start_as(app, age=5)
    assert isinstance(app.scene, HomeScene)
    games = [b for b in app.scene.buttons if b.name.startswith("game:")]
    assert [(b.name, b.enabled) for b in games][:2] == [("game:memory", True), ("game:rain", True)]

    click(app, "game:rain")

    assert isinstance(app.scene, PathScene) and app.scene.game_id == "rain"
    assert app.scene.button("level:1").enabled and not app.scene.button("level:2").enabled


# S3_AC6: the on-screen keyboard


def test_S3_AC6_the_keys_are_big_fit_on_screen_and_show_both_cases(app) -> None:
    scene = play(app, "1")
    app.step([], 16)
    keys = [b for b in scene.buttons if b.name.startswith("key:")]
    rects = [b.rect for b in keys] + [scene.button("keyboard").rect]

    assert sorted(b.name[4:] for b in keys) == sorted(app.content.letters)
    assert all(SCREEN.contains(r) and min(r.size) >= style.MIN_TARGET for r in rects)
    assert all(not a.colliderect(b) for i, a in enumerate(rects) for b in rects[i + 1 :])
    first_row = [scene.button(f"key:{letter}").rect for letter in "QWERTYUIOP"]
    assert [r.x for r in first_row] == sorted(r.x for r in first_row)
    assert scene.button("key:A").rect.x > scene.button("key:Q").rect.x  # staggered like a real one
    # each key shows its capital and its small letter: "Aa" is wider than "A"
    ink = scene.button("key:A").rect.inflate(-12, -20)
    drawn = app.surface.subsurface(ink)
    mask = pygame.mask.from_threshold(drawn, style.VOWEL, (40, 40, 40, 255))
    label = pygame.Rect.unionall(*mask.get_bounding_rects()[:1], mask.get_bounding_rects()[1:])
    assert label.w > style.font(46, True).size("A")[0] * 1.6
    assert key_label("A", "a", style.VOWEL, 46).get_width() > 0


def test_S3_AC6_the_levels_letters_are_lit(app) -> None:
    scene = play(app, "1")  # A M O S T

    lit = {
        b.name[4:] for b in scene.buttons if b.name.startswith("key:") and b.color == style.PANEL
    }
    muted = {
        b.name[4:] for b in scene.buttons if b.name.startswith("key:") and b.color == MUTED_KEY
    }
    assert lit == set("AMOST") and len(muted) == 26 - 5
    wait_for_item(app)
    click(app, "key:B")  # a muted key can still be pressed
    assert scene.game.misses == 1


# S3_AC7: hiding the keyboard


def test_S3_AC7_the_keyboard_hides_and_the_real_keys_still_work(app) -> None:
    scene = play(app, "1")
    key_a = scene.button("key:A").rect.center
    ground = scene.ground_y

    click(app, "keyboard")

    assert names(scene, "key:") == [] and not scene.keyboard_shown
    assert scene.ground_y > ground  # the items fall down to the grass
    assert min(scene.button("keyboard").rect.size) >= style.MIN_TARGET
    wait_for_item(app)
    (drop,) = scene.game.drops
    tap(app, key_a)  # no key there any more
    assert scene.game.hits == 0 and scene.game.misses == 0
    press_key(app, drop.item.answer)
    assert scene.game.hits == 1
    click(app, "keyboard")
    assert len(names(scene, "key:")) == 26


def test_S3_AC7_the_choice_is_saved_for_the_player(app) -> None:
    play(app, "1")
    click(app, "keyboard")
    win_rain_game(app)
    click(app, "next_level")

    assert isinstance(app.scene, RainScene) and not app.scene.keyboard_shown
    saved = ProfileStore(app.store.path.parent).get(app.profile.id)
    assert saved.setting("keyboard") is False


# S3_AC8: finding the letter


def test_S3_AC8_a_key_in_either_case_or_a_tap_finds_the_letter(app) -> None:
    scene = play(app, "1")
    for way in ("small", "capital", "tap"):
        wait_for_item(app)
        letter = scene.game.drops[0].item.answer
        if way == "tap":
            click(app, f"key:{letter}")
        else:
            key_down(app, letter.lower() if way == "small" else letter)  # Caps Lock or not
        assert scene.flashes[letter][0] == HIT_FLASH, way

    assert scene.game.hits == 3 and scene.game.misses == 0


def test_S3_AC8_finding_says_the_letter_and_then_the_word(app, content) -> None:
    app.audio = Recorder(content)
    scene = play(app, "1")
    wait_for_item(app)
    letter = scene.game.drops[0].item.answer
    press_key(app, letter)
    assert app.audio.said == [("letter", letter)]
    assert len(scene.pops) == 1  # it pops with a sparkle
    app.step([], 16)

    app.go(RainScene(app, "rain", "6"))
    wait_for_item(app)
    drop = app.scene.game.drops[0]
    app.audio.said.clear()
    press_key(app, drop.item.answer)
    assert app.audio.said == [("letter+word", drop.item.answer, drop.item.shows)]


def test_S3_AC8_a_wrong_key_flashes_silently_and_other_keys_do_nothing(app, content) -> None:
    app.audio = Recorder(content)
    scene = play(app, "1")
    press_key(app, "A")  # nothing falls yet
    assert scene.game.misses == 0 and scene.flashes == {}
    wait_for_item(app)
    wrong = not_falling(scene)

    press_key(app, wrong)

    assert scene.game.misses == 1 and app.audio.said == []
    assert scene.button(f"key:{wrong}").color == MISS_FLASH
    app.step([], FLASH_MS)
    assert scene.button(f"key:{wrong}").color in (style.PANEL, MUTED_KEY)
    for text in ("1", " ", "", "é"):
        key_down(app, text)
    assert (scene.game.misses, scene.game.hits) == (1, 0)


def test_S3_AC8_tapping_a_falling_item_says_its_name(app, content) -> None:
    app.audio = Recorder(content)
    scene = play(app, "1")
    wait_for_item(app, 0.2)
    drop = scene.game.drops[0]

    tap(app, scene.drop_rect(drop).center)

    assert app.audio.said == [("letter", drop.item.answer)]
    assert scene.game.drops == [drop] and scene.game.hits == 0


# S3_AC9: picture words


def test_S3_AC9_a_picture_says_its_word_when_it_appears(app, content) -> None:
    app.audio = Recorder(content)
    scene = play(app, "6")

    wait_for_item(app)
    (drop,) = scene.game.drops

    assert app.audio.said == [("word", drop.item.shows)]
    app.audio.said.clear()
    tap(app, scene.drop_rect(drop).center)
    assert app.audio.said == [("word", drop.item.shows)]


def test_S3_AC9_a_missing_word_clip_is_silent(app, content, monkeypatch) -> None:
    pygame.init()
    audio = Audio(content)
    monkeypatch.setattr(content.__class__, "word_audio", lambda self, key: "/no/such.wav")
    assert not audio.say_word("cat")
    assert audio.say_letter_and_word("C", "cat")  # the letter still plays

    def no_device():
        raise pygame.error("no audio device")

    monkeypatch.setattr(pygame.mixer, "get_init", lambda: None)
    monkeypatch.setattr(pygame.mixer, "init", no_device)
    app.audio = Audio(content)
    assert not app.audio.say_letter_and_word("C", "cat")
    scene = play(app, "6")
    win_rain_game(app)
    assert scene.win is not None


# S3_AC10: tap one of three


def test_S3_AC10_a_four_year_old_taps_one_of_three_letters(app) -> None:
    scene = play(app, "6", age=4)
    assert names(scene, "key:") == [] and names(scene, "keyboard") == []

    wait_for_item(app)
    drop = scene.game.drops[0]
    choices = [b for b in scene.buttons if b.name.startswith("choice:")]
    assert sorted(b.name[7:] for b in choices) == sorted(drop.choices)
    assert all(min(b.rect.size) >= style.MIN_TARGET for b in choices)
    wrong = next(letter for letter in drop.choices if letter != drop.item.answer)
    click(app, f"choice:{wrong}")
    assert scene.game.misses == 1 and scene.button(f"choice:{wrong}").color == MISS_FLASH

    click(app, f"choice:{drop.item.answer}")
    assert scene.game.hits == 1 and names(scene, "choice:") == []
    app.step([], NEXT_MS)
    wait_for_item(app)
    assert len(scene.game.drops) == 1 and len(names(scene, "choice:")) == 3  # new letters
    press_key(app, scene.game.drops[0].item.answer)  # the real keyboard works too
    assert scene.game.hits == 2


def test_S3_AC10_a_five_year_old_gets_the_keyboard(app) -> None:
    scene = play(app, "6", age=5)
    wait_for_item(app)

    assert len(names(scene, "key:")) == 26 and names(scene, "choice:") == []
    assert not scene.choosing
    app.profile.age = 4
    app.go(RainScene(app, "rain", "1"))
    assert not app.scene.choosing  # three letters only on picture levels


# S3_AC11: the gentle fall


def test_S3_AC11_a_bounce_says_the_name_and_never_ends_the_level(app, content) -> None:
    app.audio = Recorder(content)
    scene = play(app, "1")

    for _ in range(150):  # a minute and a half without pressing anything
        app.step([], 600)

    assert scene.win is None and scene.game.bounces >= 3
    assert scene.game.speed == MIN_SPEED  # each bounce slowed the rain down
    assert scene.game.misses == scene.game.bounces
    assert app.audio.said.count(("letter", scene.game.drops[0].item.answer)) >= 1
    win_rain_game(app)
    assert scene.win.stars >= 1


# S3_AC13: the end of a level


def test_S3_AC13_a_win_shows_the_popup_saves_stars_and_coins_and_opens_the_next_level(app) -> None:
    start_as(app)
    click(app, "game:rain")
    click(app, "level:1")
    scene = app.scene
    scene.draw_play(app.surface)
    win_rain_game(app, misses=9)  # 9 misses for a goal of 8: 2 stars

    assert (scene.win.stars, scene.win.coins) == (2, 4)
    assert {b.name for b in scene.buttons} == {"next_level", "path"}
    app.step([], 16)
    saved = ProfileStore(app.store.path.parent).get(app.profile.id)
    assert saved.progress == {"rain": {"1": 2}} and saved.coins == 4
    click(app, "path")
    assert app.scene.button("level:2").enabled
    click(app, "level:1")
    win_rain_game(app)
    assert app.scene.win.stars == 3
    click(app, "next_level")
    assert isinstance(app.scene, RainScene) and app.scene.level.id == "2"


def test_S3_AC13_the_last_level_has_no_next_level_button(app) -> None:
    scene = play(app, "10")
    win_rain_game(app)

    assert [b.name for b in scene.buttons] == ["path"]


# S3_AC14: a path of ten levels


def path_rects(scene: PathScene) -> list[tuple[str, pygame.Rect]]:
    count = len(scene.level_ids)
    size = sizes(count)["stars"]
    rects = []
    for level_id, center in zip(scene.level_ids, node_centers(count), strict=True):
        rects.append((f"stone {level_id}", scene.button(f"level:{level_id}").rect))
        rects.append((f"stars {level_id}", stars_rect(center, size)))
    return rects


def test_S3_AC14_a_ten_level_path_fits_in_two_rows_without_overlaps(app) -> None:
    start_as(app)
    app.go(PathScene(app, "rain"))
    scene = app.scene
    things = path_rects(scene)

    assert len({rect.centery for name, rect in things if name.startswith("stone")}) == 2
    assert all(min(rect.size) >= style.MIN_TARGET for name, rect in things if "stone" in name)
    for index in range(10):  # the avatar, on each level in turn
        app.profile.progress["rain"] = {str(n): 1 for n in range(1, index + 1)}
        avatar = scene.avatar_rect()
        assert SCREEN.contains(avatar)
        assert not any(avatar.colliderect(rect) for _, rect in things), index
    for i, (name, rect) in enumerate(things):
        assert SCREEN.contains(rect), name
        assert not any(rect.colliderect(other) for _, other in things[i + 1 :]), name
    app.step([], 16)

    assert [y for _, y in node_centers(5)] == [360, 560, 360, 560, 360]  # Letter Pairs unchanged


def test_S3_AC14_the_avatar_stands_on_the_current_level(app) -> None:
    start_as(app)
    app.profile.progress["rain"] = {str(n): 2 for n in range(1, 7)}
    app.go(PathScene(app, "rain"))

    stone = app.scene.button("level:7").rect
    avatar = app.scene.avatar_rect()
    assert app.scene.current_index() == 6
    assert avatar.centerx == stone.centerx and avatar.bottom <= stone.top + 10
    assert avatar.center == avatar_center(stone.center, sizes(10)["avatar"])
    assert stone.w == NODE


# S3_AC15: answers


def test_S3_AC15_answers_are_saved_at_the_end_and_when_leaving(app) -> None:
    scene = play(app, "1")
    wait_for_item(app)
    answer = scene.game.drops[0].item.answer
    wrong = not_falling(scene)
    press_key(app, wrong)
    press_key(app, answer)

    click(app, "back")  # leaving the level saves

    saved = ProfileStore(app.store.path.parent).get(app.profile.id)
    assert saved.answers["letters"][answer].wrong == {wrong: 1}
    assert saved.answers["letters"][answer].right == 1
    app.go(RainScene(app, "rain", "6"))
    win_rain_game(app)
    saved = ProfileStore(app.store.path.parent).get(app.profile.id)
    assert sum(record.right for record in saved.answers["pictures"].values()) == 8


# S3_AC16: speed


def test_S3_AC16_sixty_frames_of_letter_rain_draw_in_under_a_second(app) -> None:
    scene = play(app, "9")
    while len(scene.game.drops) < 2:
        app.step([], 100)
    app.step([], 16)  # the first frame draws and caches the sprites

    start = time.perf_counter()
    for _ in range(60):
        app.step([], 16)

    assert time.perf_counter() - start < 1.0
    assert len(scene.game.drops) == 2
