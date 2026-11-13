# EduGames

Early literacy and numeracy games for children aged 4 to 6: recognising letters, matching upper
and lower case, first letters of words, spelling, drawing letters, and numbers and quantities.

Slice 1 (MVP) ships **Letter Pairs**, a memory game where `A` is matched with `a`, and the
platform around it: player profiles, a goal path with stars, coins, and an avatar to dress up.
Slice 3 adds **Letter Rain**: letters, then pictures, fall gently, and the child finds their letter
on the keyboard. Slice 4 turns the wardrobe into an **avatar shop**: hats, glasses, wings, shoes
and pets, tried on for free and bought with the coins won.

A desktop app in Python with [pygame-ce](https://pyga.me/), for macOS, Linux and Windows.

## Features

- **Players:** several profiles on one computer, each with a first name, an age (3 to 7) and an
  avatar (face, skin tone, hair style, hair colour, eye colour and freckles, chosen one at a time
  in a mirror, and changed for free at any time). The age decides which games are offered.
- **Letter Pairs:** turn two cards over to match a capital letter with its small letter. Every
  card says its letter's name when it is turned. No timer and no way to lose.
- **Letter Rain:** letters fall from the sky and pop when the child presses them, on the real
  keyboard or on the on-screen one (laid out like the real one, each key showing `Aa`, and hidden
  with a tap if the child prefers the real keyboard). After five letter levels, pictures fall
  instead: each says its word, and the child finds its first letter. Players under 5 choose among
  three big letters on picture levels. Whatever reaches the ground bounces back up: no lives, no
  game over, and the speed adapts to the child.
- **Goal path:** one per game. Letter Pairs has 5 levels, from 3 easy pairs to 8 random letters,
  including the commonly confused `b d p q`; Letter Rain has 10, in two rows. Each level opens
  when the one before is won, and keeps its best 1 to 3 stars.
- **Coins and the shop:** the first win of a level gives 3 to 5 coins, a replay 2. Coins buy
  things for the avatar: 8 hats (up to a crown and a space helmet), 6 glasses and masks, 5 wings
  and capes (up to a jetpack), 7 pairs of shoes (up to rocket boots), 18 pets in five kinds
  (cats, dogs, birds, monsters, robots) and 8 shirt colours. Anything can be tried on for free; a green "Buy" pill with the
  price buys it, and a gold bar shows how close the coins are. Some items open when the player
  reaches their world on the path (the penguin in the snow, the jetpack in space), and the
  victory pop-up shows what a win opened. Prices are small round numbers; nothing is random or
  for a limited time. The shop's "Me" tab changes the look for free.
- **Victory pop-up:** the avatar celebrates, with the stars and coins earned (and what is new in
  the shop).
- **Art style:** a cel-shaded chibi avatar, rolling hills and a checkered ground, a world per
  level (meadow, beach, forest, snow, space), glossy stars and coins, letters in Montessori
  colours (vowels red, consonants blue), 22 pictures and 44 avatar items drawn in code.
- **Answers per letter:** every answer in Letter Rain is kept per letter and per picture, with the
  key pressed instead (`b` for `d`), for a future parents' area and practice of confused letters.
- **Private by design:** no network, no accounts, no ads; only a first name and an age (and the
  game's progress), saved on the computer.

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
criteria are in [`docs/S1_mvp.md`](docs/S1_mvp.md),
[`docs/S2_art_style.md`](docs/S2_art_style.md),
[`docs/S3_letter_rain.md`](docs/S3_letter_rain.md) and
[`docs/S4_avatar_shop.md`](docs/S4_avatar_shop.md).

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
  core/          game rules, scoring, answers, profiles, the shop's items and rules, storage,
                 content loading (no pygame)
  ui/            window, screens, widgets, keyboard, avatar and its items, pictures, scenery,
                 art helpers, audio
  content/en/    letters, games, levels per game, pictures, keyboard and UI strings (English)
  assets/        Andika and Fredoka fonts, letter-name and picture-word clips
  demo.py        scripted headless playthrough
scripts/         generate_letter_audio.py and generate_word_audio.py (Piper TTS),
                 make_fonts.py (Fredoka SemiBold)
tests/           pytest suite
docs/            standards, acceptance criteria per slice, ADRs
```

Rules for contributing: [`docs/standards.md`](docs/standards.md). Asset licences:
[`CREDITS.md`](CREDITS.md).

## Roadmap

One slice at a time, in this order. Each slice gets its acceptance criteria in
`docs/S<n>_<name>.md` when it starts.

| Slice | What it brings | Builds on |
|---|---|---|
| S1 ✅ | Profiles, goal path and Letter Pairs | — |
| S2 ✅ | Art style and a world per level | — |
| S3 ✅ | **Letter Rain:** capital and small letters fall and vanish when the child finds them on the keyboard; then pictures fall and vanish when their first letter is pressed (tap one of 3 letters for the youngest) | Levels per game; an on-screen keyboard showing both cases on each key, which can be hidden; the gentle fall (see below); every answer recorded per letter and picture; a library of pictures drawn in code, each a language-neutral concept with a word and its audio per locale |
| S4 ✅ | **Avatar shop:** crowns, helmets, wings and more, bought with coins | Item drawings in the art style; the wardrobe becomes a shop |
| S5 | **Letter games:** *Write Your Name* (build your own name letter by letter), *Draw Letters* (trace a letter following arrows), *Find the Letter* (spot every `m` in a scene) | The keyboard; the player's name; tracing with mouse or touch |
| S6 | **Picture album:** every word found in Letter Rain becomes a sticker | The pictures and the answers per picture of S3 |
| S7 | **Numbers:** *Numbers 1 to 10* (recognise and count, spoken numbers), *Count and Match* (numbers with quantities of things), *Biggest Number* (pick the largest of several). Levels go up to 5, then 10, 20 and 50 | The pictures of S3, to count; numbers in the content |
| S8 | **Fill the Gaps:** a picture and its word with letters missing, typed on the keyboard (the first letter, then a vowel, then several) | The keyboard and the pictures |
| S9 | **Word Builder:** drag the scrambled letters to spell the picture's word | Drag and drop |
| S10 | **Alphabet Order:** put letters in order, or find what comes next | — |
| S11 | **Parents' area**, behind an adult check: progress per letter and number, deleting profiles, speed and sound settings | Answers recorded since S3 |
| S12 | **Spanish:** `content/es/` adapted, not translated: the Spanish alphabet (with `Ñ`), its own levels and words for the pictures, and its own audio | Everything above as content |

**The gentle fall** (S3): nothing is lost. A letter or picture that reaches the ground bounces
back up, there are no lives and no game over, the speed adapts to the child, and a level ends
after a number of right answers.

**Later, not yet ordered:** adaptive practice (repeat the letters a child confuses, such as
`b`/`d`), animations and sound effects, Letter Sounds (needs recorded phonemes), and packaging
(double-click builds for macOS, Windows and Linux, and a web build with pygbag).

## Licence

MIT. Fonts and sounds have their own licences, listed in [`CREDITS.md`](CREDITS.md).
