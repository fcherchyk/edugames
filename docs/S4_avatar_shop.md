# Slice 4: the avatar shop

## What slice 4 delivers

Coins finally have something worth saving for. The wardrobe becomes a **shop**: on top of its
shirt, the avatar can wear a hat, glasses, wings (or a cape, or a jetpack) and shoes, and be
followed by a pet, all bought with the coins won in the games. The look itself (face, freckles,
skin, hair, eyes) can be changed at any time, for free.

- **The shop:** a "Shop" button on the home (a crown and the word) opens it. Seven round tabs,
  shown as pictures: me, hats, glasses, wings, shoes, pets, shirts. The big avatar stands on the
  left, wearing what is being tried on.
- **44 new items** in five new slots, each drawn in code in the art style: 8 hats, 6 glasses,
  5 wings and capes, 7 pairs of shoes and 18 pets. The 8 shirt colours of slice 1 become the
  shirts tab.
- **Pets come in kinds:** cats, dogs, birds, monsters and robots. The pets tab shows a row of
  kinds (a picture and its word, no price), then the 3 or 4 pets of the open kind, each with its
  price.
- **Try before you buy:** a tap on an item puts it on the avatar for free. A green "Buy" pill
  with its price buys it. Nothing is spent by accident, and trying things on is half the fun.
- **Saving up:** while the coins are not enough, the Buy pill is grey and fills with gold as the
  coins grow ("7 / 30"), and the price tags of items out of reach are grey.
- **Worlds open items:** some items wait for the player to reach a world of the path (the woolly
  hat and the penguin for the snow, the space helmet and the drone for space). Until then they
  show as a grey shape with a padlock and the world's icon, the same icon as on the path's
  stones.
- **"New in the shop!":** the victory pop-up of a win that opens a world shows what just arrived.
- **The "Me" tab:** face, skin, hair, hair colour, eyes and freckles, free to change, one at a
  time, in a mirror. Each choice has a picture and its word. The same choices, with the new eye
  colour and freckles, are offered step by step when a player is created.
- **Everywhere:** the outfit and the pet are on every screen: players, home, the paths and the
  victory pop-up.

Two rules change with the shop, to keep it fair and simple:

- **A replay gives 2 coins.** The first win of a level gives 2 coins plus 1 per star (3 to 5), as
  before. A win on a level already won gives 2, so the quickest way to the crown is new levels,
  not the easiest one again.
- **Ages 3 to 7.** Age 8 is no longer offered when a player is created, since no game is playable
  at 8. A player saved as 8 loads as 7 and can play.

## How it plays

1. On the home, the child taps **Shop** (a crown). The shop opens on the hats tab. The coins show
   at the top right, as everywhere.
2. **Tabs** are light blue circles with a picture: the player's own head ("me"), a cap, glasses,
   wings, sneakers, a kitten, a shirt. The open tab is orange.
3. **Tiles** show each item of the tab, in two rows of four:
   - **Owned:** a white tile, with no price.
   - **Not owned yet:** a white tile with its price tag under it (white if the coins are enough,
     grey if not).
   - **Closed:** its world is not won yet. A grey tile with the item's grey shape, a padlock, and
     the world's icon. A tap does nothing.
   - A **gold ring** marks what the avatar shows, and only that.
4. A tap on an item **not owned** tries it on: the big avatar wears it and the Buy pill appears
   under it. A tap on the same item, on another tab, or on **Home** takes it off again. Nothing
   was spent or saved.
5. **Buy**, with enough coins: the coins are spent, the item is the player's and is worn, the game
   saves, and the avatar cheers for a moment among gold sparkles. Without enough coins, the pill
   is grey, shows "coins / price" and is gold up to where the coins reach. A tap does nothing.
6. In the **pets** tab, under the tabs, a row of five chips shows the kinds of pets, each a
   picture and its word: a kitten ("Cat"), a puppy ("Dog"), a parrot ("Bird"), a fuzzy monster
   ("Monster"), a robot ("Robot"). A kind has no price: it only opens. The open one is orange;
   the tab opens on the kind of the pet being worn, or on cats. Under the kind's word, its 3 or
   4 pets show in one row as tiles like any other item (price tag, padlock for a world not won,
   gold ring on the avatar's). Opening another kind ends a try.
7. A tap on an item **owned** wears it at once. A tap on the item being worn takes it off: no hat,
   no glasses, no wings, no pet, or the avatar's own red shoes again. The shirt always stays on.
   One item per slot, and the slots combine: a crown, heart glasses, dragon wings, roller skates
   and a penguin together.
8. In the **Me** tab, the avatar on the left becomes a **mirror**: a round hand mirror showing the
   player's head and shoulders, large. Under the tabs, a row of six **chips** says what can be
   changed, each a picture with its word under it: a smiley ("Face"), a round of skin tones
   ("Skin"), a comb ("Hair"), drops of paint ("Hair colour"), an eye ("Eyes"), a cheek with
   freckles ("Freckles"). The open chip is orange (Face when the tab opens). Under its title
   ("Eyes"), only its choices show, as big tiles that show only what changes: a close-up of each
   face, the head with each skin, hair or hair colour, a big eye of each colour, the face without
   and with freckles. A tap changes the look at once, for free, and saves. The mirror sparkles
   where it changed (the eyes, the hair, the cheeks). Items stay on, but the mirror takes off the
   ones that hide what is being chosen: the hat while choosing hair; the glasses, goggles or mask
   while choosing the face, eyes or freckles; the space helmet always. They are back on the avatar
   when the tab is left.
9. When a player is **created**, the look step is the same chips, choices and mirror, taken in
   order: face, skin, hair, hair colour, eyes, freckles. The green button says "Next" until the
   last, then "Done". The chips jump to any step, and "Back" goes to the step before, then to the
   age.

## The items

Every item is a drawing in code (`ui/items_draw.py`), with no text and no image files, so it works
in every language and needs no new entry in `CREDITS.md`. The catalogue (slot, price, world) is in
`core/avatar.py`, next to the shirt colours. Prices are game design, the same in every locale, and
each item needs its drawing in code anyway.

| Slot | Item | Price | Opens with |
|---|---|---|---|
| head | cap | free | start |
| head | party hat | 5 | start |
| head | bunny ears | 10 | start |
| head | flower crown | 10 | meadow |
| head | woolly hat | 10 | snow |
| head | wizard hat | 20 | forest |
| head | space helmet | 25 | space |
| head | crown | 30 | start |
| eyes | round glasses | free | start |
| eyes | sunglasses | 5 | beach |
| eyes | heart glasses | 10 | start |
| eyes | star glasses | 10 | start |
| eyes | ski goggles | 10 | snow |
| eyes | hero mask | 15 | start |
| back | cape | 10 | start |
| back | butterfly wings | 15 | meadow |
| back | bird wings | 20 | beach |
| back | dragon wings | 25 | forest |
| back | jetpack | 30 | space |
| feet | sneakers | free | start |
| feet | bunny slippers | 10 | start |
| feet | rain boots | 10 | forest |
| feet | flippers | 10 | beach |
| feet | snow boots | 15 | snow |
| feet | roller skates | 20 | start |
| feet | rocket boots | 25 | space |
| pet: cat | kitten | 10 | start |
| pet: cat | ginger cat | 15 | start |
| pet: cat | black cat | 15 | start |
| pet: cat | lion cub | 25 | start |
| pet: dog | puppy | 10 | start |
| pet: dog | dalmatian | 15 | start |
| pet: dog | poodle | 20 | start |
| pet: dog | husky | 20 | start |
| pet: bird | chick | 10 | meadow |
| pet: bird | parrot | 20 | beach |
| pet: bird | owl | 20 | start |
| pet: bird | penguin | 20 | snow |
| pet: monster | fuzzy monster | 15 | start |
| pet: monster | one-eyed monster | 20 | start |
| pet: monster | baby dragon | 30 | forest |
| pet: robot | robot | 20 | start |
| pet: robot | robo-dog | 25 | start |
| pet: robot | drone | 30 | space |
| shirt | red, blue | free | start |
| shirt | green, yellow, purple, orange, pink, teal | 5 | start |

**Kinds of assets.** These are things children of 4 to 6 know from play and dressing up
(royalty, magic, animals, heroes, space, weather). Nothing is a weapon. Every item is open to
every player, whatever their age or look, and no item or colour is presented as being for a girl
or a boy. Pets sit and face the child, as friendly as the pictures of slice 3: cats and dogs
(sharing one sitting body, with their own ears, coats and faces), birds, monsters that smile
(fuzzy, one-eyed, a baby dragon) and robots (one hovers over its shadow). Within a kind, the
first pet is the cheapest (10 or 15) and the last the dream (25 or 30).

**Layers.** `back` items are drawn behind the body. `feet` items are drawn over the legs, instead
of the avatar's own red shoes. `head` items go over the hair, and `eyes` items over the eyes (the
hero mask goes under them, so the eyes show through its holes). The `pet` sits on the ground at
the avatar's right, in front of everything. The body keeps its size and place on every screen;
items may reach outside its box (wings to the sides, a wizard hat above, rocket flames below, the
pet to the right).

## The look

| Choice | Options |
|---|---|
| face | smile, grin, calm, wink |
| freckles | without, with (dots on both cheeks, a darker shade of the skin, visible on every tone) |
| skin | light, peach, tan, brown, deep |
| hair | short, long, curly, bun, spiky |
| hair colour | black, brown, blond, red, blue |
| eye colour | brown, blue, green, hazel, grey (the colour of the iris) |

These choices are the same when a player is created and in the Me tab
(`ui/look_picker.py`), and always free. They are shown one at a time, so that each screen asks
one question ("Hair colour?") with two to five big answers.

## The economy

The first win of a level gives 2 coins plus 1 per star (3 to 5); a replay gives 2. A level takes
about one to three minutes.

| Price | Means | In first wins | In replays |
|---|---|---|---|
| free | something to put on at once, to learn how the shop works | 0 | 0 |
| 5 | the first purchase, right after the first win or two | 1 to 2 | 3 |
| 10 to 15 | a normal wish: a first pet, boots, glasses | 2 to 5 | 5 to 8 |
| 20 to 30 | a dream, saved for over a few sessions | 4 to 10 | 10 to 15 |

- **Small round numbers.** Prices are multiples of 5 and at most 30, numbers a child of 4 to 6
  can read or count to (by fives). The gold bar in the Buy pill shows "how far" without
  arithmetic.
- **Totals.** The 44 items cost 690 coins (the 18 pets alone 340), and the shirts 30 more.
  Winning every level once (15 levels for ages 4 to 7; 5 for a three-year-old, who plays Letter
  Pairs only) gives 45 to 75 coins: a first pet, a pair of boots and a hat. The shop is a
  collection to choose from, not to complete: a child picks a favourite pet or two, not all 18.
  Buying everything would take about 330 replays at 2 coins. Every new game or level in later
  slices brings new first wins, and so more coins.
- **Replays.** A replay gives 2 coins whatever its stars, so no level pays better than new
  progress. Replays are still worth something, which keeps practice rewarding.
- **Worlds.** The meadow opens three items and the other worlds four each, always with an animal.
  So reaching a new world is rewarded with something new to see, not only with coins. The
  meadow's open at the very first win, which teaches the child that winning opens things.

## When items open

An item with a world opens when the player wins **any** level of that world, in **any** game (the
theme of the level, `theme` in `<game>_levels.json`). It stays open. Both games have the five
worlds, so a three-year-old who only plays Letter Pairs reaches them all. Items with no world are
open from the start: price is their only gate. A closed item cannot be bought, in the core as
well as on the screen.

| World | Opens |
|---|---|
| meadow | flower crown, butterfly wings, chick |
| beach | sunglasses, bird wings, flippers, parrot |
| forest | wizard hat, dragon wings, rain boots, baby dragon |
| snow | woolly hat, ski goggles, snow boots, penguin |
| space | space helmet, jetpack, rocket boots, drone |

## Saved data

Each profile in `profiles.json` gains `owned_items`. Its avatar gains `head`, `eyes`, `back`,
`feet` and `pet` (`""` is nothing), plus `eye_color` and `freckles`. The schema version does not
change:

```json
"avatar": {"face": "grin", "shirt": "green", "head": "crown", "eyes": "", "back": "cape",
           "feet": "", "pet": "kitten", "eye_color": "green", "freckles": true},
"owned_items": ["crown", "cape", "kitten"]
```

Profiles saved before this slice load with nothing on, brown eyes and no freckles. An unknown
item (one removed from the shop) is dropped from `owned_items`. A worn item that is unknown, in
the wrong slot or not owned is taken off. An unknown eye colour or freckles value gets the
default. A player saved as 8 loads as 7. In every case the profile still loads.

## Code

- `core/avatar.py`: `Item` (id, slot, price, world, and for pets their kind), `ITEMS`, `SLOTS`,
  `items_for(slot)` (shirts included), `PET_KINDS`, `pets_of(kind)`, `EYE_COLORS`, `FRECKLES`, and the avatar's `head`, `eyes`, `back`, `feet`, `pet`,
  `eye_color` and `freckles`. `Avatar.wearing(item)` is a copy for trying on; `Avatar.bare()`
  is a copy with no items (for the heads of the Me tab).
- `core/profiles.py`: `owns`, `can_buy`, `buy`, `wear` and `take_off` for any item; the shirt
  methods of slice 1 use them. `load_owned_items`, `load_avatar` and `load_age` handle old and
  damaged saved data. `MAX_AGE` is 7.
- `core/progress.py`: `coins_for(stars, replay)`: a replay gives `BASE_COINS`.
- `core/shop.py` (no pygame): `worlds_won`, `is_open`, `open_items`, `newly_opened` and `buy`,
  which refuses a closed item.
- `ui/items_draw.py`: the 44 drawings with `ItemPen` (outlined shapes, cel shades, see-through
  lenses and glass); pets are drawn around their own ground point (`PET_X`), cats and dogs on
  one sitting body (`_sitter`). Also `item_icon`
  for tiles (and grey shapes for closed items) and `draw_shirt`.
- `ui/avatar_draw.py`: draws the layers, the eye colour and the freckles. The sprite covers
  `ITEMS_FRAME` while the body keeps its size and place.
- `ui/look_picker.py`: `LookPicker`, shared by the profile creation and the Me tab. It holds the
  chips (`look:<choice>`, with their pictures and words), the open chip's choices, the mirror
  (`mirror_look` takes off the items that hide the open choice; `mirror` draws it, cached) and
  the sparkles after a change.
- `ui/avatar_draw.py`: `draw_bust`, the head and shoulders with their items, for the mirror.
- `ui/scenes/shop.py`: `ShopScene` (replaces `wardrobe.py`), with the Me tab and the pets tab's
  kinds (`kind:<kind>` chips).
- `ui/widgets.py`: `draw_chip` (a picture and its word, fitted by `fitting_size`), shared by the
  Me tab's chips and the pets' kinds.
- `ui/scenes/level.py`: the victory pop-up lists `new_items` (`new_item_tiles`).
- `ui/scenes/home.py`, `profiles.py` and `path.py`: room for tall hats, boots and pets (see
  "Changes to earlier slices").
- `demo.py`: tries on and buys in the shop, changes the look in the Me tab, tries on a pet, and
  shows a dressed avatar at home. `choose_look` and `finish_look` go through the look's steps.

## Changes to earlier slices

- **S1_AC2:** ages are 3 to 7 (the test is renamed `test_S1_AC2_ages_3_to_7_are_accepted`, and 8
  is refused).
- **S1_AC12 and S3_AC13:** a replay gives 2 coins, whatever its stars.
- **S1_AC2 and S1_AC14:** the look step offers one choice at a time (face, skin, hair, hair
  colour, eyes, freckles), with "Next" and then "Done". It shows a mirror instead of the whole
  avatar, and "Back" goes back through its steps before the age. The tests choose the look
  through the chips.
- **S2_AC4:** the look's "Next" is a main action (the green pill), like "Done".
- **S1_AC15:** the wardrobe is now the shop's shirt tab, so a colour is tried on and then bought
  with the Buy pill instead of being bought by the first tap. Prices do not change. The test
  keeps its name and follows the new flow.
- **S1_AC1:** the demo's ninth screen is `shop` instead of `wardrobe`.
- **S2_AC2:** every look is still drawn and cached. The cache key now includes the items, the eye
  colour and the freckles, and the sprite has room around the body.
- **Layouts:** the home's avatar is a little smaller (330 px, the name tag above it, the Shop
  button 10 px lower). The players' tiles draw it at 166 px and the victory pop-up at 340 px. The
  goal path draws its title after the avatar, so a hat goes behind the title instead of over its
  letters.
- Strings: `shop`, `buy`, `new_in_shop`, `eye_color`, `freckles` and `pet_cat`, `pet_dog`,
  `pet_bird`, `pet_monster`, `pet_robot` are new; `face`, `skin`,
  `hair` and `hair_color` are now used (the chips' words); `wardrobe` is gone.

## Not in slice 4

- Refunds or selling back: decided against. Buying is a real choice, and trying on first makes
  it an informed one.
- Spoken item names and sounds when buying: decided against for now.
- Animated items (flapping wings, a pet that wags its tail or hops when the avatar cheers).
- A badge on the Shop button when something new or affordable is waiting (see open points).

## Decisions

Taken with the owner:

- **Try before you buy, with an explicit Buy.** A child of 4 taps everything. With one-tap buying
  (the old wardrobe), a tap on the wrong tile spends the coins saved for the crown. Trying on is
  free and unlimited.
- **No refunds**, and **no spoken item names**.
- **A replay gives 2 coins**, whatever its stars, so that replaying an easy level is not the
  quickest way to the crown.
- **Age 8 is no longer offered**; players saved as 8 become 7 rather than being lost.
- **A "Me" tab** to change the look for free after creation. **Eye colour and freckles** join the
  look, at creation and in the Me tab.
- **The look, one thing at a time** (found confusing as five rows of 27 round heads, with no
  word saying what a row changes). Chips with a picture and a word say what can be changed; the
  choices show only what changes; a mirror shows the head large, without the items that would
  hide the change, and sparkles where it changed. A new player goes through the same steps in
  order, with "Next".
- **Shoes and pets** join the shop. Shoes replace the avatar's own (taking them off brings the red
  ones back). The pet sits beside the avatar on every screen.
- **Pets by kind:** cats, dogs, birds, monsters, robots, with 3 or 4 pets each, shown one kind at
  a time behind a row of kinds that have no price. The bunny and the turtle, which fit no kind,
  left the shop; the chick and the parrot now open with the meadow and the beach.
- **A gold ring only means "on the avatar".** Tabs use colour (orange when open), not a ring.
- **Items open by world, not by a star count.** The world's icon is already on the path's stones,
  so a closed item explains itself without text. A star count is a number the youngest cannot
  relate to.
- **Closed items are visible as shapes**, to give something to look forward to, not hidden.
- **Nothing random, nothing limited in time, no pressure.** No mystery boxes, no daily deals, no
  streaks, no "only 2 left". The shop never interrupts a game; the only place it is mentioned
  outside the home is the victory pop-up, and only when a world opens. This is now written in
  `docs/standards.md`.
- **The catalogue is code, not per-locale content.** Items have no words, and their prices do not
  change with the language.
- **Free starter items** (a cap, round glasses and sneakers) so that the shop makes sense on the
  first visit, before any coins.

## Open points for the owner

1. **The pace after the first pass.** With replays at 2 coins, a 20-coin pet takes 10 replays.
   If children stall, there are two small changes: a replay that improves the level's best stars
   could also give its star coins, or the dearer pets could come down (for example, to 20 at
   most).
2. **A badge on the Shop button** when an item becomes affordable. It would bring children back to
   the shop, which is also why it was left out.

## Acceptance criteria

Each criterion lists its tests. `tests/test_project.py` (S1_AC18) checks that this list and the
tests agree.

### S4_AC1: The shop replaces the wardrobe

The home has a "Shop" button, drawn with a crown and the word, at least 96 pixels. It opens the
shop on the hats tab, and "Home" goes back. Seven tabs: me, then hats, glasses, wings, shoes, pets
and shirts, which show the items of their slot, at most eight each (the pets one kind at a time,
S4_AC20). The open tab is orange, and no
tab has the gold ring. Tabs and tiles are at least 96 pixels, on the screen, and do not overlap.

- `tests/test_shop_ui.py::test_S4_AC1_home_opens_the_shop_and_home_goes_back`
- `tests/test_shop_ui.py::test_S4_AC1_the_tabs_show_the_items_of_their_slot`
- `tests/test_shop_ui.py::test_S4_AC1_every_tile_is_big_and_fits_on_screen`

### S4_AC2: The catalogue

There are 8 hats, 6 glasses, 5 wings or capes, 7 pairs of shoes, 18 pets and the 8 shirts, with
ids unique across slots. Prices are multiples of 5 from 0 to 30. The cap, the round glasses and
the sneakers are free, and the crown costs 30. Each of the five worlds (meadow, beach, forest,
snow, space), all reachable in the content, opens three or four items that cost coins, one of
them a pet; the other items are open from the start.

- `tests/test_shop.py::test_S4_AC2_the_catalogue_has_hats_glasses_and_wings`
- `tests/test_shop.py::test_S4_AC2_prices_are_small_round_numbers`
- `tests/test_shop.py::test_S4_AC2_each_world_of_the_path_opens_three_or_four_items`

### S4_AC3: Every item is drawn in the art style

Every item is drawn in shapes with the navy outline on the avatar, standing and cheering, with
any hair style. It is also drawn alone for its tile, fitting the tile, and as a flat grey shape
when closed. The body keeps the size and place it had before this slice; items may reach outside
it. An item with no drawing draws nothing and does not crash. Avatars and icons are drawn once
per size and reused.

- `tests/test_shop_ui.py::test_S4_AC3_every_item_changes_the_avatar_with_the_navy_outline`
- `tests/test_shop_ui.py::test_S4_AC3_every_item_has_an_icon_for_its_tile`
- `tests/test_shop_ui.py::test_S4_AC3_the_body_keeps_its_size_and_place`
- `tests/test_shop_ui.py::test_S4_AC3_an_item_without_a_drawing_draws_nothing`
- `tests/test_shop_ui.py::test_S4_AC3_an_item_is_drawn_once_and_then_reused`

### S4_AC4: World items open with a win in their world

An item with a world is closed until the player wins a level of that world, in any game, and then
stays open. A closed item cannot be bought, even by the core. On the screen it is a grey shape
with a padlock and the world's icon, and a tap on it does nothing.

- `tests/test_shop.py::test_S4_AC4_a_world_item_opens_with_a_win_in_its_world_in_any_game`
- `tests/test_shop.py::test_S4_AC4_a_closed_item_cannot_be_bought`
- `tests/test_shop_ui.py::test_S4_AC4_a_closed_item_is_a_grey_shape_with_a_padlock_and_does_nothing`

### S4_AC5: Try on before buying

A tap on an open item not owned puts it on the big avatar with the gold ring on its tile and
shows the Buy pill. Nothing is spent or saved. A tap on the same item, on another tab, or on
"Home" ends the try.

- `tests/test_shop_ui.py::test_S4_AC5_an_item_is_tried_on_for_free`
- `tests/test_shop_ui.py::test_S4_AC5_tapping_again_changing_tab_or_leaving_ends_the_try`

### S4_AC6: Buying

With enough coins, Buy (the green pill) spends the price, and the item is owned, worn and saved.
The avatar cheers for 1.5 seconds. Without enough coins the pill is grey, does nothing, and is
gold up to the share of the price the coins reach. Price tags are white when the coins are
enough and grey when not. An item already owned, free or bought, is never bought again.

- `tests/test_shop.py::test_S4_AC6_an_item_is_bought_with_enough_coins_and_worn`
- `tests/test_shop.py::test_S4_AC6_an_item_is_refused_without_enough_coins_or_when_owned`
- `tests/test_shop_ui.py::test_S4_AC6_buy_spends_the_coins_saves_and_the_avatar_cheers`
- `tests/test_shop_ui.py::test_S4_AC6_without_enough_coins_buy_shows_how_far_the_coins_are`

### S4_AC7: Wearing and taking off

One item per slot; the slots combine. Only owned items can be worn. A tap on an owned item wears
it and saves. A tap on the item being worn takes it off; the shirt cannot be taken off. Shoes
from the shop replace the avatar's own red shoes. A pet sits on the ground at the avatar's right.
The outfit shows wherever the avatar does: players, home, paths and the victory pop-up.

- `tests/test_shop.py::test_S4_AC7_one_item_per_slot_and_only_owned_items_are_worn`
- `tests/test_shop.py::test_S4_AC7_hats_glasses_and_wings_come_off_but_a_shirt_does_not`
- `tests/test_shop_ui.py::test_S4_AC7_tapping_an_owned_item_wears_it_and_again_takes_it_off`
- `tests/test_shop_ui.py::test_S4_AC7_the_outfit_shows_wherever_the_avatar_does`
- `tests/test_shop_ui.py::test_S4_AC7_shoes_replace_the_avatars_own_and_a_pet_sits_beside_it`

### S4_AC8: Items and outfits are saved, and old profiles load

Owned items and the outfit survive a restart. Profiles saved before this slice load with nothing
on. Unknown or repeated ids in `owned_items` are dropped, and a damaged `owned_items` is
ignored. A worn item that is unknown, in the wrong slot or not owned is taken off, and the
profile still loads. A new look with an item in the wrong slot is refused.

- `tests/test_shop.py::test_S4_AC8_items_and_the_outfit_survive_a_restart`
- `tests/test_shop.py::test_S4_AC8_old_profiles_load_and_damaged_items_are_dropped`
- `tests/test_shop.py::test_S4_AC8_a_new_look_refuses_an_item_in_the_wrong_slot`

### S4_AC9: The victory pop-up shows what a win opened

A win that opens a world shows "New in the shop!" and the items it opened, inside the pop-up and
clear of its buttons; they are open in the shop. A win that opens nothing shows nothing new.

- `tests/test_shop.py::test_S4_AC9_newly_opened_lists_what_a_win_opened`
- `tests/test_shop_ui.py::test_S4_AC9_a_win_that_opens_a_world_shows_its_new_items`
- `tests/test_shop_ui.py::test_S4_AC9_a_win_that_opens_nothing_shows_no_new_items`

### S4_AC10: Tall hats, wide wings, boots and pets fit on every screen

Take the tallest hat, wide wings, rocket boots and the pet reaching furthest. With them, the
avatar stays inside its player tile and does not cover the home's name tag or buttons. In the
victory pop-up it leaves the new items and the buttons clear. On the goal path, the title is
drawn over the avatar, so a hat never covers the title's letters.

- `tests/test_shop_ui.py::test_S4_AC10_a_dressed_avatar_stays_inside_its_player_tile`
- `tests/test_shop_ui.py::test_S4_AC10_on_home_a_tall_hat_leaves_the_name_and_the_shop_button_clear`
- `tests/test_shop_ui.py::test_S4_AC10_on_the_path_the_title_is_drawn_over_a_tall_hat`
- `tests/test_shop_ui.py::test_S4_AC10_in_the_victory_popup_the_avatar_leaves_the_new_items_clear`

### S4_AC11: Drawing stays fast

In the shop, with a fully dressed avatar trying on wings, 60 frames draw in under a second
headless; so do 60 frames of the Me tab with its mirror sparkling.

- `tests/test_shop_ui.py::test_S4_AC11_sixty_frames_of_the_shop_draw_in_under_a_second`

### S4_AC12: The sandbox demo visits the shop

`python -m edugames.demo <dir>` saves the shop with a hat tried on (where the wardrobe was). Then
it saves the shop saving up for the crown, the avatar cheering after buying wings, the Me tab
after choosing green eyes and freckles (the mirror sparkling, the star glasses off), the pets tab
with a kitten tried on, and the home with a dressed avatar. The look step shows the mirror
sparkling on the hair just chosen.

- `tests/test_project.py::test_S4_AC12_the_demo_visits_the_shop`

### S4_AC13: A replay gives 2 coins

The first win of a level gives 2 coins plus 1 per star; a win on a level already won gives 2,
whatever its stars, even when it improves the best stars (which are kept). Levels of different
games are different levels. The victory pop-up shows "+2 coins".

- `tests/test_progress.py::test_S4_AC13_a_replay_gives_2_coins_whatever_its_stars`
- `tests/test_shop_ui.py::test_S4_AC13_the_victory_popup_of_a_replay_shows_2_coins`

### S4_AC14: Players are 3 to 7

The age step offers 3 to 7, and 8 is refused. A player saved as 8 loads as 7; other ages out of
range are still a damaged profile, skipped.

- `tests/test_shop_ui.py::test_S4_AC14_the_age_step_offers_3_to_7`
- `tests/test_profiles.py::test_S4_AC14_a_player_saved_as_8_loads_as_7`

### S4_AC15: The "Me" tab changes the look for free, one thing at a time

The Me tab has six chips: face, skin, hair, hair colour, eyes, freckles. The face is open first,
and the open chip is orange. Only the open chip's choices show (4 faces, 5 skins, 5 hair styles,
5 hair colours, 5 eye colours, without and with freckles), with the player's current choice
ringed. Chips and choices are at least 96 pixels, on the screen and not overlapping. A tap on a
choice changes the look at once and saves it. No coins are spent, and the items worn stay on.

- `tests/test_shop_ui.py::test_S4_AC15_the_me_tab_changes_the_look_for_free_and_saves_it`
- `tests/test_shop_ui.py::test_S4_AC15_each_chip_shows_only_its_own_choices_big_and_on_screen`

### S4_AC16: Eye colour and freckles

Every eye colour is drawn as the colour of the iris, and freckles as dots on the cheeks, on the
face only. A new player chooses them in the look step, with the other options. Profiles saved
before this slice load with brown eyes and no freckles; an unknown eye colour or freckles value
gets the default. A new look with an unknown one is refused.

- `tests/test_shop_ui.py::test_S4_AC16_every_eye_colour_and_freckles_are_drawn`
- `tests/test_shop_ui.py::test_S4_AC16_a_new_player_chooses_eye_colour_and_freckles`
- `tests/test_profiles.py::test_S4_AC16_old_or_damaged_eye_colours_and_freckles_get_the_default`

### S4_AC17: The mirror shows what changes

In the Me tab and the look step, a mirror shows the head and shoulders instead of the whole
avatar; the other tabs show the whole avatar. The mirror takes off the items that hide the open
choice: the hat for hair and hair colour; glasses, goggles or a mask for the face, eyes and
freckles; the space helmet always. Wings, capes and pets stay, and the player keeps every item.
After a choice, the mirror sparkles where the look changed, for 0.9 seconds.

- `tests/test_shop_ui.py::test_S4_AC17_the_me_tab_shows_a_mirror_instead_of_the_whole_avatar`
- `tests/test_shop_ui.py::test_S4_AC17_the_mirror_takes_off_what_hides_the_part_being_chosen`
- `tests/test_shop_ui.py::test_S4_AC17_a_choice_sparkles_where_it_changes_the_mirror`

### S4_AC18: Words under the pictures

Each chip has its word under its picture, from the content (`face`, `skin`, `hair`,
`hair_color`, `eye_color`, `freckles`: "Face", "Skin", "Hair", "Hair colour", "Eyes",
"Freckles"). The font shrinks until the word fits in the chip. The open chip's word is also the
title over its choices.

- `tests/test_shop_ui.py::test_S4_AC18_every_chip_has_its_word_under_its_picture`

### S4_AC19: A new player chooses the look step by step

After the age, the look step opens on the face and goes through face, skin, hair, hair colour,
eyes and freckles with the green "Next", and "Done" on the last. The chips jump to any step.
"Back" goes to the step before, and from the first one to the age.

- `tests/test_shop_ui.py::test_S4_AC19_a_new_player_goes_through_the_look_with_next_and_done`

### S4_AC20: Pets come in kinds

Every pet has a kind: cat (4), dog (4), bird (4), monster (3) or robot (3). The pets tab shows a
chip per kind, each a picture and its word ("Cat", "Dog", "Bird", "Monster", "Robot"), with no
price, at least 96 pixels. The open kind is orange. The tab opens on the kind of the pet worn, or
on cats. Only the open kind's pets show, in one row centred under the kinds, each with its price
tag or padlock like any item. Opening another kind ends a try.

- `tests/test_shop.py::test_S4_AC20_every_pet_has_a_kind_with_three_or_four_pets`
- `tests/test_shop_ui.py::test_S4_AC20_the_pets_tab_has_a_chip_per_kind_without_a_price`
- `tests/test_shop_ui.py::test_S4_AC20_each_kind_shows_only_its_own_pets`
- `tests/test_shop_ui.py::test_S4_AC20_the_tab_opens_on_the_kind_of_the_pet_worn_and_a_new_kind_ends_a_try`
