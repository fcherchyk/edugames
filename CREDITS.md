# Credits

Every file in `src/edugames/assets/` is listed here with its source and licence. Only licences
that allow redistribution are used (a test checks this list against the files).

## Andika font

By SIL International, designed for beginning readers (single-storey `a` and `g`, clear `b`/`d`
and `p`/`q`). Downloaded from https://github.com/google/fonts/tree/main/ofl/andika.

Licence: SIL Open Font License 1.1 (full text in `fonts/OFL.txt`)

- `fonts/Andika-Regular.ttf`
- `fonts/Andika-Bold.ttf`
- `fonts/OFL.txt`

## Fredoka font

By Milena Brandão and Hafontia, a rounded display font for titles, buttons and numbers. Downloaded
from https://github.com/google/fonts/tree/main/ofl/fredoka (the variable font); the static
SemiBold was cut from it with `scripts/make_fonts.py`.

Licence: SIL Open Font License 1.1 (full text in `fonts/OFL-Fredoka.txt`)

- `fonts/Fredoka-SemiBold.ttf`
- `fonts/OFL-Fredoka.txt`

## Letter names (English)

Generated with [Piper](https://github.com/OHF-Voice/piper1-gpl) and the `en_US-ljspeech-medium`
voice from https://huggingface.co/rhasspy/piper-voices (MIT), trained on the
[LJ Speech dataset](https://keithito.com/LJ-Speech-Dataset/) (public domain). Piper itself is
GPL-3.0 and is not part of EduGames: it only ran once, through `uvx`, in
`scripts/generate_letter_audio.py`.

Licence: Public domain (LJ Speech recordings; voice model MIT)

- `audio/en/letters/*.wav`

## Picture words (English)

Generated like the letter names, with the same voice, by `scripts/generate_word_audio.py`:
[Piper](https://github.com/OHF-Voice/piper1-gpl) and the `en_US-ljspeech-medium` voice from
https://huggingface.co/rhasspy/piper-voices (MIT), trained on the
[LJ Speech dataset](https://keithito.com/LJ-Speech-Dataset/) (public domain). Each clip says the
`word` of a picture in `content/en/pictures.json`.

Licence: Public domain (LJ Speech recordings; voice model MIT)

- `audio/en/words/*.wav`
