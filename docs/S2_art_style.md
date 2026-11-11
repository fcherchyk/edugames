# Slice 2: the art style

## What slice 2 delivers

The look of the game, taken from a seed image: a cel-shaded chibi kid, rolling hills, a checkered
ground and green pill buttons. Rules, scoring and saved data do not change.

- **Style:** every shape has a navy outline and one flat cel shade. Gloss (a gradient and a white
  shine) is kept for rewards and main actions: stars, coins and the green main button.
- **Scenery per level:** the path's levels are worlds (meadow, beach, forest, snow, space). Each
  memory level is played in front of its world, and the path shows each world's icon on its
  stepping stone. Other screens use the meadow.
- **Avatar:** a chibi kid with big eyes, drawn in shapes for every face, skin tone, hair style,
  hair colour and shirt; arms up and happy eyes when celebrating.
- **Cards:** the back is blue with a gold star. The letters are in Andika, vowels in red and
  consonants in blue (Montessori colours). Which letters are vowels comes from each language's
  content, not from the code.
- **Fonts:** Fredoka (rounded) for titles, buttons and numbers; Andika stays for letters and names.
- **Speed:** backgrounds, avatars, buttons, stars and coins are drawn once and cached.

## Not in slice 2

- Avatar items (hats, crowns, glasses) bought with coins; gems as a currency.
- Animations (cards flipping, stars popping) and sound effects.
- Pictures for future games (First Letter): they will be language-neutral concepts mapped to a word
  per language (see `docs/standards.md`, Localisation).

## Acceptance criteria

Each criterion lists its tests. `tests/test_project.py` (S1_AC18) checks that this list and the
tests agree.

### S2_AC1: Each level has its own scenery

Each memory level names a theme in `memory_levels.json` (meadow, beach, forest, snow, space). The
memory screen draws its level's scenery, full screen; a theme that is not a name is refused when
the content loads, a level without one gets the meadow, and an unknown name draws the meadow. Each
theme has an icon for its stone on the path.

- `tests/test_art.py::test_S2_AC1_every_level_has_a_theme_that_draws_a_full_screen_scenery`
- `tests/test_art.py::test_S2_AC1_an_unknown_theme_falls_back_to_the_meadow`
- `tests/test_art.py::test_S2_AC1_the_memory_screen_draws_its_level_scenery`
- `tests/test_art.py::test_S2_AC1_every_theme_has_an_icon_for_the_path`
- `tests/test_content.py::test_S2_AC1_a_level_whose_theme_is_not_a_name_is_refused`
- `tests/test_content.py::test_S2_AC1_a_level_without_a_theme_gets_the_meadow`

### S2_AC2: The chibi avatar

Every face, skin tone, hair style, hair colour and shirt is drawn, standing and celebrating, with
the navy outline. The look buttons show the head alone. A look is drawn once per size and reused.

- `tests/test_art.py::test_S2_AC2_every_look_is_drawn_with_the_navy_outline`
- `tests/test_art.py::test_S2_AC2_the_head_alone_is_drawn_for_the_look_buttons`
- `tests/test_art.py::test_S2_AC2_a_look_is_drawn_once_and_then_reused`

### S2_AC3: Vowels in red, consonants in blue

A turned card shows its letter in red if the content marks it as a vowel (`"vowel": true` in
`letters.json`), in blue otherwise. In English the vowels are A, E, I, O and U.

- `tests/test_art.py::test_S2_AC3_vowels_are_red_and_consonants_blue_as_the_content_says`
- `tests/test_art.py::test_S2_AC3_a_turned_card_shows_its_letter_in_its_colour`

### S2_AC4: Main actions are the green pill

"Next", "Done" and "Next level" are glossy green pills; the other buttons are white. Every button
a child taps is still at least 96 pixels on its smallest side.

- `tests/test_art.py::test_S2_AC4_main_actions_are_the_green_pill`
- `tests/test_art.py::test_S2_AC4_next_done_and_next_level_are_main_actions_and_every_target_is_big`

### S2_AC5: Fredoka for titles, Andika for letters

Titles, buttons and numbers use Fredoka SemiBold; letters and names use Andika. If a font file is
missing, pygame's own font is used and nothing crashes.

- `tests/test_art.py::test_S2_AC5_titles_use_fredoka_and_letters_use_andika`
- `tests/test_art.py::test_S2_AC5_a_missing_font_falls_back_to_pygames_own`

### S2_AC6: Drawing stays fast

With the largest level (16 cards), 60 frames draw in under a second headless, because what is drawn
is cached.

- `tests/test_art.py::test_S2_AC6_sixty_frames_of_the_memory_game_draw_in_under_a_second`
