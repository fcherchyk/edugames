"""Avatar options and the wardrobe (shirt colours bought with coins)."""

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


class AvatarError(ValueError):
    pass


@dataclass
class Avatar:
    face: str = FACES[0]
    skin: str = "peach"
    hair_style: str = HAIR_STYLES[0]
    hair_color: str = "brown"
    shirt: str = FREE_SHIRTS[0]

    def validate(self) -> "Avatar":
        checks = (
            (self.face, FACES),
            (self.skin, SKIN_TONES),
            (self.hair_style, HAIR_STYLES),
            (self.hair_color, HAIR_COLORS),
            (self.shirt, SHIRT_COLORS),
        )
        for value, options in checks:
            if value not in options:
                raise AvatarError(f"Unknown avatar option: {value!r}")
        return self
