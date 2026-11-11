"""The screens, driven headless with taps and key presses as a child would."""

import pygame
import pytest

from edugames.core.avatar import FACES, HAIR_COLORS, HAIR_STYLES, SKIN_TONES, Avatar
from edugames.core.profiles import new_profile
from edugames.demo import click, type_text, win_memory_game
from edugames.ui import style
from edugames.ui.app import FPS, App
from edugames.ui.audio import Audio
from edugames.ui.avatar_draw import draw_avatar
from edugames.ui.scenes.home import HomeScene
from edugames.ui.scenes.memory import TURN_BACK_MS, MemoryScene, card_rects
from edugames.ui.scenes.path import PathScene
from edugames.ui.scenes.profiles import ProfileCreateScene, ProfileSelectScene
from edugames.ui.scenes.wardrobe import WardrobeScene


def key(app: App, code: int) -> None:
    app.step([pygame.event.Event(pygame.KEYDOWN, key=code)], 16)


def start_as(app: App, name: str = "Sam", age: int = 5, coins: int = 0) -> None:
    profile = app.store.add(new_profile(name, age))
    profile.coins = coins
    app.scene = ProfileSelectScene(app)
    click(app, f"profile:{name}")


def play_level(app: App, level: str, mistakes: int = 0) -> MemoryScene:
    app.go(MemoryScene(app, "memory", level))
    scene = app.scene
    win_memory_game(app, mistakes)
    return scene


class Recorder(Audio):
    def __init__(self, content) -> None:
        super().__init__(content)
        self.said: list[str] = []

    def say_letter(self, upper: str) -> bool:
        self.said.append(upper)
        return super().say_letter(upper)


def test_S1_AC2_a_new_player_types_a_name_picks_an_age_and_a_look(app) -> None:
    click(app, "new_player")
    assert not app.scene.button("next").enabled

    type_text(app, "Sam3!")  # digits and symbols are dropped
    key(app, pygame.K_BACKSPACE)
    type_text(app, "m")
    assert app.scene.name == "Sam"
    click(app, "next")
    click(app, "age:5")
    click(app, "face:wink")
    click(app, "hair_style:bun")
    click(app, "done")

    (profile,) = app.store.profiles
    assert (profile.name, profile.age) == ("Sam", 5)
    assert (profile.avatar.face, profile.avatar.hair_style) == ("wink", "bun")
    assert isinstance(app.scene, HomeScene) and app.profile is profile


def test_S1_AC2_the_name_is_limited_and_enter_moves_on(app) -> None:
    click(app, "new_player")
    type_text(app, "Maximilianoooo")
    assert app.scene.name == "Maximiliano"[:11] + "o"
    key(app, pygame.K_RETURN)
    assert app.scene.step == "age"


def test_S1_AC2_back_goes_one_step_back_and_finally_cancels(app) -> None:
    click(app, "new_player")
    type_text(app, "Sam")
    click(app, "next")
    click(app, "age:4")
    click(app, "back")
    assert app.scene.step == "age" and app.scene.button("age:4").selected
    click(app, "back")
    assert app.scene.step == "name" and app.scene.name == "Sam"
    click(app, "back")
    assert isinstance(app.scene, ProfileSelectScene) and app.store.profiles == []


def test_S1_AC3_choosing_a_player_opens_their_home_and_players_goes_back(app) -> None:
    app.store.add(new_profile("Ana", 4))
    start_as(app, "Sam")
    assert app.profile.name == "Sam"

    click(app, "back")

    assert isinstance(app.scene, ProfileSelectScene) and app.profile is None
    assert {b.name for b in app.scene.buttons} == {"profile:Ana", "profile:Sam", "new_player"}


def test_S1_AC3_no_new_player_tile_when_the_profiles_are_full(app) -> None:
    for i in range(6):
        app.store.add(new_profile(f"Kid {'abcdef'[i]}", 5))
    app.scene = ProfileSelectScene(app)

    with pytest.raises(KeyError):
        app.scene.button("new_player")


def test_S1_AC5_home_shows_the_games_for_the_age_and_locks_coming_soon(app) -> None:
    start_as(app, age=5)
    games = [b for b in app.scene.buttons if b.name.startswith("game:")]

    assert [b.name for b in games] == [
        "game:memory",
        "game:letter-sounds",
        "game:first-letter",
        "game:draw-letters",
    ]
    assert [b.enabled for b in games] == [True, False, False, False]
    click(app, "game:letter-sounds")
    assert isinstance(app.scene, HomeScene)
    click(app, "game:memory")
    assert isinstance(app.scene, PathScene)


def test_S1_AC7_two_different_cards_turn_back_after_a_second(app) -> None:
    start_as(app)
    app.go(MemoryScene(app, "memory", "1"))
    game = app.scene.game
    other = next(i for i, c in enumerate(game.cards) if c.letter != game.cards[0].letter)
    click(app, "card:0")
    click(app, f"card:{other}")

    app.step([], TURN_BACK_MS - 100)
    assert game.waiting_turn_back
    app.step([], 100)
    assert not game.waiting_turn_back and not game.is_shown(0)


@pytest.mark.parametrize("level", ["1", "2", "3", "5"])
def test_S1_AC7_cards_are_big_and_fit_on_screen(app, level) -> None:
    start_as(app)
    pairs = app.content.memory_level(level).pairs
    rects = card_rects(2 * pairs)
    screen = pygame.Rect((0, 0), style.SIZE)

    assert all(screen.contains(r) and min(r.size) >= style.MIN_TARGET for r in rects)
    assert all(not a.colliderect(b) for i, a in enumerate(rects) for b in rects[i + 1 :])


def test_S1_AC8_turning_a_card_says_its_letter(app, content) -> None:
    app.audio = Recorder(content)
    start_as(app)
    app.go(MemoryScene(app, "memory", "1"))
    first = app.scene.game.cards[0]

    click(app, "card:0")
    click(app, "card:0")  # already up: no sound

    assert app.audio.said == [first.letter]


def test_S1_AC8_the_letter_clips_play_on_a_sound_device(content) -> None:
    pygame.init()
    audio = Audio(content)

    assert audio.enabled
    assert audio.say_letter("A") and "A" in audio.sounds


def test_S1_AC8_with_no_sound_device_the_game_stays_silent(app, content, monkeypatch) -> None:
    def no_device():
        raise pygame.error("no audio device")

    monkeypatch.setattr(pygame.mixer, "get_init", lambda: None)
    monkeypatch.setattr(pygame.mixer, "init", no_device)
    app.audio = Audio(content)
    assert not app.audio.enabled

    start_as(app)
    scene = play_level(app, "1")

    assert scene.win is not None


def test_S1_AC8_a_missing_clip_is_silent(content, monkeypatch) -> None:
    pygame.init()
    audio = Audio(content)
    monkeypatch.setattr(content.__class__, "letter_audio", lambda self, upper: "/no/such.wav")

    assert not audio.say_letter("B")


def test_S1_AC9_mistakes_never_end_the_game(app) -> None:
    start_as(app)
    scene = play_level(app, "1", mistakes=10)

    assert scene.game.mismatches == 10 and scene.win.stars == 1


def test_S1_AC10_S1_AC11_S1_AC12_a_win_saves_stars_coins_and_opens_the_next_level(app) -> None:
    start_as(app)
    click(app, "game:memory")
    assert not app.scene.button("level:2").enabled

    click(app, "level:1")
    win_memory_game(app, mistakes=1)
    click(app, "path")

    assert app.scene.button("level:2").enabled
    assert app.scene.current_index() == 1
    saved = app.store.__class__(app.store.path.parent).get(app.profile.id)
    assert saved.progress == {"memory": {"1": 3}} and saved.coins == 5


def test_S1_AC11_the_avatar_waits_on_the_last_level_once_all_are_won(app) -> None:
    start_as(app)
    app.profile.progress["memory"] = {str(n): 1 for n in range(1, 6)}
    app.go(PathScene(app, "memory"))

    assert app.scene.current_index() == 4


def test_S1_AC13_the_victory_popup_shows_stars_coins_and_next_level(app) -> None:
    start_as(app)
    scene = play_level(app, "1")

    assert scene.win.stars == 3 and scene.win.coins == 5
    assert {b.name for b in scene.buttons} == {"next_level", "path"}
    app.step([], 16)  # draws the pop-up with the celebrating avatar
    click(app, "next_level")
    assert isinstance(app.scene, MemoryScene) and app.scene.level.id == "2"


def test_S1_AC13_the_last_level_has_no_next_level_button(app) -> None:
    start_as(app)
    scene = play_level(app, "5")

    assert [b.name for b in scene.buttons] == ["path"]


def test_S1_AC14_every_avatar_option_is_drawn(app) -> None:
    surface = pygame.Surface((300, 300))
    options = zip(FACES, SKIN_TONES, HAIR_STYLES, HAIR_COLORS, strict=False)
    for face, skin, hair, color in options:
        for celebrating in (False, True):
            surface.fill(style.WHITE)
            draw_avatar(surface, Avatar(face, skin, hair, color), (150, 150), 260, celebrating)
            assert surface.get_bounding_rect().w > 100  # something was drawn


def test_S1_AC14_the_look_step_offers_every_option(app) -> None:
    click(app, "new_player")
    type_text(app, "Sam")
    click(app, "next")
    click(app, "age:6")
    names = {b.name for b in app.scene.buttons}

    for field, values in (
        ("face", FACES),
        ("skin", SKIN_TONES),
        ("hair_style", HAIR_STYLES),
        ("hair_color", HAIR_COLORS),
    ):
        assert {f"{field}:{v}" for v in values} <= names
    app.step([], 16)
    assert isinstance(app.scene, ProfileCreateScene)


def test_S1_AC15_the_wardrobe_buys_and_wears_a_colour(app) -> None:
    start_as(app, coins=6)
    click(app, "wardrobe")
    assert isinstance(app.scene, WardrobeScene)
    assert app.scene.button("shirt:green").enabled

    click(app, "shirt:green")

    assert app.profile.avatar.shirt == "green" and app.profile.coins == 1
    assert not app.scene.button("shirt:yellow").enabled  # 1 coin is not enough
    click(app, "shirt:blue")  # free colour
    assert app.profile.avatar.shirt == "blue"
    click(app, "back")
    assert isinstance(app.scene, HomeScene)


def test_S1_AC1_closing_the_window_stops_the_loop(app) -> None:
    app.step([pygame.event.Event(pygame.QUIT)], 16)

    assert not app.running and FPS == 60
