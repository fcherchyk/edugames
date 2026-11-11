"""Generate the letter-name clips (`assets/audio/<locale>/letters/<letter>.wav`) with Piper TTS.

    uv run python scripts/generate_letter_audio.py --voice path/to/en_US-ljspeech-medium.onnx

Piper (GPL-3.0) runs through `uvx`, so it is never a dependency of EduGames; only the generated
clips are versioned. Voices: https://huggingface.co/rhasspy/piper-voices (download the `.onnx` and
its `.onnx.json`). Each clip says the `spoken` text of `content/<locale>/letters.json`, with the
silence around it trimmed.
"""

import argparse
import array
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from edugames.core.content import ASSETS_DIR, CONTENT_DIR, _read  # noqa: E402

PIPER = ["uvx", "--from", "piper-tts==1.8.0", "piper"]
SILENCE = 400  # 16-bit sample level under which a sample counts as silence
PADDING_MS = 40


def trim_silence(samples: array.array, rate: int) -> array.array:
    """Drop the silence before and after the voice, keeping a little padding."""
    loud = [i for i, sample in enumerate(samples) if abs(sample) > SILENCE]
    if not loud:
        return samples
    pad = rate * PADDING_MS // 1000
    return samples[max(0, loud[0] - pad) : loud[-1] + pad]


def speak(voice: Path, text: str, out: Path) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        raw = Path(tmp) / "raw.wav"
        subprocess.run([*PIPER, "-m", str(voice), "-f", str(raw)], input=text.encode(), check=True)
        with wave.open(str(raw), "rb") as source:
            params = source.getparams()
            samples = array.array("h", source.readframes(params.nframes))
    trimmed = trim_silence(samples, params.framerate)
    out.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(out), "wb") as target:
        target.setparams(params)
        target.writeframes(trimmed.tobytes())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--voice", type=Path, required=True, help="Piper voice (.onnx)")
    parser.add_argument("--locale", default="en")
    parser.add_argument("--letters", default="", help="only these letters, for example: F Q")
    args = parser.parse_args()
    letters = _read(CONTENT_DIR / args.locale / "letters.json")["letters"]
    only = set(args.letters.upper().split())
    for letter in letters:
        if only and letter["upper"] not in only:
            continue
        out = ASSETS_DIR / "audio" / args.locale / "letters" / f"{letter['lower']}.wav"
        speak(args.voice, letter["spoken"] + ".", out)
        print(f"{letter['upper']}: {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
