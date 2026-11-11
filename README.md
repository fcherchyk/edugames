# EduGames

Literacy games for children aged 4 to 6 who are learning to read: recognising letters, matching
upper and lower case, letter sounds, first letters of words and drawing letters.

Slice 1 (MVP) ships **Letter Pairs**, a memory game where `A` is matched with `a`, and the
platform around it: player profiles, a goal path with stars, coins, and an avatar to dress up.

A desktop app in Python with [pygame-ce](https://pyga.me/), for macOS, Linux and Windows.

## Features

- **Players:** several profiles on one computer, each with a first name, an age and an avatar
  (face, skin tone, hair style and hair colour). The age decides which games are offered.
- **Letter Pairs:** turn two cards over to match a capital letter with its small letter. Every
  card says its letter's name when it is turned. No timer and no way to lose.
- **Goal path:** 5 levels, from 3 easy pairs to 8 random letters, including the commonly confused
  `b d p q`. Each level opens when the one before is won, and keeps its best 1 to 3 stars.
- **Coins and wardrobe:** every win gives coins, which buy shirt colours for the avatar.
- **Victory pop-up:** the avatar celebrates, with the stars and coins earned.
- **Art style:** a cel-shaded chibi avatar, rolling hills and a checkered ground, a world per
  level (meadow, beach, forest, snow, space), glossy stars and coins, and letters in Montessori
  colours (vowels red, consonants blue).
- **Private by design:** no network, no accounts, no ads; only a first name and an age, saved on
  the computer.

## Run it

Requires [uv](https://docs.astral.sh/uv/) (it installs Python 3.12 if needed).

```sh
uv run edugames
```

Profiles are saved in the user data folder: `~/Library/Application Support/EduGames` on macOS,
`~/.local/share/EduGames` on Linux, `%LOCALAPPDATA%\EduGames` on Windows.

## Tests

```sh
uv run pytest                 # headless, with coverage (fails below 80%)
uv run ruff check .
uv run ruff format --check .
```

Tests run without a window or sound card (SDL's dummy drivers). CI runs them on macOS, Ubuntu
and Windows. Each test is named after the acceptance criterion it covers (`test_S1_AC7_…`); the
criteria are in [`docs/S1_mvp.md`](docs/S1_mvp.md) and
[`docs/S2_art_style.md`](docs/S2_art_style.md).

## Sandbox

For Linux or macOS machines with no screen, no sound card and possibly no network:

| Script | What it does |
|---|---|
| `./test-sandbox.sh [pytest args]` | Installs dependencies, then runs ruff and pytest. |
| `./run-sandbox.sh [dir]` | Plays a scripted game headless and saves a PNG of every screen to `.sandbox/screens/` (or `dir`). Uses a throwaway data folder. |

Dependencies (`sandbox-deps.sh`) come from the uv cache first, then the network. If the index
refuses the versions in `uv.lock`, they are installed from the version ranges in
`pyproject.toml`, skipping releases newer than 14, 30, 60 or 90 days (`uv.lock` is never
changed). Settings: `SANDBOX_OFFLINE=1`, `SANDBOX_DEPS=locked`,
`SANDBOX_DEPS_MIN_AGE_DAYS="14 30"`.

The same demo runs anywhere with `uv run python -m edugames.demo <dir>`.

## Project structure

```
src/edugames/
  core/          game rules, scoring, profiles, storage, content loading (no pygame)
  ui/            window, screens, widgets, avatar, scenery and art helpers, audio
  content/en/    letters, games, levels and UI strings (English)
  assets/        Andika and Fredoka fonts, letter-name clips
  demo.py        scripted headless playthrough
scripts/         generate_letter_audio.py (Piper TTS), make_fonts.py (Fredoka SemiBold)
tests/           pytest suite
docs/            standards, acceptance criteria per slice, ADRs
```

Rules for contributing: [`docs/standards.md`](docs/standards.md). Asset licences:
[`CREDITS.md`](CREDITS.md).

## Roadmap

Ideas for the next slices, to be prioritised:

- **More games:** Letter Sounds (hear a sound, tap the letter), First Letter (a picture such as a
  sun or a duck, choose its first letter), Draw Letters (trace a letter following arrows), Find
  the Letter (spot every `m` in a scene), alphabet order, and building your own name.
- **Spanish:** `content/es/` adapted, not translated: the Spanish alphabet (including `Ñ`), its
  own levels and words for pictures, and recorded clips, chosen per player.
- **Avatar:** more faces and hair, and items bought with coins (crowns, hats, glasses, clothes).
- **Adaptive practice:** repeat the letters a child confuses (`b`/`d`, `p`/`q`).
- **Parents' area:** letters mastered per player, deleting profiles, behind an adult check.
- **Packaging:** double-click builds for macOS, Windows and Linux; a web build with pygbag.

## Licence

MIT. Fonts and sounds have their own licences, listed in [`CREDITS.md`](CREDITS.md).
