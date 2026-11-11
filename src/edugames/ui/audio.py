"""Letter names, read aloud. With no sound device the game stays silent and keeps working."""

import pygame

from edugames.core.content import Content


class Audio:
    def __init__(self, content: Content) -> None:
        self.content = content
        self.sounds: dict[str, pygame.mixer.Sound] = {}
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            self.enabled = True
        except pygame.error:
            self.enabled = False

    def say_letter(self, upper: str) -> bool:
        """Play the letter's name; False if nothing could be played."""
        if not self.enabled:
            return False
        try:
            if upper not in self.sounds:
                self.sounds[upper] = pygame.mixer.Sound(self.content.letter_audio(upper))
            self.sounds[upper].play()
        except (pygame.error, FileNotFoundError):
            return False
        return True
