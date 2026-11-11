"""`uv run edugames` (or `python -m edugames`): open the game window."""

import asyncio

import pygame


def main() -> None:  # pragma: no cover - opens a window
    from edugames.ui.app import create_app

    try:
        asyncio.run(create_app().run())
    finally:
        pygame.quit()


if __name__ == "__main__":  # pragma: no cover
    main()
