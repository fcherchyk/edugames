"""Generate the picture-word clips (`assets/audio/<locale>/words/<picture id>.wav`) with Piper TTS.

    uv run python scripts/generate_word_audio.py --voice path/to/en_US-ljspeech-medium.onnx

Use the same voice as the letter names (`generate_letter_audio.py`), so the game has one voice.
Each clip says the `word` of `content/<locale>/pictures.json`, with the silence around it trimmed.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from generate_letter_audio import ROOT, speak  # noqa: E402

from edugames.core.content import ASSETS_DIR, CONTENT_DIR, _read  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--voice", type=Path, required=True, help="Piper voice (.onnx)")
    parser.add_argument("--locale", default="en")
    parser.add_argument("--pictures", default="", help="only these picture ids, for example: cat")
    args = parser.parse_args()
    pictures = _read(CONTENT_DIR / args.locale / "pictures.json")["pictures"]
    only = set(args.pictures.split())
    for picture in pictures:
        if only and picture["id"] not in only:
            continue
        out = ASSETS_DIR / "audio" / args.locale / "words" / f"{picture['id']}.wav"
        speak(args.voice, picture["word"] + ".", out)
        print(f"{picture['id']}: {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
