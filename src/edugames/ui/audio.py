"""Letter names and picture words, read aloud with one voice. With no sound device, or a missing
clip, the game stays silent and keeps working.

The game speaks with one voice, so two clips never talk over each other: each utterance (a clip,
or a letter's name followed by a word) waits until the one before has ended. A hint (a bounce, a
tap) is dropped when the voice is busy; a waiting utterance can be cancelled (the word of a picture
already found); and one that waited too long is dropped, because it would come too late to help.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import pygame

from edugames.core.content import Content

MAX_WAIT_MS = 2500  # an utterance still waiting after this is dropped
VOICE_CHANNEL = 0  # reserved for speech


class Voice(Protocol):
    """What the audio needs from a mixer channel (a fake one in tests)."""

    def play(self, sound: pygame.mixer.Sound) -> object: ...

    def get_busy(self) -> bool: ...


@dataclass
class Utterance:
    sounds: list[pygame.mixer.Sound]
    key: object = None  # who it is about, so that it can be cancelled
    waited: int = 0  # ms spent waiting for the voice


class Audio:
    def __init__(self, content: Content) -> None:
        self.content = content
        self.sounds: dict[str, pygame.mixer.Sound] = {}
        self.voice: Voice | None = None
        self.speaking: Utterance | None = None
        self.waiting: list[Utterance] = []
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            pygame.mixer.set_reserved(VOICE_CHANNEL + 1)
            self.voice = pygame.mixer.Channel(VOICE_CHANNEL)
            self.enabled = True
        except pygame.error:
            self.enabled = False

    # --- Clips ----------------------------------------------------------------------------------

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

    # --- Speaking -------------------------------------------------------------------------------

    def say_letter(self, upper: str, *, hint: bool = False, key: object = None) -> bool:
        """Say the letter's name; False if nothing will be said."""
        return self._say([self._letter(upper)], hint, key)

    def say_word(self, picture_id: str, *, hint: bool = False, key: object = None) -> bool:
        """Say the picture's word; False if nothing will be said."""
        return self._say([self._word(picture_id)], hint, key)

    def say_letter_and_word(self, upper: str, picture_id: str) -> bool:
        """The letter's name, then the picture's word ("see… cat"), as one utterance."""
        return self._say([self._letter(upper), self._word(picture_id)], False, None)

    @property
    def busy(self) -> bool:
        """Something is being said, or waits to be said."""
        voice_busy = self.voice is not None and self.voice.get_busy()
        return voice_busy or bool(self.speaking and self.speaking.sounds) or bool(self.waiting)

    def cancel(self, key: object) -> None:
        """Drop what waits to be said about `key` (what is being said ends normally)."""
        self.waiting = [utterance for utterance in self.waiting if utterance.key is not key]

    def update(self, dt_ms: int) -> None:
        """Called every frame: age what waits, and let the voice say the next clip."""
        for utterance in self.waiting:
            utterance.waited += dt_ms
        self._next()

    def _say(self, clips: list[pygame.mixer.Sound | None], hint: bool, key: object) -> bool:
        sounds = [sound for sound in clips if sound is not None]  # a missing clip is skipped
        if not sounds or self.voice is None or (hint and self.busy):
            return False
        self.waiting.append(Utterance(sounds, key))
        self._next()
        return True

    def _next(self) -> None:
        if self.voice is None or self.voice.get_busy():
            return
        if self.speaking and self.speaking.sounds:  # the word after the letter's name
            self.voice.play(self.speaking.sounds.pop(0))
            return
        self.speaking = None
        while self.waiting:
            utterance = self.waiting.pop(0)
            if utterance.waited > MAX_WAIT_MS:
                continue  # too late to help
            self.speaking = utterance
            self.voice.play(utterance.sounds.pop(0))
            return
