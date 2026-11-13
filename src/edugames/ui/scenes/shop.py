"""The avatar shop: hats, glasses, wings, shoes, pets and shirts, tried on for free and bought
with coins, and the "Me" tab, where the look itself (face, skin, hair, eyes, freckles) changes for
free, one thing at a time, in a mirror (`ui/look_picker.py`). Pets are shown one kind at a time
(cats, dogs, birds, monsters, robots): the kinds are chips with no price, the pets have theirs.

A tap on an item the player does not own puts it on the big avatar to try; the green "Buy" pill
(with its price) buys it. Items of a world not won yet show as a shape with a padlock and the
world's icon. A tap on an owned item wears it; a tap on the item being worn takes it off (but not
the shirt).
"""

import pygame

from edugames.core import shop
from edugames.core.avatar import (
    ITEMS,
    PET_KINDS,
    SHIRT,
    SHIRT_COLORS,
    SLOTS,
    Avatar,
    Item,
    items_for,
    pets_of,
)
from edugames.ui import paint, style
from edugames.ui.avatar_draw import draw_avatar, draw_head
from edugames.ui.items_draw import draw_item_icon, draw_shirt, item_icon
from edugames.ui.look_picker import PANEL_COLOR, LookPicker
from edugames.ui.scenery import icon
from edugames.ui.scenes.base import Scene
from edugames.ui.widgets import Button, draw_chip, draw_coin, draw_padlock, draw_text

TILE = 150
GAP = 40
LEFT = 510  # the tabs and the grid of items, right of the avatar
ME = "me"  # the tab of the look, before the tabs of the items
TABS = (ME, *SLOTS)
TAB, TAB_GAP, TABS_Y = style.MIN_TARGET, 8, 140
GRID_Y, ROW_STEP = 276, 228
LOOK_TOP = 256  # the chips of the "Me" tab, under the tabs
MIRROR_CENTER, MIRROR_RADIUS = (250, 390), 170  # the "Me" tab shows a mirror, not the avatar
PET = "pet"
KINDS_TOP = 256  # the pets tab: a chip per kind, then that kind's pets
CHIP_W, CHIP_H, CHIP_GAP = 136, 100, 10
KIND_PICTURES = {
    "cat": "kitten",
    "dog": "puppy",
    "bird": "parrot",
    "monster": "fuzzy_monster",
    "robot": "robot",
}
COLUMNS = 4
TAG = (104, 48)  # the price tag under an item not owned yet
AVATAR_CENTER, AVATAR_HEIGHT = (250, 430), 380
CHEER_MS = 1500  # the avatar cheers this long after buying
TAB_ICONS = {
    "head": "cap",
    "eyes": "round_glasses",
    "back": "butterfly_wings",
    "feet": "sneakers",
    "pet": "kitten",
}
# Tabs are circles, light blue, the open one orange: the gold ring only ever means "on the
# avatar".
TAB_COLOR, OPEN_TAB_COLOR = (205, 225, 250), style.ACCENT


def column_x(col: int) -> int:
    return LEFT + col * (TILE + GAP)


def tab_rect(index: int) -> pygame.Rect:
    return pygame.Rect(LEFT + index * (TAB + TAB_GAP), TABS_Y, TAB, TAB)


def tile_rect(index: int) -> pygame.Rect:
    row, col = divmod(index, COLUMNS)
    return pygame.Rect(column_x(col), GRID_Y + row * ROW_STEP, TILE, TILE)


def kind_rect(index: int) -> pygame.Rect:
    """A chip of the pets tab: five across, under the tabs."""
    return pygame.Rect(LEFT + index * (CHIP_W + CHIP_GAP), KINDS_TOP, CHIP_W, CHIP_H)


def pet_tile_rect(index: int, count: int) -> pygame.Rect:
    """The pets of the open kind: one row under its word, centred."""
    left = LEFT + (720 - (count * (TILE + GAP) - GAP)) // 2
    return pygame.Rect(left + index * (TILE + GAP), KINDS_TOP + 194, TILE, TILE)


def tag_rect(tile: pygame.Rect) -> pygame.Rect:
    rect = pygame.Rect((0, 0), TAG)
    rect.center = (tile.centerx, tile.bottom + 36)
    return rect


class ShopScene(Scene):
    def __init__(self, app, tab: str = SLOTS[0]) -> None:  # opens on the hats
        self.tab = tab
        self.trying: Item | None = None  # on the avatar to try, not bought
        self.cheer_ms = 0
        self.picker = LookPicker(app.content, LEFT, LOOK_TOP)
        worn = app.profile.avatar.pet
        self.pet_kind = ITEMS[worn].kind if worn in ITEMS else PET_KINDS[0]
        super().__init__(app)

    # --- State ----------------------------------------------------------------------------------

    @property
    def look(self) -> Avatar:
        """The avatar as shown: what the player wears, with the item being tried on."""
        avatar = self.profile.avatar
        return avatar.wearing(self.trying) if self.trying else avatar

    def shows(self, item: Item) -> bool:
        return getattr(self.look, item.slot) == item.id

    def is_open(self, item: Item) -> bool:
        return item.id in self.open_ids

    # --- Layout ---------------------------------------------------------------------------------

    def layout(self) -> None:
        self.open_ids = shop.open_items(self.profile, self.content.levels)
        self.buttons = [self.back_button(self.content.text("home"), self.to_home)]
        for index, tab in enumerate(TABS):
            self.buttons.append(
                Button(
                    tab_rect(index),
                    lambda tab=tab: self.open_tab(tab),
                    name=f"tab:{tab}",
                    draw=lambda surface, rect, tab=tab: self._draw_tab(surface, rect, tab),
                    color=OPEN_TAB_COLOR if tab == self.tab else TAB_COLOR,
                    radius=TAB // 2,
                )
            )
        if self.tab == ME:
            self.buttons += self.picker.buttons(self.profile.avatar, self.look_changed, self.layout)
            return
        if self.tab == PET:
            self.buttons += self._kind_chips()
        things = pets_of(self.pet_kind) if self.tab == PET else items_for(self.tab)
        for index, item in enumerate(things):
            open_ = self.is_open(item)
            self.buttons.append(
                Button(
                    pet_tile_rect(index, len(things)) if self.tab == PET else tile_rect(index),
                    lambda item=item: self.choose(item),
                    name=f"{item.slot}:{item.id}",
                    draw=lambda surface, rect, item=item: self._draw_item(surface, rect, item),
                    enabled=open_,
                    selected=open_ and self.shows(item),
                    radius=32,
                )
            )
        if self.trying:
            self.buttons.append(self._buy_button(self.trying))

    def _kind_chips(self) -> list[Button]:
        """The pets tab: a chip per kind of pet (a picture and its word, no price)."""
        chips = []
        for index, kind in enumerate(PET_KINDS):
            chips.append(
                Button(
                    kind_rect(index),
                    lambda kind=kind: self.open_kind(kind),
                    name=f"kind:{kind}",
                    draw=lambda surface, rect, kind=kind: draw_chip(
                        surface, rect, item_icon(KIND_PICTURES[kind], 62), self.kind_word(kind)
                    ),
                    color=OPEN_TAB_COLOR if kind == self.pet_kind else style.PANEL,
                    radius=24,
                )
            )
        return chips

    def kind_word(self, kind: str) -> str:
        return self.content.text(f"pet_{kind}")

    def _buy_button(self, item: Item) -> Button:
        rect = pygame.Rect(0, 0, 320, style.MIN_TARGET)
        rect.center = (AVATAR_CENTER[0], style.HEIGHT - 110)
        return Button(
            rect,
            self.buy,
            name="buy",
            draw=lambda surface, rect: self._draw_buy(surface, rect, item),
            primary=True,
            enabled=self.profile.can_buy(item),
        )

    # --- Actions --------------------------------------------------------------------------------

    def open_tab(self, tab: str) -> None:
        self.tab = tab
        self.trying = None
        self.layout()

    def open_kind(self, kind: str) -> None:
        """Show the pets of another kind (a pet being tried on comes off)."""
        self.pet_kind = kind
        self.trying = None
        self.layout()

    def look_changed(self) -> None:
        """The "Me" tab: the look has changed at once, for free; it is saved."""
        self.app.save()
        self.layout()

    def choose(self, item: Item) -> None:
        """Try an item on, wear it, or take it off (see the module's docstring)."""
        if self.shows(item):
            if self.trying == item:
                self.trying = None
            elif item.slot != SHIRT:  # the worn item comes off
                self.profile.take_off(item.slot)
                self.app.save()
        elif self.profile.owns(item):
            self.trying = None
            self.profile.wear(item)
            self.app.save()
        else:
            self.trying = item
        self.layout()

    def buy(self) -> None:
        assert self.trying is not None
        shop.buy(self.profile, self.trying, self.content.levels)
        self.app.save()
        self.trying = None
        self.cheer_ms = CHEER_MS
        self.layout()

    def to_home(self) -> None:
        from edugames.ui.scenes.home import HomeScene

        self.app.go(HomeScene(self.app))

    def update(self, dt_ms: int) -> None:
        self.cheer_ms = max(0, self.cheer_ms - dt_ms)
        self.picker.update(dt_ms)

    # --- Drawing --------------------------------------------------------------------------------

    def _draw_kind_panel(self, surface: pygame.Surface) -> None:
        """The panel behind the kinds of pets, and the open kind's word over its pets."""
        panel = pygame.Rect(LEFT - 8, KINDS_TOP - 8, 720 + 16, CHIP_H + 16)
        paint.draw_box(surface, panel, PANEL_COLOR, 28, lip=False)
        title = self.kind_word(self.pet_kind)
        paint.draw_title_text(surface, title, 52, (LEFT + 360, KINDS_TOP + 150))

    def _draw_tab(self, surface: pygame.Surface, rect: pygame.Rect, tab: str) -> None:
        center = (rect.centerx, rect.centery - 2)
        if tab == ME:  # the player's own head
            draw_head(surface, self.profile.avatar.bare(), (center[0], center[1] + 6), 27)
        elif tab == SHIRT:
            draw_shirt(surface, SHIRT_COLORS[self.profile.avatar.shirt].rgb, center, 62)
        else:
            draw_item_icon(surface, TAB_ICONS[tab], center, 58)

    def _draw_item(self, surface: pygame.Surface, rect: pygame.Rect, item: Item) -> None:
        center = (rect.centerx, rect.centery - 4)
        open_ = self.is_open(item)
        if item.slot == SHIRT:
            draw_shirt(surface, SHIRT_COLORS[item.id].rgb, center, rect.w * 0.7)
        else:
            draw_item_icon(surface, item.id, center, round(rect.w * 0.72), not open_)
        if not open_:
            draw_padlock(surface, (rect.right - 30, rect.top + 32), 34)
            world = icon(item.world or "", 52)
            surface.blit(world, world.get_rect(center=(rect.left + 30, rect.top + 30)))
        elif not self.profile.owns(item):
            self._draw_price(surface, tag_rect(rect), item)

    def _draw_price(self, surface: pygame.Surface, tag: pygame.Rect, item: Item) -> None:
        """The price on a white tag, or a grey one while the coins are not enough."""
        affordable = self.profile.coins >= item.price
        paint.draw_box(surface, tag, style.WHITE if affordable else style.LOCKED, 24, lip=False)
        draw_coin(surface, (tag.left + 26, tag.centery), 15)
        ink = style.OUTLINE if affordable else style.MUTED
        draw_text(surface, str(item.price), 32, (tag.centerx + 16, tag.centery), ink, title=True)

    def _draw_buy(self, surface: pygame.Surface, rect: pygame.Rect, item: Item) -> None:
        """ "Buy" and the price; while the coins are not enough, how many of them the player
        has, as a gold bar filling up towards the price."""
        cy = rect.centery - 2
        if self.profile.can_buy(item):
            paint.draw_title_text(
                surface, self.content.text("buy"), 44, (rect.x + 100, cy), outline=(60, 115, 40)
            )
            draw_coin(surface, (rect.right - 110, cy), 20)
            paint.draw_title_text(
                surface, str(item.price), 44, (rect.right - 55, cy), outline=(60, 115, 40)
            )
            return
        inner = rect.inflate(-16, -16)
        filled = inner.copy()
        filled.w = round(inner.w * min(1, self.profile.coins / item.price))
        if filled.w:
            pygame.draw.rect(surface, style.GOLD, filled, border_radius=inner.h // 2)
        draw_coin(surface, (rect.x + 60, cy), 20)
        label = f"{self.profile.coins} / {item.price}"
        draw_text(surface, label, 40, (rect.centerx + 24, cy), style.OUTLINE, title=True)

    def draw_scene(self, surface: pygame.Surface) -> None:
        self.draw_title(surface, self.content.text("shop"))
        self.draw_coin_count(surface)
        if self.tab == ME:
            self.picker.draw(surface)
            self.picker.draw_mirror(surface, self.profile.avatar, MIRROR_CENTER, MIRROR_RADIUS)
            return
        if self.tab == PET:
            self._draw_kind_panel(surface)
        cheering = self.cheer_ms > 0
        draw_avatar(surface, self.look, AVATAR_CENTER, AVATAR_HEIGHT, celebrating=cheering)
        if cheering:
            x, y = AVATAR_CENTER
            for dx, dy, r in ((-150, -120, 22), (150, -60, 18), (-120, 90, 16), (140, 130, 20)):
                paint.sparkle(surface, (x + dx, y + dy), r, style.GOLD)
