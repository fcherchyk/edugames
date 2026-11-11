"""The window, the main loop and the current screen (scene)."""

import asyncio
import random
from pathlib import Path

import pygame

from edugames import APP_NAME
from edugames.core import storage
from edugames.core.content import Content, load_content
from edugames.core.profiles import Profile, ProfileStore
from edugames.ui import style
from edugames.ui.audio import Audio
from edugames.ui.scenes.base import Scene

FPS = 60


class App:
    def __init__(
        self,
        content: Content,
        store: ProfileStore,
        audio: Audio,
        surface: pygame.Surface,
        rng: random.Random | None = None,
    ) -> None:
        self.content = content
        self.store = store
        self.audio = audio
        self.surface = surface
        self.rng = rng or random.Random()
        self.profile: Profile | None = None
        self.running = True
        from edugames.ui.scenes.profiles import ProfileSelectScene

        self.scene: Scene = ProfileSelectScene(self)

    def go(self, scene: Scene) -> None:
        self.scene = scene

    def save(self) -> None:
        self.store.save()

    def step(self, events: list[pygame.event.Event], dt_ms: int) -> None:
        """One frame: events, then time, then drawing."""
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                return
            self.scene.handle(event)
        self.scene.update(dt_ms)
        self.scene.draw(self.surface)

    async def run(self) -> None:
        clock = pygame.time.Clock()
        while self.running:
            self.step(pygame.event.get(), clock.tick(FPS))
            pygame.display.flip()
            await asyncio.sleep(0)  # lets a pygbag (web) build run the same loop


def open_window() -> pygame.Surface:
    pygame.display.set_caption(APP_NAME)
    return pygame.display.set_mode(style.SIZE, pygame.SCALED | pygame.RESIZABLE)


def create_app(data_dir: Path | None = None, surface: pygame.Surface | None = None) -> App:
    pygame.init()
    content = load_content()
    store = ProfileStore(data_dir or storage.default_data_dir())
    return App(content, store, Audio(content), surface or open_window())
