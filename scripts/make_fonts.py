"""Cut the static Fredoka SemiBold (`assets/fonts/Fredoka-SemiBold.ttf`) from the variable font.

    uv run python scripts/make_fonts.py path/to/Fredoka[wdth,wght].ttf

The variable font comes from https://github.com/google/fonts/tree/main/ofl/fredoka. pygame cannot
choose a weight of a variable font reliably, so the game ships one static weight. fontTools runs
through `uvx`, so it is never a dependency of EduGames.
"""

import argparse
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "src" / "edugames" / "assets" / "fonts" / "Fredoka-SemiBold.ttf"
FONTTOOLS = ["uvx", "--from", "fonttools==4.55.3", "fonttools"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("variable_font", type=Path)
    args = parser.parse_args()
    command = [*FONTTOOLS, "varLib.instancer", str(args.variable_font), "wght=600", "wdth=100"]
    subprocess.run([*command, "-o", str(OUT)], check=True)
    print(OUT)


if __name__ == "__main__":
    main()
