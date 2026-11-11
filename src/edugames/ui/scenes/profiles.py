"""Choose who is playing, or create a new player: name, age and look."""

import pygame

from edugames.core import avatar as options
from edugames.core.avatar import Avatar
from edugames.core.profiles import (
    MAX_AGE,
    MIN_AGE,
    NAME_MAX_LENGTH,
    ProfileError,
    clean_name,
    new_profile,
)
from edugames.ui import paint, style
from edugames.ui.avatar_draw import draw_avatar, draw_head
from edugames.ui.scenes.base import Scene
from edugames.ui.widgets import Button, draw_text, name_tag

TILE_W, TILE_H = 320, 270
TILES_PER_ROW = 3


def tile_rect(index: int) -> pygame.Rect:
    gap = 40
    row_w = TILES_PER_ROW * TILE_W + (TILES_PER_ROW - 1) * gap
    left = (style.WIDTH - row_w) // 2
    row, col = divmod(index, TILES_PER_ROW)
    return pygame.Rect(left + col * (TILE_W + gap), 190 + row * (TILE_H + gap), TILE_W, TILE_H)


class ProfileSelectScene(Scene):
    def layout(self) -> None:
        self.buttons = []
        for index, profile in enumerate(self.app.store.profiles):

            def draw_tile(surface, rect, profile=profile):
                draw_avatar(surface, profile.avatar, (rect.centerx, rect.centery - 22), 190)
                draw_text(surface, profile.name, 40, (rect.centerx, rect.bottom - 35), title=True)

            self.buttons.append(
                Button(
                    tile_rect(index),
                    lambda profile=profile: self.choose(profile.id),
                    name=f"profile:{profile.name}",
                    draw=draw_tile,
                )
            )
        if not self.app.store.is_full():

            def draw_new(surface, rect):
                plus = pygame.Rect(0, 0, 120, 120)
                plus.center = (rect.centerx, rect.centery - 30)
                paint.draw_box(surface, plus, style.PRIMARY, 60, gloss=True, lip=False)
                paint.draw_title_text(surface, "+", 110, (plus.centerx, plus.centery - 6))
                draw_text(
                    surface,
                    self.content.text("new_player"),
                    36,
                    (rect.centerx, rect.bottom - 35),
                    title=True,
                )

            index = len(self.app.store.profiles)
            self.buttons.append(
                Button(tile_rect(index), self.create, name="new_player", draw=draw_new)
            )

    def choose(self, profile_id: str) -> None:
        from edugames.ui.scenes.home import HomeScene

        self.app.profile = self.app.store.get(profile_id)
        self.app.go(HomeScene(self.app))

    def create(self) -> None:
        self.app.go(ProfileCreateScene(self.app))

    def draw_scene(self, surface: pygame.Surface) -> None:
        self.draw_title(surface, self.content.text("who_is_playing"))


# The look step: one row per choice, each option drawn as it would look.
LOOK_ROWS = (
    ("face", options.FACES),
    ("skin", tuple(options.SKIN_TONES)),
    ("hair_style", options.HAIR_STYLES),
    ("hair_color", tuple(options.HAIR_COLORS)),
)
NAME_STEP, AGE_STEP, LOOK_STEP = "name", "age", "look"


class ProfileCreateScene(Scene):
    def __init__(self, app) -> None:
        self.step = NAME_STEP
        self.name = ""
        self.age: int | None = None
        self.avatar = Avatar()
        super().__init__(app)
        pygame.key.start_text_input()

    def layout(self) -> None:
        back = {NAME_STEP: self.cancel, AGE_STEP: self.to_name, LOOK_STEP: self.to_age}[self.step]
        self.buttons = [self.back_button(self.content.text("back"), back)]
        getattr(self, f"_layout_{self.step}")()

    def _layout_name(self) -> None:
        rect = pygame.Rect(0, 0, 300, style.MIN_TARGET)
        rect.midbottom = (style.WIDTH // 2, style.HEIGHT - 60)
        self.buttons.append(
            Button(
                rect,
                self.to_age,
                label=self.content.text("next"),
                name="next",
                primary=True,
                enabled=self.valid_name(),
            )
        )

    def _layout_age(self) -> None:
        ages = range(MIN_AGE, MAX_AGE + 1)
        size, gap = 150, 30
        left = (style.WIDTH - len(ages) * size - (len(ages) - 1) * gap) // 2
        for i, age in enumerate(ages):
            rect = pygame.Rect(left + i * (size + gap), 330, size, size)
            self.buttons.append(
                Button(
                    rect,
                    lambda age=age: self.choose_age(age),
                    label=str(age),
                    name=f"age:{age}",
                    label_size=80,
                    selected=age == self.age,
                )
            )

    def _layout_look(self) -> None:
        size, gap, left = style.MIN_TARGET, 18, 470
        for row, (field, values) in enumerate(LOOK_ROWS):
            for col, value in enumerate(values):
                rect = pygame.Rect(left + col * (size + gap), 150 + row * (size + 30), size, size)
                self.buttons.append(
                    Button(
                        rect,
                        lambda field=field, value=value: self.choose_look(field, value),
                        name=f"{field}:{value}",
                        draw=lambda surface, rect, field=field, value=value: self._draw_option(
                            surface, rect, field, value
                        ),
                        selected=getattr(self.avatar, field) == value,
                    )
                )
        rect = pygame.Rect(0, 0, 300, style.MIN_TARGET)
        rect.bottomright = (style.WIDTH - 60, style.HEIGHT - 50)
        self.buttons.append(
            Button(rect, self.finish, label=self.content.text("done"), name="done", primary=True)
        )

    def _draw_option(self, surface, rect, field, value) -> None:
        preview = Avatar(**{**vars(self.avatar), field: value})
        draw_head(surface, preview, (rect.centerx, rect.centery + 8), rect.w * 0.36)

    def valid_name(self) -> bool:
        try:
            clean_name(self.name)
        except ProfileError:
            return False
        return True

    def handle(self, event: pygame.event.Event) -> None:
        if self.step == NAME_STEP and event.type == pygame.TEXTINPUT:
            self.type_text(event.text)
        elif self.step == NAME_STEP and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.name = self.name[:-1]
                self.layout()
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER) and self.valid_name():
                self.to_age()
        else:
            super().handle(event)

    def type_text(self, text: str) -> None:
        allowed = "".join(char for char in text if char.isalpha() or char in " -'")
        self.name = (self.name + allowed)[:NAME_MAX_LENGTH]
        self.layout()

    def cancel(self) -> None:
        pygame.key.stop_text_input()
        self.app.go(ProfileSelectScene(self.app))

    def to_name(self) -> None:
        self.step = NAME_STEP
        pygame.key.start_text_input()
        self.layout()

    def to_age(self) -> None:
        pygame.key.stop_text_input()
        self.step = AGE_STEP
        self.layout()

    def choose_age(self, age: int) -> None:
        self.age = age
        self.step = LOOK_STEP
        self.layout()

    def choose_look(self, field: str, value: str) -> None:
        setattr(self.avatar, field, value)
        self.layout()

    def finish(self) -> None:
        from edugames.ui.scenes.home import HomeScene

        assert self.age is not None
        profile = self.app.store.add(new_profile(self.name, self.age, self.avatar))
        self.app.profile = profile
        self.app.go(HomeScene(self.app))

    def draw_scene(self, surface: pygame.Surface) -> None:
        if self.step == NAME_STEP:
            self.draw_title(surface, self.content.text("your_name"))
            box = pygame.Rect(0, 0, 760, 140)
            box.center = (style.WIDTH // 2, 380)
            paint.draw_box(surface, box, style.WHITE, 28, lip=False)
            draw_text(surface, self.name + "|", 80, box.center, bold=True)
        elif self.step == AGE_STEP:
            self.draw_title(surface, self.content.text("how_old"))
        else:
            self.draw_title(surface, self.content.text("your_look"))
            draw_avatar(surface, self.avatar, (240, 432), 420)
            name_tag(surface, self.name, (240, 700))
