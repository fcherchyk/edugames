# hgames workspace standards

The rules for the games in `~/hgames` ("H" for Harnesses). They start from the `~/hworkspace`
harness standards and change the architecture: games are desktop apps, not web apps. Anyone
working on the repo (a person or an agent) reads this file first.

## General

- Python 3.12+, managed with `uv`: `pyproject.toml`, a versioned `uv.lock`, a project `.venv`.
  Run everything with `uv run`.
- Everything versioned is in English: code, names, comments, docstrings, UI text, tests, docs,
  commit messages. Other languages arrive as content locales (see "Localisation"), never as code.
- Small functions with one job and names that say what they do. Type hints on public functions.
- No secrets in the code. The games need none: no network, no accounts.
- Prefer the standard library before adding a dependency.
- Licence: MIT.

## Architecture

1. **Desktop with pygame-ce.** One window with a fixed 1280×800 logical surface, scaled to the
   screen (`pygame.SCALED`). Saved data are JSON files in
   `platformdirs.user_data_dir("EduGames")`. No database, no server, no network.
2. **Logic separate from the screen.** `edugames.core` is plain Python and never imports pygame:
   rules, scoring, progress, profiles, storage, content. `edugames.ui` only draws and turns events
   into calls to the core. A rule that can be tested without a window lives in the core.
3. **Content separate from code.** Letters, levels, games and UI strings live in
   `src/edugames/content/<locale>/*.json`, and recorded audio in
   `src/edugames/assets/audio/<locale>/`. Adding a language means adding those folders, not code.
   UI text always goes through `Content.text(key)`.
4. **Async main loop.** The loop awaits `asyncio.sleep(0)` every frame, so a web build with pygbag
   stays possible without rewriting the game.
5. **Writes are atomic.** Save to a temporary file and `os.replace` it. A damaged file is set aside
   (`.corrupt`), never a crash.

## Localisation

Localising a game is adapting its content to the language, not translating its words. Each
locale chooses its own:

- **Alphabet and letter names:** Spanish has `Ñ`; the letter Z is "zee" in American English and
  "zeta" in Spanish. Which letters are vowels is content too (`"vowel"` in `letters.json`).
- **Levels:** letter sets follow that language's most frequent letters and its common confusions
  (`b d p q` in English; `b/v`, `c/s/z`, `ll/y` in Spanish).
- **Words for pictures:** a picture is a language-neutral concept (`cow`); each locale maps it to
  its word and first letter (cow → C, vaca → V). A picture appears only in the locales that define
  it, which leaves out cases that don't work in a language (a silent `h`).
- **Audio:** recorded or generated per locale.

Drawings and scenery carry no text, so they are shared by every language.

## Designing for children aged 4 to 6

- No timers, no "you lost" screens, no penalties: a game ends when it is completed.
- Things that fall fall gently: whatever reaches the ground bounces back up, there are no lives,
  the speed adapts to the child, and a level ends after a number of right answers.
- Every tap target is at least 96 px (`style.MIN_TARGET`). Icons and pictures first, text second.
- Feedback is spoken or visual (the letter's name, green for a match), not written.
- No network, ads, analytics or purchases with real money. The only personal data is a first
  name and an age, kept on the device.
- Rewards: stars mark progress (1 to 3 per level; a win never gives 0), coins buy cosmetic items.

## Assets

- Every font, sound and image in `src/edugames/assets/` is listed in `CREDITS.md` with its source
  and licence. Only licences that allow redistribution (OFL, public domain, CC0, MIT). A test
  checks the list against the files.
- Generated assets come from a script in `scripts/` that can run again. Tools with other licences
  (for example Piper, GPL) run through `uvx` and are never dependencies.
- Prefer shapes drawn in code (the avatar) when colours or variants must change.

## Art style

- A navy outline (`style.OUTLINE`) around every shape, and one flat cel shade per shape.
- Gloss (a gradient and a white shine) only on rewards and main actions: stars, coins and the
  green main button (`Button(primary=True)`). Other buttons are white.
- Fredoka (`style.title_font`) for titles, buttons and numbers; Andika (`style.font`) for letters
  and names, because it is made for children learning to read.
- On cards, vowels are red and consonants blue (Montessori colours), as the content says.
- Each level of a path has a theme (`ui/scenery.py`); other screens use the meadow.
- Draw at twice the size and scale down (`ui/paint.py`), and cache what is drawn (backgrounds,
  avatars, boxes, stars, coins), so a frame only blits.

## Platforms and sandbox

- The game runs from source on macOS, Linux and Windows. Use `pathlib` and `platformdirs`; no
  shell-only steps are required to play or test (every step is a `uv run` command).
- CI (`.github/workflows/tests.yml`) runs ruff and pytest on macOS, Ubuntu and Windows.
- The root `.sh` scripts are helpers for Linux and macOS sandboxes (no screen, no sound card,
  maybe no network): `test-sandbox.sh` runs the checks, `run-sandbox.sh` plays a scripted game
  and saves screenshots, and `sandbox-deps.sh` installs dependencies offline first, with a
  fallback when the lockfile's versions are not available. They are versioned as executable.

## Tests

- Every behaviour change comes with tests. pytest, with UI tests running headless
  (`SDL_VIDEODRIVER=dummy`, `SDL_AUDIODRIVER=dummy`) and driving screens with real events.
- Line coverage at least 80% (`[tool.coverage.report] fail_under`); `uv run pytest` fails below it.
- Each slice has `docs/S<n>_<name>.md` with its acceptance criteria `S<n>_AC<m>`. Every criterion
  has at least one test, and every test is named after its criteria (`test_S1_AC7_…`). A test
  checks that the doc lists exactly the tests that exist.

## Style

- `ruff format` and `ruff check` (rules E, F, I, UP, B), line length 100.
- No commented-out code and no debugging `print`.

## Workflow

- No orchestrator for now: work happens in a Claude Code session, following the 6-phase workflow
  (understand, plan, execute, test, manual validation, finalize). Commit messages are confirmed
  by the owner.
- Decisions that change these rules are recorded as ADRs in `docs/adr/`.
