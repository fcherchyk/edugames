# Slice 3: Letter Rain, with letter levels and picture levels

## What slice 3 delivers

A second game, and the platform changes that any later game needs:

- **Letter Rain:** letters fall gently from the sky. The child finds each one on the keyboard (the
  real one, or the one on the screen) and it pops. A letter that reaches the ground bounces back
  up: nothing is lost, there are no lives and no game over, and the speed adapts to the child.
- **Picture levels:** after the five letter levels, the rain brings pictures (an apple, a cat, the
  moon). Each picture says its word, and the child finds its **first letter**. This was "Picture
  Rain" (slice 6 in the old roadmap); it is the same game with different things falling.
- **Tap one of three:** on picture levels, the youngest players (under 5) get three big letters
  to choose from instead of the whole keyboard.
- **The on-screen keyboard:** laid out like the real one (QWERTY in English, from the content),
  each key showing the capital and the small letter. It can be hidden by a child who prefers the
  real keyboard, and that choice is remembered for the player.
- **A picture library:** 22 pictures drawn in code in the art style, each a language-neutral
  concept that the locale maps to a word, its first letter and a spoken clip.
- **Levels per game:** each game has its own levels file and its own goal path. The path fits ten
  levels, in two rows.
- **Every answer recorded:** for each letter (and picture), how often it was found and which key
  was pressed instead. Nothing shows this yet; the parents' area (slice 11) and adaptive practice
  will.

## How it plays

1. A letter (or a picture, on a white card) appears at the top of the sky, in a random lane, and
   falls. Letters are in Montessori colours (vowels red, consonants blue) and in the level's case:
   capitals, small letters, or both mixed. Pictures have no text and say their word as they appear.
2. The child presses the letter: on the real keyboard (Caps Lock and Shift do not matter), on a
   key of the on-screen keyboard, or, for the youngest on picture levels, on one of three big
   letters.
   - **Right:** the item pops with a sparkle, the key flashes green, and the letter's name is said
     (on picture levels, the letter's name and then the word: "see… cat").
   - **Wrong:** the key flashes orange. Nothing is said and nothing is lost.
3. An item that reaches the ground bounces back up to the top, says its name again as a hint, and
   falls again.
4. Three right answers in a row make the rain a little faster; a wrong key or a bounce makes it a
   little slower.
5. A row of dots fills in gold with each right answer. When the row is full (the level's goal),
   the victory pop-up of Letter Pairs shows the avatar, 1 to 3 stars and the coins.

## Content

Everything a language changes is in `content/<locale>/` and `assets/audio/<locale>/`.

**`games.json`:** Letter Rain is playable from age 4 to 7:

```json
{"id": "rain", "title": "Letter Rain", "icon": "Rr", "min_age": 4, "max_age": 7, "playable": true}
```

The "First Letter" placeholder is removed: its idea is now Letter Rain's picture levels. Letter
Sounds and Draw Letters stay as "coming soon", so a 5- or 6-year-old sees four tiles.

**`<game id>_levels.json`:** the levels of each playable game (`memory_levels.json` stays as it
is; `rain_levels.json` is new). A rain level has either `letters` or `pictures` (a list of ids,
or `"*"` for all of them):

```json
{"id": "1", "letters": ["A", "M", "O", "S", "T"], "case": "upper", "goal": 8,
 "at_once": 1, "fall_seconds": 9, "theme": "meadow"}
{"id": "6", "pictures": ["apple", "ball", "moon", "sun", "fish", "egg"], "goal": 8,
 "at_once": 1, "fall_seconds": 11, "theme": "meadow"}
```

| Field | Meaning |
|---|---|
| `letters` / `pictures` | what can fall (exactly one of the two) |
| `case` | letter levels only: `upper`, `lower` or `both` |
| `goal` | right answers that finish the level |
| `at_once` | how many items fall at the same time (1 to 3) |
| `fall_seconds` | how long an item takes from the top to the ground, at normal speed |
| `theme` | the scenery, as for Letter Pairs (meadow if missing) |

The English levels:

| Level | Falls | Case | Goal | At once | Seconds | World |
|---|---|---|---|---|---|---|
| 1 | A M O S T | upper | 8 | 1 | 9 | meadow |
| 2 | A E I O U M S T P N | upper | 10 | 1 | 8 | beach |
| 3 | the same letters | lower | 10 | 1 | 8 | forest |
| 4 | B D P Q N U A E I O | both | 12 | 2 | 8 | snow |
| 5 | every letter | both | 12 | 2 | 7 | space |
| 6 | apple, ball, moon, sun, fish, egg | | 8 | 1 | 11 | meadow |
| 7 | cat, dog, hat, pig, tree, leaf, key, sun | | 10 | 1 | 10 | beach |
| 8 | umbrella, igloo, octopus, apple, egg, jam, rainbow, volcano | | 10 | 1 | 10 | forest |
| 9 | ball, dog, pig (b, d, p), grapes, watermelon, yo-yo, key, cat | | 12 | 2 | 10 | snow |
| 10 | every picture | | 12 | 2 | 9 | space |

**`pictures.json`:** the pictures this language uses, each with its word and first letter (the
letter is content, not `word[0]`: "árbol" starts with A, and a picture whose word starts with a
silent letter is simply left out of that language):

```json
{"pictures": [{"id": "cat", "word": "cat", "letter": "C"}, ...]}
```

English: apple, ball, cat, dog, egg, fish, grapes, hat, igloo, jam, key, leaf, moon, octopus, pig,
rainbow, sun, tree, umbrella, volcano, watermelon, yo-yo: 22 pictures, one per letter except N, Q,
X and Z, whose words are hard to draw without doubt (a nest with eggs reads as "eggs"). Each word
is spoken when the picture appears, so a child who thinks "kitty" hears "cat".

**`keyboard.json`:** the rows of the on-screen keyboard, as on the real keyboard of that language
(the Spanish one will have `Ñ` after `L`):

```json
{"rows": [["Q","W","E","R","T","Y","U","I","O","P"], ["A","S","D","F","G","H","J","K","L"],
          ["Z","X","C","V","B","N","M"]]}
```

**Audio:** `assets/audio/<locale>/words/<picture id>.wav`, generated by
`scripts/generate_word_audio.py` with Piper and the same voice as the letter names, and credited
in `CREDITS.md`.

**Saved data:** each profile in `profiles.json` gains two optional fields (older files load as
they are; the schema version does not change):

```json
"answers": {"letters": {"B": {"right": 4, "wrong": {"D": 2}}},
            "pictures": {"cat": {"right": 1, "wrong": {"K": 1}}}},
"settings": {"keyboard": false}
```

## Code

- `core/rain_game.py` (no pygame): `RainGame` with `advance(ms)`, `press(letter)` and the items
  in flight, each with what it shows, the letter that clears it, a lane and a height from 0 (top)
  to 1 (ground). Letter and picture levels are the same game: only what an item shows changes.
- `core/content.py`: levels per game, rain levels, pictures and the keyboard, with their checks.
- `core/progress.py`: answers per letter and per picture; `stars_for` with generic names.
- `core/profiles.py`: `answers` and `settings`.
- `ui/scenes/level.py`: what every game level shares (the victory pop-up, next level, back to the
  path), used by Letter Pairs and Letter Rain.
- `ui/scenes/rain.py`: the Letter Rain screen; `ui/keyboard.py`: the on-screen keyboard;
  `ui/pictures.py`: the picture drawings, made with `paint.Pen` (the outlined shapes the avatar
  is drawn with, now shared).
- `ui/scenes/path.py`: any game's levels, in one row up to five, in two rows up to ten.
- `demo.py`: the demo also plays Letter Rain.

## Not in slice 3

- The picture album (stickers for the words learnt): slice 6, now on its own.
- New worlds for the picture levels: they reuse the five worlds of the letter levels.
- Showing the recorded answers, or using them to repeat confused letters.
- A speed setting, or keeping the speed from one level to the next (each level starts at its own
  speed).
- Tap one of three on letter levels; sound effects; animations beyond the pop and the bounce.
- Spanish content (the code is ready for it: keyboard, pictures and levels are content).

## Roadmap changes

The README's roadmap changes with this slice:

- **S3** becomes *Letter Rain, with letter levels and picture levels*.
- **S6** becomes *Picture album* alone (every word found in Letter Rain becomes a sticker). It
  builds on the pictures and on the answers per picture recorded from S3. The numbers of the other
  slices do not change.
- "The gentle fall" refers to S3 only. S7 (Numbers) and S8 (Fill the Gaps) build on the pictures
  of S3 instead of S6.

## Decisions

Taken with the owner before this slice started:

- The on-screen keyboard mirrors the real one (QWERTY in English, from `keyboard.json`), and can be
  hidden; the choice is saved per player in a generic `settings` (room for slice 11's settings).
- Keys of letters outside the level are muted but can be pressed (a miss).
- A bounce counts as a miss for the stars, as generous as Letter Pairs: at most one miss per right
  answer gives 3 stars.
- A wrong key is silent; the name is said on a right key, on a bounce and when an item is tapped.
  Tapping a falling item only says its name: finding the key is the game.
- One item at a time on the first levels, two at most on the last; never three for this age.
- Answers are recorded per letter across games, with the key pressed instead; Letter Pairs does
  not record answers yet. They are saved at the end of a level and when leaving it.
- Letter Pairs' level flow and victory pop-up move into a shared `LevelScene`.
- Picture Rain joins this slice as Letter Rain's picture levels, with tap one of three for the
  youngest; the picture album stays a slice of its own.
- The "First Letter" placeholder is removed, so the home keeps its 2×2 grid.

## Acceptance criteria

Each criterion lists its tests. `tests/test_project.py` (S1_AC18) checks that this list and the
tests agree.

### S3_AC1: Each game has its own levels and goal path

A playable game's levels come from `<game id>_levels.json`; a playable game with no levels is
refused when the content loads. Each game's path shows its own levels and opens its own screen,
and stars are kept per game: winning Letter Rain's level 1 does not open Letter Pairs' level 2.
Letter Pairs plays as before.

- `tests/test_content.py::test_S3_AC1_each_playable_game_loads_its_own_levels`
- `tests/test_content.py::test_S3_AC1_a_playable_game_without_levels_is_refused`
- `tests/test_progress.py::test_S3_AC1_progress_is_kept_per_game`
- `tests/test_rain_ui.py::test_S3_AC1_each_path_shows_its_game_levels_and_opens_its_game`

### S3_AC2: Letter Rain is offered from age 4 to 7

Letter Rain is playable for ages 4 to 7 and comes right after Letter Pairs on the home. "First
Letter" is gone: a 5-year-old sees Letter Pairs, Letter Rain, and Letter Sounds and Draw Letters
as "coming soon". Tapping Letter Rain opens its goal path.

- `tests/test_content.py::test_S3_AC2_letter_rain_is_offered_from_age_4_to_7`
- `tests/test_rain_ui.py::test_S3_AC2_home_opens_the_letter_rain_path`

### S3_AC3: Rain levels are content

The ten English rain levels load from `rain_levels.json`: five letter levels, then five picture
levels. A level is refused if it has both or neither of `letters` and `pictures`, an unknown or
repeated letter or picture, an unknown case, a goal under 1, an `at_once` outside 1 to 3 or
larger than the number of different answer letters, or a `fall_seconds` that is not positive.

- `tests/test_content.py::test_S3_AC3_english_rain_levels_load`
- `tests/test_content.py::test_S3_AC3_a_wrong_rain_level_is_refused`

### S3_AC4: Pictures are content, drawn in code

The 22 English pictures load from `pictures.json`, each with its word, its first letter and its
clip. A picture with an unknown letter, a repeated id or no clip is refused. Every picture is
drawn in shapes, with the navy outline and no text, once per size and then reused; an id with no
drawing gets a plain fallback instead of a crash.

- `tests/test_content.py::test_S3_AC4_english_pictures_load_with_their_first_letter`
- `tests/test_content.py::test_S3_AC4_a_wrong_picture_is_refused`
- `tests/test_pictures.py::test_S3_AC4_every_picture_is_drawn_with_the_navy_outline`
- `tests/test_pictures.py::test_S3_AC4_an_unknown_picture_draws_a_fallback`
- `tests/test_pictures.py::test_S3_AC4_a_picture_is_drawn_once_and_then_reused`

### S3_AC5: Letters and pictures fall

Items appear at the top in random lanes and fall. Letters are in the level's case (with `both`,
each letter comes as a capital or a small letter at random); a picture's answer is its first
letter. At most `at_once` items fall together, never two with the same answer letter and never two
in the same lane, and a new one arrives shortly after one is found.

- `tests/test_rain_game.py::test_S3_AC5_letters_fall_in_the_levels_case`
- `tests/test_rain_game.py::test_S3_AC5_pictures_fall_and_their_answer_is_the_first_letter`
- `tests/test_rain_game.py::test_S3_AC5_no_more_than_at_once_fall_and_never_the_same_answer_twice`
- `tests/test_rain_game.py::test_S3_AC5_a_new_item_arrives_after_one_is_found`

### S3_AC6: The on-screen keyboard

The keyboard has the rows of `keyboard.json`; a keyboard that misses, repeats or invents a letter
is refused. Every key is at least 96 pixels, fits on the screen and shows its capital and small
letter. The keys of the letters that can fall in the level are lit (in Montessori colours); the
others are muted and can still be pressed.

- `tests/test_content.py::test_S3_AC6_the_keyboard_has_every_letter_once`
- `tests/test_content.py::test_S3_AC6_a_wrong_keyboard_is_refused`
- `tests/test_rain_ui.py::test_S3_AC6_the_keys_are_big_fit_on_screen_and_show_both_cases`
- `tests/test_rain_ui.py::test_S3_AC6_the_levels_letters_are_lit`

### S3_AC7: The keyboard can be hidden

A keyboard button (a drawn keyboard, at least 96 pixels) hides and shows the on-screen keyboard.
Hidden keys are neither drawn nor tappable, items fall down to the grass, and the real keyboard
still works. The choice is saved in the player's `settings` and kept for the next level and the
next time the game starts; a damaged setting is dropped and the profile still loads.

- `tests/test_rain_ui.py::test_S3_AC7_the_keyboard_hides_and_the_real_keys_still_work`
- `tests/test_rain_ui.py::test_S3_AC7_the_choice_is_saved_for_the_player`
- `tests/test_profiles.py::test_S3_AC7_settings_survive_a_restart_and_bad_ones_are_dropped`

### S3_AC8: Finding the letter

The right letter (a real key in either case, or a tapped key) clears the lowest item with that
answer: it pops, the key flashes green and the letter's name is said, followed by the word on
picture levels. A wrong letter while something falls flashes its key orange, says nothing and
counts as a miss. A key while nothing falls, or a key that is not a letter, does nothing. Tapping a
falling item says its name (the letter, or the word) and does not clear it.

- `tests/test_rain_game.py::test_S3_AC8_the_right_key_clears_the_lowest_item_with_that_letter`
- `tests/test_rain_game.py::test_S3_AC8_a_wrong_key_is_a_miss_and_a_key_with_nothing_falling_is_ignored`
- `tests/test_rain_ui.py::test_S3_AC8_a_key_in_either_case_or_a_tap_finds_the_letter`
- `tests/test_rain_ui.py::test_S3_AC8_finding_says_the_letter_and_then_the_word`
- `tests/test_rain_ui.py::test_S3_AC8_a_wrong_key_flashes_silently_and_other_keys_do_nothing`
- `tests/test_rain_ui.py::test_S3_AC8_tapping_a_falling_item_says_its_name`

### S3_AC9: Pictures say their word

A picture says its word when it appears. With no sound device, or a missing clip, the game is
silent and keeps working.

- `tests/test_rain_ui.py::test_S3_AC9_a_picture_says_its_word_when_it_appears`
- `tests/test_rain_ui.py::test_S3_AC9_a_missing_word_clip_is_silent`

### S3_AC10: The youngest tap one of three letters

On picture levels, a player younger than 5 gets three big letters (at least 96 pixels) where the
keyboard would be: the picture's first letter and two others, taken from the level's other
pictures when there are enough, shuffled and new for every picture. One picture falls at a time.
The right letter clears it; a wrong one flashes and counts as a miss. The real keyboard still
works, and there is no keyboard button. Players of 5 and over get the keyboard.

- `tests/test_rain_game.py::test_S3_AC10_the_choices_are_the_answer_and_two_other_letters`
- `tests/test_rain_ui.py::test_S3_AC10_a_four_year_old_taps_one_of_three_letters`
- `tests/test_rain_ui.py::test_S3_AC10_a_five_year_old_gets_the_keyboard`

### S3_AC11: The gentle fall

An item that reaches the ground bounces back up to the top (in half its fall time) and falls
again. The bounce says its name and counts as a miss. There are no lives: however many bounces
and misses, the level only ends at its goal.

- `tests/test_rain_game.py::test_S3_AC11_an_item_that_reaches_the_ground_bounces_back_up`
- `tests/test_rain_ui.py::test_S3_AC11_a_bounce_says_the_name_and_never_ends_the_level`

### S3_AC12: The speed adapts to the child

Each level starts at normal speed (its `fall_seconds`). Every three right answers in a row make it
15% faster, up to 1.6 times; a miss or a bounce makes it 20% slower, down to half speed.

- `tests/test_rain_game.py::test_S3_AC12_three_right_in_a_row_speed_up_to_a_limit`
- `tests/test_rain_game.py::test_S3_AC12_a_miss_or_a_bounce_slows_down_to_a_limit`

### S3_AC13: A level ends at its goal

A row of dots, one per right answer of the goal, fills in gold. At the goal, the items left
vanish and the victory pop-up shows the stars (3 with at most one miss per right answer, 2 with at
most two, otherwise 1) and the coins (2 plus 1 per star, replays included). The next level opens;
the last level has no "Next level" button.

- `tests/test_rain_game.py::test_S3_AC13_the_level_ends_after_its_goal_of_right_answers`
- `tests/test_progress.py::test_S3_AC13_stars_come_from_the_misses`
- `tests/test_rain_ui.py::test_S3_AC13_a_win_shows_the_popup_saves_stars_and_coins_and_opens_the_next_level`
- `tests/test_rain_ui.py::test_S3_AC13_the_last_level_has_no_next_level_button`

### S3_AC14: A goal path of ten levels

A path with more than five levels shows them in two rows of up to five (letters above, pictures
below), joined by one road. Stones are at least 96 pixels; stones, stars and the avatar fit on
the screen and do not overlap; the avatar stands on the first open level not won yet. Letter
Pairs' path of five is unchanged.

- `tests/test_rain_ui.py::test_S3_AC14_a_ten_level_path_fits_in_two_rows_without_overlaps`
- `tests/test_rain_ui.py::test_S3_AC14_the_avatar_stands_on_the_current_level`

### S3_AC15: Every answer is recorded

A right answer adds 1 to its letter's `right`; a wrong one adds 1 to `wrong[<key pressed>]` of the
lowest falling item's letter. On picture levels the picture's record is counted too. Bounces are
not answers. Answers are saved when the level ends and when the child leaves it. Profiles saved
before this slice load with no answers; damaged answers are dropped and the profile still loads.

- `tests/test_progress.py::test_S3_AC15_answers_are_counted_per_letter_with_the_key_pressed_instead`
- `tests/test_progress.py::test_S3_AC15_picture_answers_are_counted_per_picture`
- `tests/test_rain_ui.py::test_S3_AC15_answers_are_saved_at_the_end_and_when_leaving`
- `tests/test_profiles.py::test_S3_AC15_old_profiles_load_and_damaged_answers_are_dropped`

### S3_AC16: Drawing stays fast

On a picture level with the keyboard and two items falling, 60 frames draw in under a second
headless.

- `tests/test_rain_ui.py::test_S3_AC16_sixty_frames_of_letter_rain_draw_in_under_a_second`

### S3_AC17: The sandbox demo plays Letter Rain

`python -m edugames.demo <dir>` also saves the Letter Rain path, a letter level, a letter level
with the keyboard hidden, a picture level, a picture level with three letters to choose from, and
a Letter Rain victory.

- `tests/test_project.py::test_S3_AC17_the_demo_plays_letter_rain`
