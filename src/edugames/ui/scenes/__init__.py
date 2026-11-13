"""The screens: choose or create a player, home, goal path, the games and the shop."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from edugames.ui.app import App
    from edugames.ui.scenes.level import LevelScene


def level_scene(app: "App", game_id: str, level_id: str) -> "LevelScene":
    """The screen that plays `level_id` of the game `game_id`."""
    from edugames.ui.scenes.memory import MemoryScene
    from edugames.ui.scenes.rain import RainScene

    scenes = {"memory": MemoryScene, "rain": RainScene}
    return scenes[game_id](app, game_id, level_id)
