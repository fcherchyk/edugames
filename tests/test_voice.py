"""S3_AC18: the game speaks with one voice, so two clips never talk over each other."""

import time

import pygame
import pytest

from edugames.core.profiles import new_profile
from edugames.demo import click, press_key
from edugames.ui.audio import MAX_WAIT_MS, Audio
from edugames.ui.scenes.memory import MemoryScene
from edugames.ui.scenes.profiles import ProfileSelectScene
from edugames.ui.scenes.rain import RainScene


class FakeVoice:
    """A mixer channel that plays in pretend time: each clip lasts its real length."""

    def __init__(self) -> None:
        self.now = 0
        self.left = 0
        self.played: list[tuple[int, int, pygame.mixer.Sound]] = []  # start, end, clip

    def play(self, sound: pygame.mixer.Sound) -> None:
        assert not self.get_busy(), "two clips at once"
        self.left = round(sound.get_length() * 1000)
        self.played.append((self.now, self.now + self.left, sound))

    def get_busy(self) -> bool:
        return self.left > 0

    def elapse(self, ms: int) -> None:
        self.now += ms
        self.left = max(0, self.left - ms)

    def clips(self) -> list[pygame.mixer.Sound]:
        return [sound for _, _, sound in self.played]


@pytest.fixture
def voice(app) -> FakeVoice:
    """The app's audio, speaking through a fake voice that `frame` moves on."""
    app.audio = Audio(app.content)
    app.audio.voice = fake = FakeVoice()
    return fake


def frame(app, voice: FakeVoice, ms: int = 16, events=()) -> None:
    voice.elapse(ms)
    app.step(list(events), ms)


def talk(audio: Audio, voice: FakeVoice, ms: int) -> None:
    for _ in range(ms // 10):
        voice.elapse(10)
        audio.update(10)


def letter(audio: Audio, upper: str) -> pygame.mixer.Sound:
    return audio.sounds[upper]


def word(audio: Audio, picture_id: str) -> pygame.mixer.Sound:
    return audio.sounds[f"word:{picture_id}"]


def no_overlap(voice: FakeVoice) -> bool:
    """Each clip started after the one before had ended."""
    pairs = zip(voice.played, voice.played[1:], strict=False)
    return all(end <= start for (_, end, _), (start, _, _) in pairs)


def test_S3_AC18_clips_wait_their_turn_on_one_voice(app, voice) -> None:
    audio = app.audio
    assert audio.say_letter_and_word("C", "cat")
    assert audio.say_word("moon")
    assert voice.clips() == [letter(audio, "C")] and audio.busy

    talk(audio, voice, 3000)

    # "see… cat" stays together, and "moon" waits until it has ended
    assert voice.clips() == [letter(audio, "C"), word(audio, "cat"), word(audio, "moon")]
    assert no_overlap(voice) and not audio.busy


def test_S3_AC18_hints_are_dropped_when_the_voice_is_busy(app, voice) -> None:
    audio = app.audio
    audio.say_word("octopus")

    assert not audio.say_word("sun", hint=True)
    assert not audio.say_letter("S", hint=True)
    talk(audio, voice, 2000)
    assert audio.say_word("sun", hint=True)  # the voice is free again
    assert len(voice.clips()) == 2


def test_S3_AC18_a_found_pictures_word_and_stale_clips_are_dropped(app, voice) -> None:
    audio = app.audio
    moon = object()
    audio.say_letter_and_word("C", "cat")
    audio.say_word("moon", key=moon)
    audio.cancel(moon)  # the moon was found before its word could be said
    talk(audio, voice, 3000)
    assert voice.clips() == [letter(audio, "C"), word(audio, "cat")]

    voice.left = MAX_WAIT_MS + 500  # something long is being said
    audio.say_word("sun")
    talk(audio, voice, MAX_WAIT_MS + 1000)
    assert word(audio, "sun") not in voice.clips()  # it would have come too late to help


def test_S3_AC18_on_a_sound_device_two_clips_never_play_together(content) -> None:
    pygame.init()
    audio = Audio(content)
    pygame.mixer.stop()  # a clip from an earlier test may still be playing on the shared mixer
    channels = [pygame.mixer.Channel(i) for i in range(pygame.mixer.get_num_channels())]
    audio.say_letter_and_word("E", "egg")
    audio.say_word("dog")
    heard = []

    start = time.perf_counter()
    while (audio.busy or not heard) and time.perf_counter() - start < 3:
        audio.update(10)
        assert sum(channel.get_busy() for channel in channels) <= 1
        sound = channels[0].get_sound()
        if sound is not None and (not heard or heard[-1] is not sound):
            heard.append(sound)
        time.sleep(0.01)

    assert heard == [letter(audio, "E"), word(audio, "egg"), word(audio, "dog")]


def test_S3_AC18_in_the_game_the_next_pictures_word_waits_for_see_cat(app, voice) -> None:
    app.store.add(new_profile("Sam", 5))
    app.scene = ProfileSelectScene(app)
    click(app, "profile:Sam")
    app.go(RainScene(app, "rain", "6"))
    scene = app.scene
    found = []
    for _ in range(6):  # a quick child: each picture found 1 second after it appears
        while not scene.game.drops:
            frame(app, voice, 50)
        drop = scene.game.drops[0]
        for _ in range(20):
            frame(app, voice, 50)
        found.append(drop)
        press_key(app, drop.item.answer)
    for _ in range(100):
        frame(app, voice, 50)

    clips = voice.clips()
    assert no_overlap(voice)
    for drop in found:  # every picture found was answered with "<letter>… <word>"
        pair = [letter(app.audio, drop.item.answer), word(app.audio, drop.item.shows)]
        assert any(clips[i : i + 2] == pair for i in range(len(clips) - 1)), drop.item.shows


def test_S3_AC18_letter_pairs_speaks_with_the_same_voice(app, voice) -> None:
    app.store.add(new_profile("Sam", 5))
    app.scene = ProfileSelectScene(app)
    click(app, "profile:Sam")
    app.go(MemoryScene(app, "memory", "1"))
    game = app.scene.game
    other = next(i for i, card in enumerate(game.cards) if card.letter != game.cards[0].letter)

    click(app, "card:0")
    click(app, f"card:{other}")  # turned quickly, before the first name has ended
    for _ in range(100):
        frame(app, voice)

    assert voice.clips() == [
        letter(app.audio, game.cards[0].letter),
        letter(app.audio, game.cards[other].letter),
    ]
    assert no_overlap(voice)
