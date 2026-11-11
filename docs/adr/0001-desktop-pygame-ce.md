# ADR 0001: A desktop game with pygame-ce, not a web app

- Status: accepted
- Date: 2026-11-11

## Context

The `~/hworkspace` standard for web projects is a FastAPI API with a React/Vite SPA and
PostgreSQL. EduGames is a set of literacy games for children aged 4 to 6, and the owner wants it
written in Python as much as possible, with Pygame. Pygame does not run in a browser as is.

Options considered:

1. **pygbag web build only**: Pygame compiled to WebAssembly, progress in browser storage. All
   Python, but progress lives in one browser and is lost when site data is cleared.
2. **pygbag + FastAPI/PostgreSQL**: follows the web standard and syncs progress, but needs
   accounts, which for young children raises privacy issues.
3. **React shell with pygbag games in iframes**: easier accessible UI, but mostly TypeScript.
4. **Desktop pygame-ce**: runs from source on macOS, Linux and Windows (pygame-ce ships wheels for
   all three, including Linux arm64), with saved data in local JSON files.

## Decision

Option 4: a desktop app with **pygame-ce** (the community-maintained Pygame fork: more active
releases and wheels for current Python versions).

- No server, no accounts, no network: data stays on the device.
- The main loop is `async` (`await asyncio.sleep(0)` each frame), the pattern pygbag needs, so a
  web build (option 1) can be added later without rewriting the game.
- Game rules live in `edugames.core` with no pygame import, so they are tested without a window,
  and the UI is tested headless with SDL's dummy drivers (also in sandboxes and CI).

## Consequences

- Playing requires `uv` and running from source until a later slice packages executables
  (PyInstaller per OS in CI; unsigned macOS builds show a Gatekeeper warning).
- Progress is per computer; syncing across devices would need the backend of option 2.
- The FastAPI/React/PostgreSQL decisions of `~/hworkspace` do not apply to `~/hgames`.
