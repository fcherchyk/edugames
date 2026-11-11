import os

# No window and no sound card needed: set before pygame is imported.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import random  # noqa: E402

import pygame  # noqa: E402
import pytest  # noqa: E402

from edugames.core.content import Content, load_content  # noqa: E402
from edugames.core.profiles import ProfileStore  # noqa: E402
from edugames.ui import style  # noqa: E402
from edugames.ui.app import App  # noqa: E402
from edugames.ui.audio import Audio  # noqa: E402


@pytest.fixture(scope="session")
def content() -> Content:
    return load_content()


@pytest.fixture
def store(tmp_path) -> ProfileStore:
    return ProfileStore(tmp_path)


@pytest.fixture
def app(content, store) -> App:
    pygame.init()
    return App(content, store, Audio(content), pygame.Surface(style.SIZE), random.Random(1))
