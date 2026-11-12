"""Letter names and picture words, read aloud. With no sound device, or a missing clip, the game
stays silent and keeps working."""

from pathlib import Path

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

    def _sound(self, key: str, path: Path) -> pygame.mixer.Sound | None:
        if not self.enabled:
            return None
        try:
            if key not in self.sounds:
                self.sounds[key] = pygame.mixer.Sound(path)
        except (pygame.error, FileNotFoundError):
            return None
        return self.sounds[key]

    def _letter(self, upper: str) -> pygame.mixer.Sound | None:
        return self._sound(upper, self.content.letter_audio(upper))

    def _word(self, picture_id: str) -> pygame.mixer.Sound | None:
        return self._sound(f"word:{picture_id}", self.content.word_audio(picture_id))

    def say_letter(self, upper: str) -> bool:
        """Play the letter's name; False if nothing could be played."""
        sound = self._letter(upper)
        if sound is None:
            return False
        sound.play()
        return True

    def say_word(self, picture_id: str) -> bool:
        """Play the picture's word; False if nothing could be played."""
        sound = self._word(picture_id)
        if sound is None:
            return False
        sound.play()
        return True

    def say_letter_and_word(self, upper: str, picture_id: str) -> bool:
        """The letter's name, then the picture's word ("see… cat")."""
        letter, word = self._letter(upper), self._word(picture_id)
        if letter is None:
            return self.say_word(picture_id)
        channel = letter.play()
        if word is not None and channel is not None:
            channel.queue(word)
        return True
