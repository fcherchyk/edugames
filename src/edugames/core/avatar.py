"""Avatar options (the look, changed for free), and the items bought with coins in the shop: shirt
colours, and hats, glasses, wings, shoes and pets on top of the look."""

from dataclasses import dataclass

Color = tuple[int, int, int]

FACES = ("smile", "grin", "calm", "wink")
SKIN_TONES: dict[str, Color] = {
    "light": (255, 224, 196),
    "peach": (241, 194, 160),
    "tan": (205, 150, 110),
    "brown": (150, 100, 70),
    "deep": (100, 65, 45),
}
HAIR_STYLES = ("short", "long", "curly", "bun", "spiky")
HAIR_COLORS: dict[str, Color] = {
    "black": (40, 35, 35),
    "brown": (110, 70, 40),
    "blond": (235, 200, 100),
    "red": (190, 80, 40),
    "blue": (70, 130, 220),
}
EYE_COLORS: dict[str, Color] = {
    "brown": (95, 62, 40),
    "blue": (60, 125, 205),
    "green": (70, 150, 85),
    "hazel": (160, 115, 50),
    "grey": (120, 132, 150),
}
FRECKLES = (False, True)


@dataclass(frozen=True)
class ShirtColor:
    rgb: Color
    price: int


SHIRT_COLORS: dict[str, ShirtColor] = {
    "red": ShirtColor((220, 60, 60), 0),
    "blue": ShirtColor((60, 110, 220), 0),
    "green": ShirtColor((60, 170, 90), 5),
    "yellow": ShirtColor((245, 200, 40), 5),
    "purple": ShirtColor((150, 80, 200), 5),
    "orange": ShirtColor((245, 140, 40), 5),
    "pink": ShirtColor((240, 120, 180), 5),
    "teal": ShirtColor((40, 170, 170), 5),
}
FREE_SHIRTS = tuple(name for name, shirt in SHIRT_COLORS.items() if shirt.price == 0)

# Where an item is worn. A shirt is always worn; the others can be taken off ("" is nothing;
# without shoes from the shop, the avatar wears its own red ones).
SHIRT = "shirt"
ACCESSORY_SLOTS = ("head", "eyes", "back", "feet", "pet")
SLOTS = (*ACCESSORY_SLOTS, SHIRT)  # the order of the shop's tabs
NOTHING = ""


@dataclass(frozen=True)
class Item:
    """Something the avatar wears, drawn in code (`ui/items_draw.py`). `world` is the theme of
    the levels that open it (win one, in any game); None if it is in the shop from the start."""

    id: str
    slot: str
    price: int
    world: str | None = None
    kind: str | None = None  # pets come in kinds (cat, dog...), shown one kind at a time


# Prices are small round numbers a child can count to (by fives): 5 is one or two wins, 10 is two
# or three, 25 to 30 is a dream saved for over a few days. Each world of the path opens three or
# four items.
ITEMS: dict[str, Item] = {
    item.id: item
    for item in (
        Item("cap", "head", 0),
        Item("party_hat", "head", 5),
        Item("bunny_ears", "head", 10),
        Item("flower_crown", "head", 10, "meadow"),
        Item("woolly_hat", "head", 10, "snow"),
        Item("wizard_hat", "head", 20, "forest"),
        Item("space_helmet", "head", 25, "space"),
        Item("crown", "head", 30),
        Item("round_glasses", "eyes", 0),
        Item("sunglasses", "eyes", 5, "beach"),
        Item("heart_glasses", "eyes", 10),
        Item("star_glasses", "eyes", 10),
        Item("ski_goggles", "eyes", 10, "snow"),
        Item("hero_mask", "eyes", 15),
        Item("cape", "back", 10),
        Item("butterfly_wings", "back", 15, "meadow"),
        Item("bird_wings", "back", 20, "beach"),
        Item("dragon_wings", "back", 25, "forest"),
        Item("jetpack", "back", 30, "space"),
        Item("sneakers", "feet", 0),
        Item("bunny_slippers", "feet", 10),
        Item("rain_boots", "feet", 10, "forest"),
        Item("flippers", "feet", 10, "beach"),
        Item("snow_boots", "feet", 15, "snow"),
        Item("roller_skates", "feet", 20),
        Item("rocket_boots", "feet", 25, "space"),
        Item("kitten", "pet", 10, kind="cat"),
        Item("ginger_cat", "pet", 15, kind="cat"),
        Item("black_cat", "pet", 15, kind="cat"),
        Item("lion_cub", "pet", 25, kind="cat"),
        Item("puppy", "pet", 10, kind="dog"),
        Item("dalmatian", "pet", 15, kind="dog"),
        Item("poodle", "pet", 20, kind="dog"),
        Item("husky", "pet", 20, kind="dog"),
        Item("chick", "pet", 10, "meadow", kind="bird"),
        Item("parrot", "pet", 20, "beach", kind="bird"),
        Item("owl", "pet", 20, kind="bird"),
        Item("penguin", "pet", 20, "snow", kind="bird"),
        Item("fuzzy_monster", "pet", 15, kind="monster"),
        Item("one_eyed_monster", "pet", 20, kind="monster"),
        Item("baby_dragon", "pet", 30, "forest", kind="monster"),
        Item("robot", "pet", 20, kind="robot"),
        Item("robo_dog", "pet", 25, kind="robot"),
        Item("drone", "pet", 30, "space", kind="robot"),
    )
}


PET_KINDS = ("cat", "dog", "bird", "monster", "robot")  # the pets tab shows one kind at a time


def pets_of(kind: str) -> tuple[Item, ...]:
    return tuple(item for item in ITEMS.values() if item.slot == "pet" and item.kind == kind)


def items_for(slot: str) -> tuple[Item, ...]:
    """Everything the shop offers for `slot`, shirts included, in the shop's order."""
    if slot == SHIRT:
        return tuple(Item(color, SHIRT, shirt.price) for color, shirt in SHIRT_COLORS.items())
    return tuple(item for item in ITEMS.values() if item.slot == slot)


def item(slot: str, item_id: str) -> Item:
    for candidate in items_for(slot):
        if candidate.id == item_id:
            return candidate
    raise AvatarError(f"No {slot} item {item_id!r}")


class AvatarError(ValueError):
    pass


@dataclass
class Avatar:
    face: str = FACES[0]
    skin: str = "peach"
    hair_style: str = HAIR_STYLES[0]
    hair_color: str = "brown"
    shirt: str = FREE_SHIRTS[0]
    head: str = NOTHING
    eyes: str = NOTHING  # glasses or a mask (the colour of the eyes is `eye_color`)
    back: str = NOTHING
    feet: str = NOTHING
    pet: str = NOTHING
    eye_color: str = "brown"
    freckles: bool = False

    def validate(self) -> "Avatar":
        checks = (
            (self.face, FACES),
            (self.skin, SKIN_TONES),
            (self.hair_style, HAIR_STYLES),
            (self.hair_color, HAIR_COLORS),
            (self.shirt, SHIRT_COLORS),
            (self.eye_color, EYE_COLORS),
        )
        for value, options in checks:
            if value not in options:
                raise AvatarError(f"Unknown avatar option: {value!r}")
        if not isinstance(self.freckles, bool):
            raise AvatarError(f"Freckles are on or off, not {self.freckles!r}")
        for slot in ACCESSORY_SLOTS:
            value = getattr(self, slot)
            if value != NOTHING and (value not in ITEMS or ITEMS[value].slot != slot):
                raise AvatarError(f"Unknown {slot} item: {value!r}")
        return self

    def wearing(self, item: Item) -> "Avatar":
        """A copy of this look with `item` on (to try it on without changing anything)."""
        return Avatar(**{**vars(self), item.slot: item.id})

    def bare(self) -> "Avatar":
        """A copy of this look with no hat, glasses, wings, shoes or pet (only the shirt)."""
        return Avatar(**{**vars(self), **dict.fromkeys(ACCESSORY_SLOTS, NOTHING)})

    def outfit(self) -> tuple[str, ...]:
        """The items worn, one per slot ("" where there is none)."""
        return tuple(getattr(self, slot) for slot in SLOTS)
