# Slice 1 (MVP): players, the goal path and the Letter Pairs memory game

## What slice 1 delivers

A desktop app (Mac, Linux, Windows) for children aged 4 to 6 who are learning to read:

- **Players:** several profiles on the same computer, each with a first name, an age (3 to 8) and
  an avatar (face, skin tone, hair style and hair colour). The age decides which games are offered.
- **Home:** the player's avatar and coins, and the games for their age. Only **Letter Pairs** is
  playable; the others show locked as "coming soon".
- **Letter Pairs:** a memory game where `A` is matched with `a`. Turning a card over says the
  letter's name. There is no timer and no way to lose.
- **Goal path:** 5 levels, each opened by winning the one before, with 1 to 3 stars per level.
- **Coins and wardrobe:** every win gives coins, which buy shirt colours for the avatar.
- **Victory pop-up:** the avatar celebrating, the stars and the coins earned.

Everything is local: no network, no accounts, no data beyond a first name and an age.

## Not in slice 1

- Other games (Letter Sounds, First Letter, Draw Letters), more avatar items, sound effects.
- Spanish (planned as `content/es/` plus Spanish letter clips; the code is already per locale).
- Packaged executables (`.app`, `.exe`) and a web build (pygbag).
- A parents' area (progress per letter, deleting profiles).

## Acceptance criteria

Each criterion lists its tests. `tests/test_project.py` (S1_AC18) checks that this list and the
tests agree.

### S1_AC1: It runs from source on Mac, Linux and Windows

`uv run edugames` opens a 1280×800 window (scaled to the screen) and runs the main loop until the
window is closed. CI runs the tests on macOS, Ubuntu and Windows. With no display (a sandbox),
`python -m edugames.demo <dir>` plays a scripted game and saves a PNG of every screen.

- `tests/test_project.py::test_S1_AC1_the_game_has_a_command_and_supports_python_3_12`
- `tests/test_project.py::test_S1_AC1_ci_runs_the_tests_on_mac_linux_and_windows`
- `tests/test_project.py::test_S1_AC1_the_app_opens_a_window_and_runs_its_loop`
- `tests/test_project.py::test_S1_AC1_the_sandbox_demo_saves_a_picture_of_every_screen`
- `tests/test_ui.py::test_S1_AC1_closing_the_window_stops_the_loop`

### S1_AC2: A new player gives a name, an age and a look

Given the "New player" tile, the player types a name (1 to 12 letters, spaces, hyphens or
apostrophes; other characters are dropped), picks an age from 3 to 8 (3 to 7 since S4_AC14), and
chooses a look. Invalid
names, ages and avatar options are refused. "Back" goes one step back, and from the first step
cancels.

- `tests/test_profiles.py::test_S1_AC2_valid_names_are_accepted_and_trimmed`
- `tests/test_profiles.py::test_S1_AC2_invalid_names_are_refused`
- `tests/test_profiles.py::test_S1_AC2_ages_3_to_7_are_accepted`
- `tests/test_profiles.py::test_S1_AC2_other_ages_are_refused`
- `tests/test_profiles.py::test_S1_AC2_an_unknown_avatar_option_is_refused`
- `tests/test_ui.py::test_S1_AC2_a_new_player_types_a_name_picks_an_age_and_a_look`
- `tests/test_ui.py::test_S1_AC2_the_name_is_limited_and_enter_moves_on`
- `tests/test_ui.py::test_S1_AC2_back_goes_one_step_back_and_finally_cancels`

### S1_AC3: Several players, each with their own progress

"Who is playing?" shows up to 6 players. Choosing one opens their home with their own stars and
coins; "Players" goes back to the list. With 6 players there is no "New player" tile.

- `tests/test_profiles.py::test_S1_AC3_each_profile_keeps_its_own_coins_and_progress`
- `tests/test_profiles.py::test_S1_AC3_there_is_a_limit_of_profiles`
- `tests/test_profiles.py::test_S1_AC3_an_unknown_profile_id_is_an_error`
- `tests/test_ui.py::test_S1_AC3_choosing_a_player_opens_their_home_and_players_goes_back`
- `tests/test_ui.py::test_S1_AC3_no_new_player_tile_when_the_profiles_are_full`

### S1_AC4: Profiles are saved on this computer, safely

Profiles live in `profiles.json` in the user data folder (`platformdirs`, app name `EduGames`).
Writes go to a temporary file that replaces the old one, so a failed write keeps the previous
file. An unreadable file is renamed to `profiles.json.corrupt` and the app starts with no
players; a damaged profile is skipped and the others load.

- `tests/test_profiles.py::test_S1_AC4_profiles_survive_a_restart`
- `tests/test_profiles.py::test_S1_AC4_the_default_data_dir_is_the_users_data_folder`
- `tests/test_profiles.py::test_S1_AC4_saving_replaces_the_file_atomically`
- `tests/test_profiles.py::test_S1_AC4_a_failed_write_keeps_the_previous_file`
- `tests/test_profiles.py::test_S1_AC4_a_corrupt_file_is_set_aside_instead_of_crashing`
- `tests/test_profiles.py::test_S1_AC4_a_damaged_profile_is_skipped_and_the_others_load`

### S1_AC5: The games offered depend on the player's age

Each game in `games.json` has an age range. Home shows the games for the player's age, playable
ones first; the others are locked with "Coming soon" and do nothing when tapped.

- `tests/test_content.py::test_S1_AC5_games_are_filtered_by_age`
- `tests/test_content.py::test_S1_AC5_playable_games_come_before_the_coming_soon_ones`
- `tests/test_ui.py::test_S1_AC5_home_shows_the_games_for_the_age_and_locks_coming_soon`

### S1_AC6: Letter Pairs deals each letter in upper and lower case

A level with N pairs deals 2×N shuffled cards: each letter once in upper case and once in lower
case. A level whose letters are `"*"` uses N random letters of the alphabet.

- `tests/test_memory_game.py::test_S1_AC6_each_letter_is_dealt_once_in_upper_and_once_in_lower_case`
- `tests/test_memory_game.py::test_S1_AC6_the_cards_are_shuffled`
- `tests/test_memory_game.py::test_S1_AC6_a_level_without_letters_gets_random_ones`

### S1_AC7: Turning cards

Two cards are turned at a time. A matching pair stays up (green). Two different cards stay up for
1 second and turn back; meanwhile no other card turns. Cards are at least 96 px and fit on screen.

- `tests/test_memory_game.py::test_S1_AC7_a_matching_pair_stays_face_up`
- `tests/test_memory_game.py::test_S1_AC7_a_mismatch_waits_and_then_turns_back`
- `tests/test_memory_game.py::test_S1_AC7_no_card_turns_while_two_wait_to_turn_back`
- `tests/test_memory_game.py::test_S1_AC7_cards_outside_the_board_are_ignored`
- `tests/test_memory_game.py::test_S1_AC7_a_face_up_or_matched_card_cannot_be_flipped_again`
- `tests/test_ui.py::test_S1_AC7_two_different_cards_turn_back_after_a_second`
- `tests/test_ui.py::test_S1_AC7_cards_are_big_and_fit_on_screen`

### S1_AC8: Turning a card says its letter

Turning a card over plays the letter's name. With no sound device, or a missing clip, the game is
silent and keeps working.

- `tests/test_ui.py::test_S1_AC8_turning_a_card_says_its_letter`
- `tests/test_ui.py::test_S1_AC8_the_letter_clips_play_on_a_sound_device`
- `tests/test_ui.py::test_S1_AC8_with_no_sound_device_the_game_stays_silent`
- `tests/test_ui.py::test_S1_AC8_a_missing_clip_is_silent`

### S1_AC9: No timer and no losing

The game ends only when every pair is matched, however many mistakes there were.

- `tests/test_memory_game.py::test_S1_AC9_the_game_ends_only_when_every_pair_is_matched`
- `tests/test_ui.py::test_S1_AC9_mistakes_never_end_the_game`

### S1_AC10: Stars

A win gives 3 stars with at most one mismatch per pair, 2 with at most two, otherwise 1 (never 0).
The goal path keeps each level's best result.

- `tests/test_progress.py::test_S1_AC10_stars_come_from_the_mismatches`
- `tests/test_progress.py::test_S1_AC10_the_best_stars_are_kept`
- `tests/test_progress.py::test_S1_AC10_a_win_gives_1_to_3_stars`
- `tests/test_ui.py::test_S1_AC10_S1_AC11_S1_AC12_a_win_saves_stars_coins_and_opens_the_next_level`

### S1_AC11: The goal path

The first level is open; each other level opens when the one before is won. The avatar stands on
the first open level not won yet (or the last one).

- `tests/test_progress.py::test_S1_AC11_only_the_first_level_starts_open`
- `tests/test_progress.py::test_S1_AC11_winning_a_level_opens_the_next_one`
- `tests/test_ui.py::test_S1_AC10_S1_AC11_S1_AC12_a_win_saves_stars_coins_and_opens_the_next_level`
- `tests/test_ui.py::test_S1_AC11_the_avatar_waits_on_the_last_level_once_all_are_won`

### S1_AC12: Coins

Every win, replays included, gives 2 coins plus 1 per star, saved at once. (Since S4_AC13 a replay
gives the 2 coins only.)

- `tests/test_progress.py::test_S1_AC12_every_win_gives_coins_replays_included`
- `tests/test_ui.py::test_S1_AC10_S1_AC11_S1_AC12_a_win_saves_stars_coins_and_opens_the_next_level`

### S1_AC13: Victory pop-up

When every pair is matched, a pop-up shows the avatar with its arms up, the stars and
"+N coins", with "Next level" (except on the last level) and "Path".

- `tests/test_ui.py::test_S1_AC13_the_victory_popup_shows_stars_coins_and_next_level`
- `tests/test_ui.py::test_S1_AC13_the_last_level_has_no_next_level_button`

### S1_AC14: The avatar

The look step offers every face (4), skin tone (5), hair style (5) and hair colour (5), each shown
as it would look. The avatar is drawn with shapes, so colours change without image files.

- `tests/test_ui.py::test_S1_AC14_every_avatar_option_is_drawn`
- `tests/test_ui.py::test_S1_AC14_the_look_step_offers_every_option`

### S1_AC15: Wardrobe

Of 8 shirt colours, 2 are free and the others cost 5 coins (since S4, the shop's shirt tab, where a
colour is tried on before it is bought). A colour is bought with enough coins
(refused otherwise) and worn; owned colours can be worn again at any time.

- `tests/test_progress.py::test_S1_AC15_free_shirts_are_owned_from_the_start`
- `tests/test_progress.py::test_S1_AC15_a_shirt_is_bought_with_enough_coins_and_worn`
- `tests/test_progress.py::test_S1_AC15_a_shirt_is_refused_without_enough_coins`
- `tests/test_progress.py::test_S1_AC15_owned_shirts_are_not_bought_twice_and_unowned_ones_cannot_be_worn`
- `tests/test_ui.py::test_S1_AC15_the_wardrobe_buys_and_wears_a_colour`

### S1_AC16: Content per locale

Letters, games, levels and UI strings come from `content/en/`, and letter clips from
`assets/audio/en/`. Loading refuses levels with unknown or repeated letters, more random pairs
than letters, letters without a clip, and malformed files.

- `tests/test_content.py::test_S1_AC16_english_content_loads`
- `tests/test_content.py::test_S1_AC16_every_letter_has_its_audio_clip`
- `tests/test_content.py::test_S1_AC16_a_level_with_an_unknown_letter_is_refused`
- `tests/test_content.py::test_S1_AC16_a_level_with_wrong_pairs_is_refused`
- `tests/test_content.py::test_S1_AC16_a_letter_without_audio_is_refused`
- `tests/test_content.py::test_S1_AC16_malformed_or_missing_content_is_an_error`
- `tests/test_content.py::test_S1_AC16_an_unknown_level_is_an_error`

### S1_AC17: Asset licences

Every file in `src/edugames/assets/` is listed in `CREDITS.md` with a licence that allows
redistribution.

- `tests/test_project.py::test_S1_AC17_every_asset_is_credited_with_an_allowed_licence`

### S1_AC18: Quality gates

ruff passes, line coverage is at least 80%, every test is named after its criterion, and each
slice's document (this one, `S2_art_style.md`, …) lists exactly the tests that exist for it.

- `tests/test_project.py::test_S1_AC18_every_slice_has_a_doc`
- `tests/test_project.py::test_S1_AC18_every_acceptance_criterion_has_tests`
- `tests/test_project.py::test_S1_AC18_the_doc_lists_exactly_the_tests_that_exist`
- `tests/test_project.py::test_S1_AC18_every_test_names_its_criterion`
