"""What every screen has: buttons, a background and a header."""

from typing import TYPE_CHECKING

import pygame

from edugames.core.content import DEFAULT_THEME
from edugames.core.profiles import Profile
from edugames.ui import paint, style
from edugames.ui.scenery import background
from edugames.ui.widgets import Button, draw_coins

if TYPE_CHECKING:
    from edugames.ui.app import App

MARGIN = 32


class Scene:
    theme = DEFAULT_THEME  # the scenery behind the screen

    def __init__(self, app: "App") -> None:
        self.app = app
        self.buttons: list[Button] = []
        self.layout()

    @property
    def content(self):
        return self.app.content

    @property
    def profile(self) -> Profile:
        assert self.app.profile is not None, "this screen needs a chosen player"
        return self.app.profile

    def layout(self) -> None:
        """Build `self.buttons` for the current state."""

    def handle(self, event: pygame.event.Event) -> None:
        for button in list(self.buttons):
            if button.handle(event):
                return

    def update(self, dt_ms: int) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(background(self.theme), (0, 0))
        self.draw_scene(surface)
        for button in self.buttons:
            button.draw(surface)
        self.draw_overlay(surface)

    def draw_scene(self, surface: pygame.Surface) -> None:
        pass

    def draw_overlay(self, surface: pygame.Surface) -> None:
        pass

    def button(self, name: str) -> Button:
        """The button called `name` (used by the tests and the demo)."""
        for button in self.buttons:
            if button.name == name:
                return button
        raise KeyError(name)

    def back_button(self, label: str, on_click) -> Button:
        rect = pygame.Rect(MARGIN, MARGIN, 220, style.MIN_TARGET)
        return Button(rect, on_click, label=label, name="back")

    def draw_title(self, surface: pygame.Surface, text: str) -> None:
        paint.draw_title_text(surface, text, 64, (style.WIDTH // 2, MARGIN + style.MIN_TARGET // 2))

    def draw_coin_count(self, surface: pygame.Surface) -> None:
        draw_coins(surface, self.profile.coins, (style.WIDTH - 130, MARGIN + style.MIN_TARGET // 2))
