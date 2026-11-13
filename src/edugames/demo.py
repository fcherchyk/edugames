"""A scripted playthrough with no window, saving a PNG of each screen.

For machines with no display, such as a sandbox: `python -m edugames.demo <output dir>`.
It plays in a throwaway data directory, so it never touches real profiles.
"""

import os
import random
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402

from edugames.core.content import load_content  # noqa: E402
from edugames.core.profiles import ProfileStore  # noqa: E402
from edugames.ui import style  # noqa: E402
from edugames.ui.app import App  # noqa: E402
from edugames.ui.audio import Audio  # noqa: E402
from edugames.ui.look_picker import SPARKLE_MS, option_name  # noqa: E402
from edugames.ui.scenes.memory import TURN_BACK_MS, MemoryScene  # noqa: E402
from edugames.ui.scenes.rain import RainScene  # noqa: E402

FRAME_MS = 16
WAIT_MS = 100  # one frame while waiting for the rain (coarser than real frames, so it runs fast)


def click(app: App, name: str) -> None:
    """Tap the centre of the current screen's button called `name`, then draw a frame."""
    pos = app.scene.button(name).rect.center
    app.step([pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=pos)], FRAME_MS)


def choose_look(app: App, field: str, value: object) -> None:
    """Open the look's chip for `field` and tap `value` (creating a player or in the Me tab)."""
    click(app, f"look:{field}")
    click(app, option_name(field, value))


def finish_look(app: App) -> None:
    """Go through the rest of a new player's look with "Next", then tap "Done"."""
    while "done" not in [button.name for button in app.scene.buttons]:
        click(app, "next")
    click(app, "done")


def type_text(app: App, text: str) -> None:
    app.step([pygame.event.Event(pygame.TEXTINPUT, text=text)], FRAME_MS)


def press_key(app: App, letter: str) -> None:
    """Press a letter on the real keyboard (small letters, as without Caps Lock)."""
    app.step([pygame.event.Event(pygame.KEYDOWN, key=0, unicode=letter.lower())], FRAME_MS)


def wait_for_item(app: App, height: float = 0.0) -> None:
    """Let the rain fall until an item is at least `height` of the way down."""
    game = app.scene.game
    for _ in range(2000):
        if any(drop.y >= height for drop in game.drops):
            return
        app.step([], WAIT_MS)
    raise AssertionError("nothing fell")


def win_rain_game(app: App, misses: int = 0) -> None:
    """Press `misses` wrong letters, then find every item until the level is won."""
    scene = app.scene
    assert isinstance(scene, RainScene)
    for _ in range(misses):
        wait_for_item(app)
        falling = {drop.item.answer for drop in scene.game.drops}
        press_key(app, next(letter for letter in app.content.letters if letter not in falling))
    while scene.win is None:
        wait_for_item(app)
        press_key(app, scene.game.lowest().item.answer)


def win_memory_game(app: App, mistakes: int = 1) -> None:
    """Make `mistakes` wrong guesses, then match every pair."""
    scene = app.scene
    assert isinstance(scene, MemoryScene)
    cards = scene.game.cards
    for _ in range(mistakes):
        first = 0
        second = next(i for i, card in enumerate(cards) if card.letter != cards[first].letter)
        click(app, f"card:{first}")
        click(app, f"card:{second}")
        app.step([], TURN_BACK_MS)  # wait for the two cards to turn back
    for letter in dict.fromkeys(card.letter for card in cards):
        for index, card in enumerate(cards):
            if card.letter == letter:
                click(app, f"card:{index}")


def run_demo(out_dir: Path, data_dir: Path, seed: int = 7) -> list[Path]:
    pygame.init()
    content = load_content()
    app = App(
        content,
        ProfileStore(data_dir),
        Audio(content),
        pygame.Surface(style.SIZE),
        random.Random(seed),
    )
    shots: list[Path] = []

    def shot(name: str) -> None:
        app.step([], FRAME_MS)
        path = out_dir / f"{len(shots) + 1:02d}-{name}.png"
        pygame.image.save(app.surface, path)
        shots.append(path)

    out_dir.mkdir(parents=True, exist_ok=True)
    shot("players")
    click(app, "new_player")
    type_text(app, "Sam")
    shot("name")
    click(app, "next")
    click(app, "age:5")
    for field, value in (("face", "grin"), ("hair_style", "curly"), ("skin", "tan")):
        choose_look(app, field, value)
    choose_look(app, "hair_color", "red")  # the mirror sparkles on the hair
    app.step([], SPARKLE_MS // 2)
    shot("look")
    finish_look(app)
    shot("home")
    click(app, "game:memory")
    shot("path")
    click(app, "level:1")
    game = app.scene.game
    partner = next(
        i for i in range(1, len(game.cards)) if game.cards[i].letter == game.cards[0].letter
    )
    click(app, "card:0")
    click(app, f"card:{partner}")  # one pair matched
    click(app, f"card:{next(i for i in range(len(game.cards)) if not game.is_shown(i))}")
    shot("memory")
    win_memory_game(app)
    shot("victory")
    click(app, "path")
    shot("path-after-win")
    click(app, "back")
    click(app, "shop")
    click(app, "head:party_hat")  # tried on, with the price to buy it
    shot("shop")
    click(app, "buy")
    click(app, "back")
    click(app, "game:rain")
    shot("rain-path")
    click(app, "level:1")
    wait_for_item(app)
    win_one_then_wait(app)
    shot("rain-letters")
    click(app, "keyboard")
    shot("rain-no-keyboard")
    click(app, "keyboard")
    win_rain_game(app, misses=2)
    shot("rain-victory")
    play_to_picture_levels(app)
    wait_for_item(app, 0.3)
    shot("rain-pictures")
    for _ in ("path", "home", "players"):
        click(app, "back")
    click(app, "new_player")
    type_text(app, "Mia")
    click(app, "next")
    click(app, "age:4")
    finish_look(app)
    click(app, "game:rain")
    click(app, "level:1")
    win_rain_game(app)
    play_to_picture_levels(app)
    wait_for_item(app, 0.3)
    shot("rain-choices")
    for _ in ("path", "home"):
        click(app, "back")
    click(app, "shop")
    click(app, "head:crown")  # too dear yet: the coins fill a bar towards its price
    shot("shop-saving")
    click(app, "tab:back")
    click(app, "back:butterfly_wings")
    click(app, "buy")
    shot("shop-bought")
    click(app, "tab:eyes")
    click(app, "eyes:star_glasses")
    click(app, "buy")
    click(app, "tab:me")
    choose_look(app, "eye_color", "green")
    choose_look(app, "freckles", True)  # the star glasses are off in the mirror for the freckles
    app.step([], SPARKLE_MS // 2)
    shot("shop-me")
    click(app, "tab:pet")
    click(app, "pet:kitten")  # tried on: 10 coins are not enough yet
    shot("shop-pets")
    click(app, "back")
    shot("home-dressed")
    return shots


def win_one_then_wait(app: App) -> None:
    """Find one item, then wait for the rain to bring the next ones well into the sky."""
    press_key(app, app.scene.game.lowest().item.answer)
    wait_for_item(app, 0.35)


def play_to_picture_levels(app: App) -> None:
    """From a won Letter Rain level, win each next letter level up to the first picture level."""
    while not app.scene.level.has_pictures:
        click(app, "next_level")
        if not app.scene.level.has_pictures:
            win_rain_game(app)


def main(argv: list[str] | None = None) -> None:  # pragma: no cover - command-line entry point
    args = sys.argv[1:] if argv is None else argv
    out_dir = Path(args[0] if args else "screens")
    with tempfile.TemporaryDirectory() as data_dir:
        for path in run_demo(out_dir, Path(data_dir)):
            print(path)
    pygame.quit()


if __name__ == "__main__":  # pragma: no cover
    main()
