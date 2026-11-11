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
from edugames.ui.scenes.memory import TURN_BACK_MS, MemoryScene  # noqa: E402

FRAME_MS = 16


def click(app: App, name: str) -> None:
    """Tap the centre of the current screen's button called `name`, then draw a frame."""
    pos = app.scene.button(name).rect.center
    app.step([pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=pos)], FRAME_MS)


def type_text(app: App, text: str) -> None:
    app.step([pygame.event.Event(pygame.TEXTINPUT, text=text)], FRAME_MS)


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
    for choice in ("face:grin", "hair_style:curly", "hair_color:red", "skin:tan"):
        click(app, choice)
    shot("look")
    click(app, "done")
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
    click(app, "wardrobe")
    click(app, "shirt:green")
    shot("wardrobe")
    return shots


def main(argv: list[str] | None = None) -> None:  # pragma: no cover - command-line entry point
    args = sys.argv[1:] if argv is None else argv
    out_dir = Path(args[0] if args else "screens")
    with tempfile.TemporaryDirectory() as data_dir:
        for path in run_demo(out_dir, Path(data_dir)):
            print(path)
    pygame.quit()


if __name__ == "__main__":  # pragma: no cover
    main()
