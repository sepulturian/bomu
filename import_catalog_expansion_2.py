"""
Catalog expansion #2: rum, agave, vodka, brandy and low-ABV. Adds 46 recipes.

WHY THIS EXISTS
---------------
After the whiskey expansion the catalog sat at 125 recipes, but the weighting
was lopsided. Gin and whiskey were well served; rum had 13 entries and most of
them tiki, agave had 10, and the low-ABV / aperitif shelf was almost empty
despite everyone in the group owning vermouth and Campari.

The brief for this batch was explicitly "raise makeable counts", not "cover the
canon". So the selection rule was: prefer drinks whose non-optional
requirements are (a) ONE fungible spirit the group already owns and (b) mixers
already on the 48-item checklist. Drinks needing two or three name-matched
liqueurs were deliberately left out even when they are modern classics --
Naked and Famous, Division Bell, Nuclear Daiquiri, Brandy Crusta, Harvey
Wallbanger and Stinger were all cut for exactly this reason. They would have
padded the one-away list, which is already 49 deep for user 1, without giving
anyone a drink they can pour tonight.

BREAKDOWN
---------
  12  rum        Rum Old Fashioned, Ti' Punch, Queen's Park Swizzle, Airmail,
                 Canchanchara, Mary Pickford, Bacardi Cocktail, Hurricane,
                 Bee's Kiss, Fog Cutter, Jamaican Mule, Chet Baker
   9  agave      Ranch Water, Batanga, Siesta, Rosita, Tequila Sour,
                 Juan Collins, Cantarito, Tequila Old Fashioned, Vampiro
  10  vodka/gin  Dirty Martini, Gibson, Cape Codder, Bay Breeze, Chi-Chi,
                 Vodka Gimlet, Caesar, Sex on the Beach, Woo Woo,
                 Pornstar Martini
   7  brandy     Japanese Cocktail, Harvard, Brandy Sour, Brandy Daisy,
                 Nikolaschka, American Beauty, Brandy Cobbler
   8  low-ABV    Adonis, Bamboo, Milano-Torino, Cardinale, Old Pal,
                 Vermouth Cocktail, Bicicletta, Kalimotxo

NEW INGREDIENTS
---------------
Three, and only three. Every new checklist row starts UNTICKED for all five
existing users, so a new ingredient makes its recipes invisible until people go
back and update their mixers. That is the opposite of the goal here, so each
one had to earn its place:

  Passion Fruit Syrup   -> Hurricane, Pornstar Martini
  Clamato / Caesar mix  -> Caesar (Canada's national drink; the catalog has a
                           Bloody Mary but no Caesar, which is absurd for a
                           group of Canadians)
  White Wine            -> Bicicletta, and the obvious base for future spritzes

The other 43 recipes resolve entirely against the existing 48 ingredients.

PROVENANCE
----------
source='manual_verified', cocktaildb_id NULL, same as the whiskey batch. Specs
cross-checked against Difford's Guide, the IBA list, PUNCH, Imbibe and Death &
Co; the per-recipe `source_url` records which. Where published specs disagree
(Hurricane, Mary Pickford, Fog Cutter) the note on the ingredient row says so.

KNOWN DATA BUG, NOT FIXED HERE
------------------------------
The ingredient row "Grape Soda" is actually being used to mean GRAPEFRUIT soda
-- see the Paloma, whose row reads "Grapefruit soda (e.g. Jarritos, Squirt)".
Users ticking "Grape Soda" are almost certainly thinking of purple grape soda.
That needs a rename migration, not a recipe import, so nothing here depends on
it. Cantarito uses grapefruit juice + soda water instead.

SAFETY
------
  * Dry run by default. Nothing is written unless you pass --commit.
  * Idempotent. Recipes are matched on name and ingredients on name, so
    re-running is a no-op.
  * Single transaction. Any error rolls the whole thing back.
  * Refuses to run if a .db-journal / -wal / -shm file is sitting next to the
    database, which is the condition behind the 2026-07-23 corruption.

USAGE
-----
    python3 import_catalog_expansion_2.py              # dry run, prints plan
    python3 import_catalog_expansion_2.py --commit     # actually writes
"""

import argparse
import os
import sqlite3
import sys

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bomu.db")

# Same marker the rest of the catalog carries, so clean_instructions() strips it.
MARKER = "[BOMU_REWRITTEN_v1]"

VALID_REQ_TYPES = {"bottle_type", "ingredient", "optional"}

# Mirror of BOTTLE_TYPE_CHOICES in app.py.
VALID_BOTTLE_TYPES = {
    "gin", "vodka", "rum", "tequila", "mezcal", "whiskey", "bourbon", "scotch",
    "rye", "irish", "brandy", "cognac", "vermouth_sweet", "vermouth_dry",
    "vermouth", "amaro", "liqueur", "other",
}

# Mirror of NAME_MATCH_TYPES in matching.py. These resolve by substring against
# the bottle's name, so `notes` must carry a distinctive 4+ character keyword.
NAME_MATCH_TYPES = {"liqueur", "amaro", "other"}

# ---------------------------------------------------------------------------
# New checklist ingredients. (name, category)
#
# category drives the grouping headers on the checklist page. "mixer" puts all
# three in the Mixers block, which is where a user would look for them.
# ---------------------------------------------------------------------------

NEW_INGREDIENTS = [
    ("Passion Fruit Syrup", "mixer"),
    ("Clamato / Caesar mix", "mixer"),
    ("White Wine", "mixer"),
]

# ---------------------------------------------------------------------------
# Recipe definitions.
#
# Each ingredient tuple is:
#   (raw_name, raw_measure, requirement_type, bottle_type, ingredient_name, notes)
#
# requirement_type rules, matching matching.py:
#   'bottle_type' -> needs a bottle. Fungible types (gin/vodka/rum/tequila/
#                    brandy/cognac/vermouth/whiskey family) match by category.
#                    'liqueur'/'amaro'/'other' match by NAME via substring,
#                    so `notes` must contain the distinctive keyword.
#   'ingredient'  -> matches the user's mixer checklist by exact name.
#   'optional'    -> garnishes, floats, rinses. Never blocks makeability.
# ---------------------------------------------------------------------------

RECIPES = [
    # ============================== RUM ====================================
    {
        "name": "Rum Old Fashioned",
        "glass": "Rocks glass",
        "source_url": "https://www.diffordsguide.com/cocktails/recipe/1737/rum-old-fashioned",
        "instructions": (
            "The Old Fashioned template is spirit-agnostic and rum takes to it better "
            "than almost anything else. Aged rum already tastes a little sweet, so go "
            "lighter on the syrup than you would with bourbon.\n\n"
            "1. Add 2 oz aged rum, 1 tsp simple syrup and 2 dashes of Angostura bitters to a rocks glass.\n"
            "2. Add one large ice cube.\n"
            "3. Stir for 30 seconds. It should get noticeably colder and slightly diluted.\n"
            "4. Express an orange twist over the top and drop it in.\n\n"
            "Demerara syrup instead of simple is the upgrade here if you ever make it."
        ),
        "ingredients": [
            ("Aged rum", "2 oz", "bottle_type", "rum", None, "Aged or dark rum has more to work with than white"),
            ("Simple syrup", "1 tsp", "ingredient", None, "Simple syrup", None),
            ("Angostura bitters", "2 dashes", "ingredient", None, "Angostura bitters", None),
            ("Orange twist", "1", "optional", None, "Oranges", "Garnish"),
        ],
    },
    {
        "name": "Ti' Punch",
        "glass": "Rocks glass",
        "source_url": "https://punchdrink.com/recipes/ti-punch/",
        "instructions": (
            "Martinique's everyday drink. Three ingredients, no ice in the traditional "
            "build, and the lime is a coin cut from the side of the fruit rather than a "
            "wedge, so you get oil and a little juice but no pith.\n\n"
            "1. Cut a thin disc from the side of a lime, peel and all.\n"
            "2. Drop it into a short glass with 1 tsp cane or simple syrup.\n"
            "3. Press it gently with a spoon. Do not muddle it to death.\n"
            "4. Add 2 oz rum and stir.\n"
            "5. Ice is optional and locals often skip it. Add one cube if you want it colder.\n\n"
            "Rhum agricole is the real thing, but any decent white rum makes a good drink."
        ),
        "ingredients": [
            ("Rhum agricole blanc", "2 oz", "bottle_type", "rum", None, "Agricole is traditional; white rum works"),
            ("Cane syrup", "1 tsp", "ingredient", None, "Simple syrup", "Cane syrup traditionally; simple syrup is fine"),
            ("Lime disc", "1", "ingredient", None, "Limes", "A coin cut from the side, not a wedge"),
        ],
    },
    {
        "name": "Queen's Park Swizzle",
        "glass": "Highball glass",
        "source_url": "https://www.diffordsguide.com/cocktails/recipe/1633/queens-park-swizzle",
        "instructions": (
            "A mojito that grew up, from the Queen's Park Hotel in Trinidad. The whole "
            "trick is the bitters float: you dash them on top at the end and do not stir "
            "them in, so the first sip is aromatic and the rest is not.\n\n"
            "1. Lightly press 8 mint leaves and 3/4 oz simple syrup in the bottom of a highball.\n"
            "2. Add 1 oz lime juice and 2 oz aged rum.\n"
            "3. Fill with crushed ice and swizzle with a bar spoon until the glass frosts.\n"
            "4. Top with more crushed ice to form a dome.\n"
            "5. Dash 4 to 6 dashes of Angostura over the top. Do not stir.\n"
            "6. Garnish with a mint sprig."
        ),
        "ingredients": [
            ("Aged rum", "2 oz", "bottle_type", "rum", None, "Demerara rum traditionally"),
            ("Lime juice", "1 oz", "ingredient", None, "Lime juice (fresh)", None),
            ("Simple syrup", "3/4 oz", "ingredient", None, "Simple syrup", None),
            ("Fresh mint", "8 leaves", "ingredient", None, "Fresh mint", None),
            ("Angostura bitters", "4-6 dashes", "ingredient", None, "Angostura bitters", "Floated on top, not stirred in"),
        ],
    },
    {
        "name": "Airmail",
        "glass": "Flute",
        "source_url": "https://www.diffordsguide.com/cocktails/recipe/126/air-mail",
        "instructions": (
            "A Daiquiri with honey instead of sugar, lengthened with something fizzy. "
            "Named for airmail postage, which tells you roughly how old it is.\n\n"
            "1. Warm 1/2 oz honey with a splash of hot water and stir until it pours freely.\n"
            "2. Shake the honey with 1 1/2 oz rum and 1/2 oz lime juice over ice.\n"
            "3. Strain into a chilled flute.\n"
            "4. Top with about 2 oz Champagne or Prosecco.\n"
            "5. Garnish with a mint sprig if you have one.\n\n"
            "Honey straight from the jar will clump in a cold shaker. Thin it first."
        ),
        "ingredients": [
            ("Gold rum", "1 1/2 oz", "bottle_type", "rum", None, None),
            ("Lime juice", "1/2 oz", "ingredient", None, "Lime juice (fresh)", None),
            ("Honey", "1/2 oz", "ingredient", None, "Honey", "Thin with a splash of hot water first"),
            ("Champagne", "2 oz", "ingredient", None, "Champagne", "Prosecco or any dry sparkling works"),
            ("Fresh mint", "1 sprig", "optional", None, "Fresh mint", "Garnish"),
        ],
    },
    {
        "name": "Canchanchara",
        "glass": "Rocks glass",
        "source_url": "https://punchdrink.com/recipes/canchanchara/",
        "instructions": (
            "Cuba's oldest cocktail, from Trinidad de Cuba, and reputedly what the "
            "independence fighters drank. Rum, lime, honey. It predates the Daiquiri and "
            "tastes like the rough draft of one, in a good way.\n\n"
            "1. Stir 3/4 oz honey with a splash of warm water in the glass until loose.\n"
            "2. Add 3/4 oz lime juice and stir again.\n"
            "3. Add 2 oz rum and a scoop of ice.\n"
            "4. Stir until cold.\n"
            "5. Garnish with a lime wheel."
        ),
        "ingredients": [
            ("White rum", "2 oz", "bottle_type", "rum", None, "Aguardiente traditionally; white rum is the usual stand-in"),
            ("Lime juice", "3/4 oz", "ingredient", None, "Lime juice (fresh)", None),
            ("Honey", "3/4 oz", "ingredient", None, "Honey", "Loosen with warm water"),
            ("Lime wheel", "1", "optional", None, "Limes", "Garnish"),
        ],
    },
    {
        "name": "Mary Pickford",
        "glass": "Coupe",
        "source_url": "https://www.diffordsguide.com/cocktails/recipe/1096/mary-pickford",
        "instructions": (
            "Havana, Prohibition era, named for the silent film star. Pink, tropical and "
            "much drier than it looks because the grenadine is a teaspoon, not a glug.\n\n"
            "1. Shake 1 1/2 oz white rum, 1 1/2 oz pineapple juice and 1 tsp grenadine hard over ice.\n"
            "2. Add 1 tsp maraschino liqueur if you have it.\n"
            "3. Strain into a chilled coupe.\n"
            "4. Garnish with a cherry.\n\n"
            "Published specs disagree on the maraschino, and plenty of good versions leave "
            "it out entirely, so it is listed as optional here."
        ),
        "ingredients": [
            ("White rum", "1 1/2 oz", "bottle_type", "rum", None, None),
            ("Pineapple juice", "1 1/2 oz", "ingredient", None, "Pineapple juice", None),
            ("Grenadine", "1 tsp", "ingredient", None, "Grenadine", None),
            ("Maraschino liqueur", "1 tsp", "optional", None, None, "Traditional but the drink stands without it"),
            ("Maraschino cherry", "1", "optional", None, "Maraschino cherries", "Garnish"),
        ],
    },
    {
        "name": "Bacardi Cocktail",
        "glass": "Coupe",
        "source_url": "https://iba-world.com/iba-cocktail/bacardi/",
        "instructions": (
            "A Daiquiri with grenadine. In 1936 a New York court ruled that a drink sold "
            "under this name legally had to be made with Bacardi rum, which is the most "
            "1930s sentence in cocktail history.\n\n"
            "1. Shake 2 oz white rum, 3/4 oz lime juice and 1/2 oz grenadine hard over ice.\n"
            "2. Double strain into a chilled coupe.\n"
            "3. No garnish needed. The colour is the garnish.\n\n"
            "Real pomegranate grenadine matters here. The neon stuff makes it taste like "
            "cough syrup."
        ),
        "ingredients": [
            ("White rum", "2 oz", "bottle_type", "rum", None, None),
            ("Lime juice", "3/4 oz", "ingredient", None, "Lime juice (fresh)", None),
            ("Grenadine", "1/2 oz", "ingredient", None, "Grenadine", "Use a real pomegranate grenadine if you can"),
        ],
    },
    {
        "name": "Hurricane",
        "glass": "Hurricane glass",
        "source_url": "https://www.diffordsguide.com/cocktails/recipe/875/hurricane",
        "instructions": (
            "Pat O'Brien's in New Orleans, invented because rum was the only spirit anyone "
            "could get during the war and the bar had far too much of it. The original is "
            "just rum, passion fruit syrup and lemon.\n\n"
            "1. Shake 2 oz rum (ideally half light, half dark), 1 oz passion fruit syrup, "
            "3/4 oz lemon juice, 1/2 oz orange juice and a dash of grenadine over ice.\n"
            "2. Pour unstrained into a tall glass.\n"
            "3. Top with more crushed ice if needed.\n"
            "4. Garnish with an orange slice and a cherry.\n\n"
            "Splitting the rum between a light and an aged bottle is the classic move if "
            "you own both."
        ),
        "ingredients": [
            ("Rum", "2 oz", "bottle_type", "rum", None, "Traditionally split between light and dark rum"),
            ("Passion fruit syrup", "1 oz", "ingredient", None, "Passion Fruit Syrup", None),
            ("Lemon juice", "3/4 oz", "ingredient", None, "Lemon juice (fresh)", None),
            ("Orange juice", "1/2 oz", "ingredient", None, "Orange juice", None),
            ("Grenadine", "1 dash", "ingredient", None, "Grenadine", None),
            ("Orange slice", "1", "optional", None, "Oranges", "Garnish"),
            ("Maraschino cherry", "1", "optional", None, "Maraschino cherries", "Garnish"),
        ],
    },
    {
        "name": "Bee's Kiss",
        "glass": "Coupe",
        "source_url": "https://www.diffordsguide.com/cocktails/recipe/253/bees-kiss",
        "instructions": (
            "Three ingredients, no citrus, tastes like a rum milkshake that went to "
            "finishing school. Underrated and almost nobody orders it.\n\n"
            "1. Loosen 1/2 oz honey with a splash of warm water.\n"
            "2. Shake it hard with 2 oz white rum and 1 oz heavy cream over ice.\n"
            "3. Shake longer than feels necessary. Cream needs the work.\n"
            "4. Double strain into a chilled coupe.\n"
            "5. Grate nutmeg over the top if you have any."
        ),
        "ingredients": [
            ("White rum", "2 oz", "bottle_type", "rum", None, None),
            ("Honey", "1/2 oz", "ingredient", None, "Honey", "Loosen with warm water first"),
            ("Heavy cream", "1 oz", "ingredient", None, "Heavy cream", None),
        ],
    },
    {
        "name": "Fog Cutter",
        "glass": "Highball glass",
        "source_url": "https://www.diffordsguide.com/cocktails/recipe/711/fog-cutter",
        "instructions": (
            "Trader Vic's, and he said of it: \"Fog Cutter, hell. After two of these you "
            "won't even see the stuff.\" Rum, brandy and gin in one glass, which sounds "
            "like a mistake and is not.\n\n"
            "1. Shake 2 oz light rum, 1 oz brandy, 1/2 oz gin, 2 oz lemon juice, 1 oz orange "
            "juice and 1/2 oz orgeat over ice.\n"
            "2. Pour into a tall glass filled with crushed ice.\n"
            "3. Float 1/2 oz sweet sherry on top if you have it.\n"
            "4. Garnish with mint.\n\n"
            "Needs three separate bottles, so it will not show as makeable unless you own "
            "a rum, a brandy and a gin."
        ),
        "ingredients": [
            ("Light rum", "2 oz", "bottle_type", "rum", None, None),
            ("Brandy", "1 oz", "bottle_type", "brandy", None, "Cognac or any brandy"),
            ("Gin", "1/2 oz", "bottle_type", "gin", None, None),
            ("Lemon juice", "2 oz", "ingredient", None, "Lemon juice (fresh)", None),
            ("Orange juice", "1 oz", "ingredient", None, "Orange juice", None),
            ("Orgeat", "1/2 oz", "ingredient", None, "Orgeat Syrup", None),
            ("Sweet sherry float", "1/2 oz", "optional", None, None, "Traditional float, skip it if you have none"),
            ("Fresh mint", "1 sprig", "optional", None, "Fresh mint", "Garnish"),
        ],
    },
    {
        "name": "Jamaican Mule",
        "glass": "Copper mug",
        "source_url": "https://www.diffordsguide.com/cocktails/recipe/3556/jamaican-mule",
        "instructions": (
            "The Moscow Mule with rum instead of vodka, which is a straight upgrade "
            "because funky Jamaican rum and ginger were made for each other.\n\n"
            "1. Fill a mug or highball with ice.\n"
            "2. Add 2 oz rum and 1/2 oz lime juice.\n"
            "3. Top with 4 oz ginger beer.\n"
            "4. Stir once, gently.\n"
            "5. Garnish with a lime wedge and mint.\n\n"
            "Ginger beer, not ginger ale. Ginger ale makes a much duller drink."
        ),
        "ingredients": [
            ("Jamaican rum", "2 oz", "bottle_type", "rum", None, "A funky Jamaican rum is best but any works"),
            ("Lime juice", "1/2 oz", "ingredient", None, "Lime juice (fresh)", None),
            ("Ginger beer", "4 oz", "ingredient", None, "Ginger beer", "Not ginger ale"),
            ("Lime wedge", "1", "optional", None, "Limes", "Garnish"),
            ("Fresh mint", "1 sprig", "optional", None, "Fresh mint", "Garnish"),
        ],
    },
    {
        "name": "Chet Baker",
        "glass": "Rocks glass",
        "source_url": "https://punchdrink.com/recipes/chet-baker/",
        "instructions": (
            "A modern classic from Sam Ross, and effectively a rum Manhattan sweetened "
            "with honey. Short, stirred, no citrus, very easy to like.\n\n"
            "1. Loosen 1 tsp honey with a splash of warm water.\n"
            "2. Stir it with 1 1/2 oz aged rum, 1/2 oz sweet vermouth and 2 dashes of "
            "Angostura over ice for 20 seconds.\n"
            "3. Strain over one large cube in a rocks glass.\n"
            "4. Express an orange twist over the top and drop it in."
        ),
        "ingredients": [
            ("Aged rum", "1 1/2 oz", "bottle_type", "rum", None, None),
            ("Sweet Vermouth", "1/2 oz", "bottle_type", "vermouth_sweet", None, "Sweet vermouth"),
            ("Honey", "1 tsp", "ingredient", None, "Honey", "Loosen with warm water"),
            ("Angostura bitters", "2 dashes", "ingredient", None, "Angostura bitters", None),
            ("Orange twist", "1", "optional", None, "Oranges", "Garnish"),
        ],
    },

    # ============================= AGAVE ===================================
    {
        "name": "Ranch Water",
        "glass": "Highball glass",
        "source_url": "https://punchdrink.com/recipes/ranch-water/",
        "instructions": (
            "West Texas, three ingredients, and the closest thing to a perfect hot-weather "
            "drink. Traditionally made by drinking an inch out of a bottle of Topo Chico "
            "and pouring the tequila and lime straight in.\n\n"
            "1. Fill a tall glass with ice.\n"
            "2. Add 2 oz blanco tequila and 3/4 oz lime juice.\n"
            "3. Top with 4 oz sparkling mineral water.\n"
            "4. Stir once.\n"
            "5. Garnish with a lime wedge.\n\n"
            "Highly carbonated mineral water makes a real difference over regular soda water."
        ),
        "ingredients": [
            ("Blanco tequila", "2 oz", "bottle_type", "tequila", None, None),
            ("Lime juice", "3/4 oz", "ingredient", None, "Lime juice (fresh)", None),
            ("Sparkling mineral water", "4 oz", "ingredient", None, "Soda water / club soda", "Topo Chico is traditional"),
            ("Lime wedge", "1", "optional", None, "Limes", "Garnish"),
        ],
    },
    {
        "name": "Batanga",
        "glass": "Highball glass",
        "source_url": "https://punchdrink.com/recipes/batanga/",
        "instructions": (
            "From La Capilla in Tequila, Mexico, where Don Javier Delgado Corona made them "
            "for sixty years and stirred every one with the same knife he used for the "
            "limes. Tequila and Coke, but the salt rim and fresh lime turn it into an "
            "actual cocktail.\n\n"
            "1. Rub a lime wedge round the rim of a tall glass and dip it in salt.\n"
            "2. Fill with ice.\n"
            "3. Add 2 oz tequila and 1/2 oz lime juice.\n"
            "4. Top with 4 oz cola.\n"
            "5. Stir with a knife if you want to do it properly."
        ),
        "ingredients": [
            ("Tequila", "2 oz", "bottle_type", "tequila", None, None),
            ("Lime juice", "1/2 oz", "ingredient", None, "Lime juice (fresh)", None),
            ("Cola", "4 oz", "ingredient", None, "Cola", None),
            ("Salt", "for the rim", "ingredient", None, "Salt", None),
            ("Lime wedge", "1", "optional", None, "Limes", "Garnish"),
        ],
    },
    {
        "name": "Siesta",
        "glass": "Coupe",
        "source_url": "https://punchdrink.com/recipes/siesta/",
        "instructions": (
            "Katie Stipe, 2006. A Hemingway Daiquiri built on tequila with Campari doing "
            "the bitter work. One of the few modern drinks that has genuinely stuck.\n\n"
            "1. Shake 2 oz tequila, 1/2 oz Campari, 1/2 oz grapefruit juice, 1/2 oz lime "
            "juice and 1/2 oz simple syrup hard over ice.\n"
            "2. Double strain into a chilled coupe.\n"
            "3. Garnish with a grapefruit or lime twist."
        ),
        "ingredients": [
            ("Tequila", "2 oz", "bottle_type", "tequila", None, None),
            ("Campari", "1/2 oz", "bottle_type", "liqueur", None, "Campari"),
            ("Grapefruit juice", "1/2 oz", "ingredient", None, "Grapefruit juice", None),
            ("Lime juice", "1/2 oz", "ingredient", None, "Lime juice (fresh)", None),
            ("Simple syrup", "1/2 oz", "ingredient", None, "Simple syrup", None),
        ],
    },
    {
        "name": "Rosita",
        "glass": "Rocks glass",
        "source_url": "https://www.diffordsguide.com/cocktails/recipe/1719/rosita",
        "instructions": (
            "A tequila Negroni with both vermouths, from Gary Regan's Bartender's Bible. "
            "Bitter, herbal, entirely stirred, and a good argument that reposado belongs "
            "in spirit-forward drinks.\n\n"
            "1. Stir 1 1/2 oz reposado tequila, 1/2 oz Campari, 1/2 oz sweet vermouth, "
            "1/2 oz dry vermouth and a dash of Angostura over ice.\n"
            "2. Stir for a full 25 seconds.\n"
            "3. Strain over fresh ice in a rocks glass.\n"
            "4. Garnish with a lemon twist."
        ),
        "ingredients": [
            ("Reposado tequila", "1 1/2 oz", "bottle_type", "tequila", None, None),
            ("Campari", "1/2 oz", "bottle_type", "liqueur", None, "Campari"),
            ("Sweet Vermouth", "1/2 oz", "bottle_type", "vermouth_sweet", None, "Sweet vermouth"),
            ("Dry Vermouth", "1/2 oz", "bottle_type", "vermouth_dry", None, "Dry vermouth"),
            ("Angostura bitters", "1 dash", "ingredient", None, "Angostura bitters", None),
            ("Lemon twist", "1", "optional", None, "Lemons", "Garnish"),
        ],
    },
    {
        "name": "Tequila Sour",
        "glass": "Coupe",
        "source_url": "https://www.diffordsguide.com/cocktails/recipe/1957/tequila-sour",
        "instructions": (
            "The sour template with tequila. Agave and lemon is a less obvious pairing "
            "than agave and lime, and it works because lemon lets the vegetal side of the "
            "tequila through.\n\n"
            "1. Dry shake 2 oz tequila, 3/4 oz lemon juice, 1/2 oz simple syrup and one "
            "egg white with NO ice for 15 seconds.\n"
            "2. Add ice and shake again until very cold.\n"
            "3. Double strain into a chilled coupe.\n"
            "4. Let the foam settle, then dash bitters across the top.\n\n"
            "The dry shake first is what builds the foam. Skipping it gives you a thin, "
            "sad head."
        ),
        "ingredients": [
            ("Tequila", "2 oz", "bottle_type", "tequila", None, None),
            ("Lemon juice", "3/4 oz", "ingredient", None, "Lemon juice (fresh)", None),
            ("Simple syrup", "1/2 oz", "ingredient", None, "Simple syrup", None),
            ("Egg white", "1", "ingredient", None, "Egg whites", None),
            ("Angostura bitters", "3 dashes", "optional", None, "Angostura bitters", "Dashed over the foam"),
        ],
    },
    {
        "name": "Juan Collins",
        "glass": "Collins glass",
        "source_url": "https://www.diffordsguide.com/cocktails/recipe/1017/juan-collins",
        "instructions": (
            "The Tom Collins with tequila. Long, cold, low effort, and one of the better "
            "ways to make a big-batch drink for a group.\n\n"
            "1. Add 2 oz tequila, 1 oz lemon juice and 1/2 oz simple syrup to a tall glass.\n"
            "2. Fill with ice and stir.\n"
            "3. Top with 3 oz soda water.\n"
            "4. Garnish with a lemon wheel and a cherry."
        ),
        "ingredients": [
            ("Tequila", "2 oz", "bottle_type", "tequila", None, None),
            ("Lemon juice", "1 oz", "ingredient", None, "Lemon juice (fresh)", None),
            ("Simple syrup", "1/2 oz", "ingredient", None, "Simple syrup", None),
            ("Soda water", "3 oz", "ingredient", None, "Soda water / club soda", None),
            ("Lemon wheel", "1", "optional", None, "Lemons", "Garnish"),
            ("Maraschino cherry", "1", "optional", None, "Maraschino cherries", "Garnish"),
        ],
    },
    {
        "name": "Cantarito",
        "glass": "Clay cup",
        "source_url": "https://punchdrink.com/recipes/cantarito/",
        "instructions": (
            "A Paloma with all three citruses, traditionally served in an unglazed clay "
            "cup that adds an earthy note as you drink. Jalisco's answer to a long "
            "afternoon.\n\n"
            "1. Salt the rim of a tall glass or clay cup.\n"
            "2. Fill with ice.\n"
            "3. Add 2 oz tequila, 1/2 oz lime juice, 1/2 oz lemon juice and 1 oz orange juice.\n"
            "4. Add 2 oz grapefruit juice.\n"
            "5. Top with soda water and stir gently.\n"
            "6. Garnish with citrus wheels."
        ),
        "ingredients": [
            ("Tequila", "2 oz", "bottle_type", "tequila", None, None),
            ("Grapefruit juice", "2 oz", "ingredient", None, "Grapefruit juice", None),
            ("Orange juice", "1 oz", "ingredient", None, "Orange juice", None),
            ("Lime juice", "1/2 oz", "ingredient", None, "Lime juice (fresh)", None),
            ("Lemon juice", "1/2 oz", "ingredient", None, "Lemon juice (fresh)", None),
            ("Soda water", "2 oz", "ingredient", None, "Soda water / club soda", None),
            ("Salt", "for the rim", "ingredient", None, "Salt", None),
            ("Citrus wheels", "assorted", "optional", None, "Limes", "Garnish"),
        ],
    },
    {
        "name": "Tequila Old Fashioned",
        "glass": "Rocks glass",
        "source_url": "https://www.diffordsguide.com/cocktails/recipe/4108/tequila-old-fashioned",
        "instructions": (
            "Agave syrup instead of sugar, because sweetening tequila with its own raw "
            "material is the obvious move. Mole bitters are what turn this from a novelty "
            "into a genuinely good drink.\n\n"
            "1. Add 2 oz reposado or anejo tequila and 1 tsp agave syrup to a rocks glass.\n"
            "2. Add 2 dashes of Angostura and 1 dash of mole bitters.\n"
            "3. Add one large cube and stir for 30 seconds.\n"
            "4. Express an orange twist over the top and drop it in.\n\n"
            "Blanco works but reposado has the vanilla and oak that make the format sing."
        ),
        "ingredients": [
            ("Reposado tequila", "2 oz", "bottle_type", "tequila", None, "Reposado or anejo; blanco works at a push"),
            ("Agave syrup", "1 tsp", "ingredient", None, "Agave Syrup", None),
            ("Angostura bitters", "2 dashes", "ingredient", None, "Angostura bitters", None),
            ("Mole bitters", "1 dash", "ingredient", None, "Mole Bitters", None),
            ("Orange twist", "1", "optional", None, "Oranges", "Garnish"),
        ],
    },
    {
        "name": "Vampiro",
        "glass": "Highball glass",
        "source_url": "https://www.diffordsguide.com/cocktails/recipe/4634/vampiro",
        "instructions": (
            "Mexico's savoury tequila highball, and a much better drink than the Bloody "
            "Maria because the orange juice and grenadine keep it from being heavy.\n\n"
            "1. Salt the rim of a tall glass and fill with ice.\n"
            "2. Add 2 oz tequila, 2 oz tomato juice, 1 oz orange juice, 1/2 oz lime juice "
            "and 1/2 oz grenadine.\n"
            "3. Add hot sauce to taste. Start with 3 dashes.\n"
            "4. Stir well.\n"
            "5. Garnish with a lime wedge and, if you are feeling it, a slice of chilli."
        ),
        "ingredients": [
            ("Tequila", "2 oz", "bottle_type", "tequila", None, None),
            ("Tomato juice", "2 oz", "ingredient", None, "Tomato juice", None),
            ("Orange juice", "1 oz", "ingredient", None, "Orange juice", None),
            ("Lime juice", "1/2 oz", "ingredient", None, "Lime juice (fresh)", None),
            ("Grenadine", "1/2 oz", "ingredient", None, "Grenadine", None),
            ("Hot sauce", "3 dashes", "ingredient", None, "Tabasco / hot sauce", None),
            ("Salt", "for the rim", "ingredient", None, "Salt", None),
            ("Lime wedge", "1", "optional", None, "Limes", "Garnish"),
        ],
    },

    # ========================== VODKA AND GIN ==============================
    {
        "name": "Dirty Martini",
        "glass": "Martini glass",
        "source_url": "https://www.diffordsguide.com/cocktails/recipe/1218/dirty-martini",
        "instructions": (
            "A Martini with olive brine in it. Divisive, and the people who like it really "
            "like it. Vodka or gin both work; gin gives you more to taste against the salt.\n\n"
            "1. Stir 2 1/2 oz vodka, 1/2 oz dry vermouth and 1/2 oz olive brine over ice "
            "for 25 seconds.\n"
            "2. Strain into a chilled martini glass.\n"
            "3. Garnish with three olives on a pick.\n\n"
            "The brine is the liquid straight from the olive jar. Taste it first; jars "
            "vary wildly in saltiness."
        ),
        "ingredients": [
            ("Vodka", "2 1/2 oz", "bottle_type", "vodka", None, "Gin works too"),
            ("Dry Vermouth", "1/2 oz", "bottle_type", "vermouth_dry", None, "Dry vermouth"),
            ("Olive brine", "1/2 oz", "ingredient", None, "Olives", "The liquid from the olive jar"),
            ("Olives", "3", "optional", None, "Olives", "Garnish"),
        ],
    },
    {
        "name": "Gibson",
        "glass": "Martini glass",
        "source_url": "https://www.diffordsguide.com/cocktails/recipe/774/gibson",
        "instructions": (
            "A Martini garnished with a pickled onion instead of an olive or a twist. That "
            "is the entire difference, and it changes the drink more than it has any right "
            "to.\n\n"
            "1. Stir 2 1/2 oz gin and 1/2 oz dry vermouth over ice for 25 seconds.\n"
            "2. Strain into a chilled martini glass.\n"
            "3. Garnish with two cocktail onions.\n\n"
            "Do not add onion brine. That is a different drink and it is not this one."
        ),
        "ingredients": [
            ("Gin", "2 1/2 oz", "bottle_type", "gin", None, None),
            ("Dry Vermouth", "1/2 oz", "bottle_type", "vermouth_dry", None, "Dry vermouth"),
            ("Cocktail onions", "2", "ingredient", None, "Cocktail onions", "The garnish IS the drink here"),
        ],
    },
    {
        "name": "Cape Codder",
        "glass": "Highball glass",
        "source_url": "https://www.diffordsguide.com/cocktails/recipe/420/cape-codder",
        "instructions": (
            "Vodka and cranberry, with enough lime to stop it being a soft drink with "
            "alcohol in it. Two minutes of effort, no shaker required.\n\n"
            "1. Fill a tall glass with ice.\n"
            "2. Add 2 oz vodka and 1/2 oz lime juice.\n"
            "3. Top with 4 oz cranberry juice.\n"
            "4. Stir and garnish with a lime wedge.\n\n"
            "Use cranberry juice rather than cranberry cocktail if you can find it, then "
            "adjust with a little simple syrup."
        ),
        "ingredients": [
            ("Vodka", "2 oz", "bottle_type", "vodka", None, None),
            ("Cranberry juice", "4 oz", "ingredient", None, "Cranberry juice", None),
            ("Lime juice", "1/2 oz", "ingredient", None, "Lime juice (fresh)", None),
            ("Lime wedge", "1", "optional", None, "Limes", "Garnish"),
        ],
    },
    {
        "name": "Bay Breeze",
        "glass": "Highball glass",
        "source_url": "https://www.diffordsguide.com/cocktails/recipe/246/bay-breeze",
        "instructions": (
            "The Sea Breeze with pineapple where the grapefruit was, which makes it "
            "sweeter and much easier to drink quickly. Consider that a warning.\n\n"
            "1. Fill a tall glass with ice.\n"
            "2. Add 1 1/2 oz vodka.\n"
            "3. Add 3 oz pineapple juice and 1 1/2 oz cranberry juice.\n"
            "4. Stir gently so it stays layered, or stir hard if you would rather it be pink.\n"
            "5. Garnish with a lime wedge."
        ),
        "ingredients": [
            ("Vodka", "1 1/2 oz", "bottle_type", "vodka", None, None),
            ("Pineapple juice", "3 oz", "ingredient", None, "Pineapple juice", None),
            ("Cranberry juice", "1 1/2 oz", "ingredient", None, "Cranberry juice", None),
            ("Lime wedge", "1", "optional", None, "Limes", "Garnish"),
        ],
    },
    {
        "name": "Chi-Chi",
        "glass": "Hurricane glass",
        "source_url": "https://www.diffordsguide.com/cocktails/recipe/468/chi-chi",
        "instructions": (
            "A Pina Colada made with vodka. Lighter than the rum version because vodka "
            "gets out of the way of the coconut.\n\n"
            "1. Blend 2 oz vodka, 3 oz pineapple juice and 1 oz coconut cream with a cup "
            "of crushed ice until smooth.\n"
            "2. Pour into a tall glass.\n"
            "3. Garnish with a pineapple wedge and a cherry.\n\n"
            "No blender? Shake it very hard over ice and pour over fresh crushed ice. "
            "Different texture, same drink."
        ),
        "ingredients": [
            ("Vodka", "2 oz", "bottle_type", "vodka", None, None),
            ("Pineapple juice", "3 oz", "ingredient", None, "Pineapple juice", None),
            ("Coconut cream", "1 oz", "ingredient", None, "Coconut cream", None),
            ("Maraschino cherry", "1", "optional", None, "Maraschino cherries", "Garnish"),
        ],
    },
    {
        "name": "Vodka Gimlet",
        "glass": "Coupe",
        "source_url": "https://www.diffordsguide.com/cocktails/recipe/785/vodka-gimlet",
        "instructions": (
            "Three ingredients, thirty seconds, and one of the sharpest drinks you can "
            "make from a bare cupboard.\n\n"
            "1. Shake 2 oz vodka, 3/4 oz lime juice and 3/4 oz simple syrup hard over ice.\n"
            "2. Double strain into a chilled coupe.\n"
            "3. Garnish with a lime wheel.\n\n"
            "Fresh lime, not cordial. Rose's makes a completely different and much sweeter "
            "drink."
        ),
        "ingredients": [
            ("Vodka", "2 oz", "bottle_type", "vodka", None, None),
            ("Lime juice", "3/4 oz", "ingredient", None, "Lime juice (fresh)", None),
            ("Simple syrup", "3/4 oz", "ingredient", None, "Simple syrup", None),
            ("Lime wheel", "1", "optional", None, "Limes", "Garnish"),
        ],
    },
    {
        "name": "Caesar",
        "glass": "Highball glass",
        "source_url": "https://www.diffordsguide.com/cocktails/recipe/3372/caesar",
        "instructions": (
            "Invented in Calgary in 1969 by Walter Chell and drunk roughly 400 million "
            "times a year in Canada alone. The difference from a Bloody Mary is Clamato: "
            "tomato juice with clam broth in it, which sounds wrong and is not.\n\n"
            "1. Rim a tall glass with celery salt using a lime wedge.\n"
            "2. Fill with ice.\n"
            "3. Add 1 1/2 oz vodka, 4 dashes Worcestershire, 4 dashes hot sauce and a "
            "squeeze of lime.\n"
            "4. Top with 5 oz Clamato.\n"
            "5. Stir, then grind black pepper over the top.\n"
            "6. Garnish with a celery stalk, a lime wedge, and whatever else you can "
            "reasonably balance on the rim."
        ),
        "ingredients": [
            ("Vodka", "1 1/2 oz", "bottle_type", "vodka", None, None),
            ("Clamato", "5 oz", "ingredient", None, "Clamato / Caesar mix", "Not the same as tomato juice"),
            ("Worcestershire sauce", "4 dashes", "ingredient", None, "Worcestershire sauce", None),
            ("Hot sauce", "4 dashes", "ingredient", None, "Tabasco / hot sauce", None),
            ("Lime juice", "1/2 oz", "ingredient", None, "Lime juice (fresh)", None),
            ("Salt", "for the rim", "ingredient", None, "Salt", "Celery salt is the proper rim"),
            ("Pepper", "to taste", "ingredient", None, "Pepper", None),
            ("Celery stalk", "1", "optional", None, None, "Garnish"),
        ],
    },
    {
        "name": "Sex on the Beach",
        "glass": "Highball glass",
        "source_url": "https://iba-world.com/iba-cocktail/sex-on-the-beach/",
        "instructions": (
            "An IBA official cocktail, which surprises people. Peach schnapps, two juices, "
            "and no pretence at being anything other than fun.\n\n"
            "1. Fill a tall glass with ice.\n"
            "2. Add 1 1/2 oz vodka and 1/2 oz peach schnapps.\n"
            "3. Add 2 oz cranberry juice and 2 oz orange juice.\n"
            "4. Stir briefly.\n"
            "5. Garnish with an orange slice."
        ),
        "ingredients": [
            ("Vodka", "1 1/2 oz", "bottle_type", "vodka", None, None),
            ("Peach schnapps", "1/2 oz", "bottle_type", "liqueur", None, "peach schnapps"),
            ("Cranberry juice", "2 oz", "ingredient", None, "Cranberry juice", None),
            ("Orange juice", "2 oz", "ingredient", None, "Orange juice", None),
            ("Orange slice", "1", "optional", None, "Oranges", "Garnish"),
        ],
    },
    {
        "name": "Woo Woo",
        "glass": "Highball glass",
        "source_url": "https://www.diffordsguide.com/cocktails/recipe/2145/woo-woo",
        "instructions": (
            "Sex on the Beach minus the orange juice. Sharper, shorter, and honestly the "
            "better of the two.\n\n"
            "1. Shake 1 1/2 oz vodka, 1 oz peach schnapps and 3 oz cranberry juice over ice.\n"
            "2. Strain into a tall glass over fresh ice.\n"
            "3. Squeeze a lime wedge over the top and drop it in."
        ),
        "ingredients": [
            ("Vodka", "1 1/2 oz", "bottle_type", "vodka", None, None),
            ("Peach schnapps", "1 oz", "bottle_type", "liqueur", None, "peach schnapps"),
            ("Cranberry juice", "3 oz", "ingredient", None, "Cranberry juice", None),
            ("Lime wedge", "1", "ingredient", None, "Limes", None),
        ],
    },
    {
        "name": "Pornstar Martini",
        "glass": "Coupe",
        "source_url": "https://www.diffordsguide.com/cocktails/recipe/3167/pornstar-martini",
        "instructions": (
            "Douglas Ankrah, London, 2002, and now one of the best-selling cocktails in "
            "the world. The shot of fizz on the side is not optional theatre; you are "
            "meant to alternate sips.\n\n"
            "1. Shake 2 oz vodka, 1 oz passion fruit syrup, 1/2 oz lime juice and a few "
            "drops of vanilla extract hard over ice.\n"
            "2. Double strain into a chilled coupe.\n"
            "3. Pour 2 oz Prosecco into a shot glass and serve it alongside.\n"
            "4. Float half a passion fruit on top if you have one.\n\n"
            "Vanilla vodka is traditional. A few drops of vanilla extract in a plain vodka "
            "gets you most of the way there."
        ),
        "ingredients": [
            ("Vanilla vodka", "2 oz", "bottle_type", "vodka", None, None),
            ("Passion fruit syrup", "1 oz", "ingredient", None, "Passion Fruit Syrup", None),
            ("Lime juice", "1/2 oz", "ingredient", None, "Lime juice (fresh)", None),
            ("Vanilla extract", "a few drops", "ingredient", None, "Vanilla Extract", "Skip if using vanilla vodka"),
            ("Prosecco", "2 oz", "ingredient", None, "Prosecco", "Served as a shot on the side"),
        ],
    },

    # ========================= BRANDY AND COGNAC ===========================
    {
        "name": "Japanese Cocktail",
        "glass": "Coupe",
        "source_url": "https://punchdrink.com/recipes/japanese-cocktail/",
        "instructions": (
            "In Jerry Thomas's 1862 book, which makes it one of the oldest recorded "
            "cocktails still worth drinking. Nothing Japanese about it; it was named for a "
            "diplomatic delegation visiting New York that year.\n\n"
            "1. Stir 2 oz cognac, 1/2 oz orgeat and 2 dashes of Angostura over ice for 20 "
            "seconds.\n"
            "2. Strain into a chilled coupe.\n"
            "3. Express a lemon twist over the surface and drop it in.\n\n"
            "Three ingredients, no citrus in the drink itself, and it tastes far more "
            "complex than it reads."
        ),
        "ingredients": [
            ("Cognac", "2 oz", "bottle_type", "brandy", None, "Cognac ideally; any decent brandy works"),
            ("Orgeat", "1/2 oz", "ingredient", None, "Orgeat Syrup", None),
            ("Angostura bitters", "2 dashes", "ingredient", None, "Angostura bitters", None),
            ("Lemon twist", "1", "optional", None, "Lemons", "Garnish"),
        ],
    },
    {
        "name": "Harvard",
        "glass": "Coupe",
        "source_url": "https://www.diffordsguide.com/cocktails/recipe/842/harvard",
        "instructions": (
            "A Manhattan with brandy in place of whiskey and a splash of soda to lift it. "
            "Late 1800s, and it deserves better than the obscurity it sits in.\n\n"
            "1. Stir 1 1/2 oz brandy, 3/4 oz sweet vermouth and 2 dashes of Angostura over "
            "ice for 20 seconds.\n"
            "2. Strain into a chilled coupe.\n"
            "3. Top with a splash of soda water.\n"
            "4. Garnish with a cherry."
        ),
        "ingredients": [
            ("Brandy", "1 1/2 oz", "bottle_type", "brandy", None, None),
            ("Sweet Vermouth", "3/4 oz", "bottle_type", "vermouth_sweet", None, "Sweet vermouth"),
            ("Angostura bitters", "2 dashes", "ingredient", None, "Angostura bitters", None),
            ("Soda water", "1 splash", "ingredient", None, "Soda water / club soda", None),
            ("Maraschino cherry", "1", "optional", None, "Maraschino cherries", "Garnish"),
        ],
    },
    {
        "name": "Brandy Sour",
        "glass": "Coupe",
        "source_url": "https://www.diffordsguide.com/cocktails/recipe/379/brandy-sour",
        "instructions": (
            "The sour template again, this time with brandy. Rounder and less sharp than a "
            "whiskey sour because brandy brings its own fruit.\n\n"
            "1. Dry shake 2 oz brandy, 3/4 oz lemon juice, 1/2 oz simple syrup and one egg "
            "white with no ice for 15 seconds.\n"
            "2. Add ice, shake hard again.\n"
            "3. Double strain into a chilled coupe.\n"
            "4. Dash Angostura over the foam once it settles.\n\n"
            "The egg white is optional but it is what makes it look like a cocktail rather "
            "than a juice."
        ),
        "ingredients": [
            ("Brandy", "2 oz", "bottle_type", "brandy", None, None),
            ("Lemon juice", "3/4 oz", "ingredient", None, "Lemon juice (fresh)", None),
            ("Simple syrup", "1/2 oz", "ingredient", None, "Simple syrup", None),
            ("Egg white", "1", "optional", None, "Egg whites", "For texture; the drink works without it"),
            ("Angostura bitters", "3 dashes", "optional", None, "Angostura bitters", "Dashed over the foam"),
        ],
    },
    {
        "name": "Brandy Daisy",
        "glass": "Highball glass",
        "source_url": "https://www.diffordsguide.com/cocktails/recipe/373/brandy-daisy",
        "instructions": (
            "The Daisy family is a sour lengthened with soda, and it is the direct ancestor "
            "of the Margarita, which is a tequila daisy. This is the brandy original.\n\n"
            "1. Shake 2 oz brandy, 3/4 oz lemon juice and 1/2 oz grenadine over ice.\n"
            "2. Strain into a tall glass over fresh ice.\n"
            "3. Top with 2 oz soda water.\n"
            "4. Garnish with an orange slice and a cherry."
        ),
        "ingredients": [
            ("Brandy", "2 oz", "bottle_type", "brandy", None, None),
            ("Lemon juice", "3/4 oz", "ingredient", None, "Lemon juice (fresh)", None),
            ("Grenadine", "1/2 oz", "ingredient", None, "Grenadine", None),
            ("Soda water", "2 oz", "ingredient", None, "Soda water / club soda", None),
            ("Orange slice", "1", "optional", None, "Oranges", "Garnish"),
        ],
    },
    {
        "name": "Nikolaschka",
        "glass": "Shot glass",
        "source_url": "https://www.diffordsguide.com/cocktails/recipe/3049/nikolaschka",
        "instructions": (
            "German, and barely a cocktail. A glass of brandy with a sugared lemon slice "
            "balanced on top. You eat the lemon, then drink the brandy, and the two combine "
            "in your mouth.\n\n"
            "1. Pour 1 1/2 oz cognac or brandy into a small glass.\n"
            "2. Lay a thin lemon slice across the rim.\n"
            "3. Heap sugar on one half of the slice.\n"
            "4. Fold the slice, eat it whole, then immediately drink the brandy.\n\n"
            "Ridiculous, extremely fun at a table, and a good party trick with almost no "
            "ingredients."
        ),
        "ingredients": [
            ("Cognac", "1 1/2 oz", "bottle_type", "brandy", None, "Cognac or any brandy"),
            ("Lemon slice", "1", "ingredient", None, "Lemons", "Cut thin"),
            ("Sugar", "1 tsp", "ingredient", None, "Sugar (white)", None),
        ],
    },
    {
        "name": "American Beauty",
        "glass": "Coupe",
        "source_url": "https://www.diffordsguide.com/cocktails/recipe/141/american-beauty",
        "instructions": (
            "A pre-Prohibition oddity that floats red wine on top of a brandy sour. It "
            "looks incredible and the wine gives you a dry, tannic first sip over "
            "something fruity underneath.\n\n"
            "1. Shake 1 oz brandy, 1 oz dry vermouth, 1 oz orange juice, 1/4 oz grenadine "
            "and a few mint leaves over ice.\n"
            "2. Double strain into a chilled coupe.\n"
            "3. Float 1/2 oz red wine over the back of a spoon so it sits on top.\n"
            "4. Garnish with mint.\n\n"
            "Pour the float slowly. Rushing it just mixes the wine in and you lose the "
            "whole effect."
        ),
        "ingredients": [
            ("Brandy", "1 oz", "bottle_type", "brandy", None, None),
            ("Dry Vermouth", "1 oz", "bottle_type", "vermouth_dry", None, "Dry vermouth"),
            ("Orange juice", "1 oz", "ingredient", None, "Orange juice", None),
            ("Grenadine", "1/4 oz", "ingredient", None, "Grenadine", None),
            ("Red wine", "1/2 oz", "ingredient", None, "Red Wine", "Floated on top"),
            ("Fresh mint", "3 leaves", "optional", None, "Fresh mint", None),
        ],
    },
    {
        "name": "Brandy Cobbler",
        "glass": "Highball glass",
        "source_url": "https://www.diffordsguide.com/cocktails/recipe/370/brandy-cobbler",
        "instructions": (
            "The Cobbler is what made the drinking straw popular in the 1830s, because you "
            "cannot drink around a mountain of crushed ice any other way. Same build as the "
            "Sherry Cobbler, more punch.\n\n"
            "1. Muddle two orange slices with 1/2 oz simple syrup in a shaker.\n"
            "2. Add 2 oz brandy and shake over ice.\n"
            "3. Strain into a tall glass packed with crushed ice.\n"
            "4. Churn with a spoon, then top with more crushed ice.\n"
            "5. Garnish with orange, berries and mint, and add a straw."
        ),
        "ingredients": [
            ("Brandy", "2 oz", "bottle_type", "brandy", None, None),
            ("Simple syrup", "1/2 oz", "ingredient", None, "Simple syrup", None),
            ("Orange slices", "2", "ingredient", None, "Oranges", "Muddled"),
            ("Fresh mint", "1 sprig", "optional", None, "Fresh mint", "Garnish"),
            ("Berries", "a few", "optional", None, None, "Garnish"),
        ],
    },

    # ===================== LOW-ABV AND APERITIF ============================
    {
        "name": "Adonis",
        "glass": "Coupe",
        "source_url": "https://punchdrink.com/recipes/adonis/",
        "instructions": (
            "Named after an 1884 Broadway musical. Sherry and sweet vermouth, no base "
            "spirit at all, so it lands around 15% and you can drink two before dinner "
            "without consequence.\n\n"
            "1. Stir 1 1/2 oz dry sherry, 1 1/2 oz sweet vermouth and 2 dashes of orange "
            "bitters over ice for 20 seconds.\n"
            "2. Strain into a chilled coupe.\n"
            "3. Express an orange twist over the top and drop it in.\n\n"
            "Fino or amontillado sherry. Cream sherry will make it cloying."
        ),
        "ingredients": [
            ("Dry Sherry", "1 1/2 oz", "bottle_type", "other", None, "sherry"),
            ("Sweet Vermouth", "1 1/2 oz", "bottle_type", "vermouth_sweet", None, "Sweet vermouth"),
            ("Orange bitters", "2 dashes", "ingredient", None, "Orange bitters", None),
            ("Orange twist", "1", "optional", None, "Oranges", "Garnish"),
        ],
    },
    {
        "name": "Bamboo",
        "glass": "Coupe",
        "source_url": "https://punchdrink.com/recipes/bamboo/",
        "instructions": (
            "The Adonis's drier sibling, created at the Grand Hotel in Yokohama in the "
            "1890s. Dry sherry and dry vermouth, so it is bracingly crisp and almost "
            "savoury.\n\n"
            "1. Stir 1 1/2 oz dry sherry, 1 1/2 oz dry vermouth, 1 dash orange bitters and "
            "1 dash Angostura over ice.\n"
            "2. Stir for a full 25 seconds. Low-ABV drinks need the dilution.\n"
            "3. Strain into a chilled coupe.\n"
            "4. Garnish with a lemon twist."
        ),
        "ingredients": [
            ("Dry Sherry", "1 1/2 oz", "bottle_type", "other", None, "sherry"),
            ("Dry Vermouth", "1 1/2 oz", "bottle_type", "vermouth_dry", None, "Dry vermouth"),
            ("Orange bitters", "1 dash", "ingredient", None, "Orange bitters", None),
            ("Angostura bitters", "1 dash", "ingredient", None, "Angostura bitters", None),
            ("Lemon twist", "1", "optional", None, "Lemons", "Garnish"),
        ],
    },
    {
        "name": "Milano-Torino",
        "glass": "Rocks glass",
        "source_url": "https://punchdrink.com/recipes/milano-torino/",
        "instructions": (
            "Campari from Milan, vermouth from Turin, and that is the whole name. This is "
            "the drink the Americano and then the Negroni were built on top of, so it is "
            "worth knowing on its own.\n\n"
            "1. Add 1 1/2 oz Campari and 1 1/2 oz sweet vermouth to a rocks glass with ice.\n"
            "2. Stir for 15 seconds.\n"
            "3. Garnish with an orange slice.\n\n"
            "Add soda and it is an Americano. Add gin and it is a Negroni. Two ingredients, "
            "three drinks."
        ),
        "ingredients": [
            ("Campari", "1 1/2 oz", "bottle_type", "liqueur", None, "Campari"),
            ("Sweet Vermouth", "1 1/2 oz", "bottle_type", "vermouth_sweet", None, "Sweet vermouth"),
            ("Orange slice", "1", "optional", None, "Oranges", "Garnish"),
        ],
    },
    {
        "name": "Cardinale",
        "glass": "Rocks glass",
        "source_url": "https://www.diffordsguide.com/cocktails/recipe/425/cardinale",
        "instructions": (
            "A Negroni made with dry vermouth instead of sweet. Sharper, drier, less "
            "syrupy, and a better warm-weather drink than the original.\n\n"
            "1. Stir 1 1/2 oz gin, 3/4 oz dry vermouth and 3/4 oz Campari over ice for 20 "
            "seconds.\n"
            "2. Strain over one large cube in a rocks glass.\n"
            "3. Express an orange twist over the top and drop it in."
        ),
        "ingredients": [
            ("Gin", "1 1/2 oz", "bottle_type", "gin", None, None),
            ("Dry Vermouth", "3/4 oz", "bottle_type", "vermouth_dry", None, "Dry vermouth"),
            ("Campari", "3/4 oz", "bottle_type", "liqueur", None, "Campari"),
            ("Orange twist", "1", "optional", None, "Oranges", "Garnish"),
        ],
    },
    {
        "name": "Old Pal",
        "glass": "Coupe",
        "source_url": "https://punchdrink.com/recipes/old-pal/",
        "instructions": (
            "A Boulevardier with rye instead of bourbon and dry vermouth instead of sweet. "
            "Harry MacElhone printed it in 1922 at Harry's New York Bar in Paris. Much "
            "leaner and more bitter than the Boulevardier.\n\n"
            "1. Stir 1 oz rye, 1 oz dry vermouth and 1 oz Campari over ice for 20 seconds.\n"
            "2. Strain into a chilled coupe.\n"
            "3. Garnish with a lemon twist.\n\n"
            "Equal parts is the historical spec. Push the rye to 1 1/2 oz if you want it "
            "less bitter."
        ),
        "ingredients": [
            ("Rye whiskey", "1 oz", "bottle_type", "rye", None, None),
            ("Dry Vermouth", "1 oz", "bottle_type", "vermouth_dry", None, "Dry vermouth"),
            ("Campari", "1 oz", "bottle_type", "liqueur", None, "Campari"),
            ("Lemon twist", "1", "optional", None, "Lemons", "Garnish"),
        ],
    },
    {
        "name": "Vermouth Cocktail",
        "glass": "Coupe",
        "source_url": "https://www.diffordsguide.com/cocktails/recipe/2087/vermouth-cocktail",
        "instructions": (
            "Vermouth treated as the base spirit rather than a modifier, which is how it "
            "was drunk in Italy long before anyone put gin in it. About 16% ABV.\n\n"
            "1. Stir 2 1/2 oz sweet vermouth with 2 dashes of Angostura over ice for 20 "
            "seconds.\n"
            "2. Strain into a chilled coupe.\n"
            "3. Garnish with a cherry and a lemon twist.\n\n"
            "Only worth making with vermouth that has been opened recently and kept in the "
            "fridge. It oxidises like wine, because it is wine."
        ),
        "ingredients": [
            ("Sweet Vermouth", "2 1/2 oz", "bottle_type", "vermouth_sweet", None, "Sweet vermouth"),
            ("Angostura bitters", "2 dashes", "ingredient", None, "Angostura bitters", None),
            ("Maraschino cherry", "1", "optional", None, "Maraschino cherries", "Garnish"),
            ("Lemon twist", "1", "optional", None, "Lemons", "Garnish"),
        ],
    },
    {
        "name": "Bicicletta",
        "glass": "Wine glass",
        "source_url": "https://punchdrink.com/recipes/bicicletta/",
        "instructions": (
            "Northern Italian, named for the wobbly ride home from the bar. Campari, white "
            "wine and soda, around 8% ABV, and the correct thing to drink at 4pm.\n\n"
            "1. Fill a large wine glass with ice.\n"
            "2. Add 1 1/2 oz Campari and 3 oz dry white wine.\n"
            "3. Top with soda water.\n"
            "4. Stir once and garnish with an orange or lemon slice.\n\n"
            "Any crisp dry white works. Pinot grigio is the traditional choice."
        ),
        "ingredients": [
            ("Campari", "1 1/2 oz", "bottle_type", "liqueur", None, "Campari"),
            ("White wine", "3 oz", "ingredient", None, "White Wine", "Dry and crisp; pinot grigio is traditional"),
            ("Soda water", "2 oz", "ingredient", None, "Soda water / club soda", None),
            ("Orange slice", "1", "optional", None, "Oranges", "Garnish"),
        ],
    },
    {
        "name": "Kalimotxo",
        "glass": "Highball glass",
        "source_url": "https://punchdrink.com/recipes/kalimotxo/",
        "instructions": (
            "Basque, equal parts red wine and cola, and drunk by the litre at Spanish "
            "festivals. It exists because it makes cheap wine drinkable, and it works "
            "better than it has any right to.\n\n"
            "1. Fill a tall glass with ice.\n"
            "2. Add 4 oz red wine.\n"
            "3. Add 4 oz cola.\n"
            "4. Stir once and squeeze a lemon wedge over the top.\n\n"
            "Do not use good wine. The point is that it rescues the bad stuff."
        ),
        "ingredients": [
            ("Red wine", "4 oz", "ingredient", None, "Red Wine", "Cheap and young is correct here"),
            ("Cola", "4 oz", "ingredient", None, "Cola", None),
            ("Lemon wedge", "1", "optional", None, "Lemons", "Garnish"),
        ],
    },
]


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate(conn, pending_ingredients):
    """Check every recipe against the schema rules and the ingredients table.
    `pending_ingredients` are the new rows this script will create, treated as
    if they already exist. Returns a list of human-readable problems."""
    problems = []
    known_ingredients = {
        row[0].lower() for row in conn.execute("SELECT name FROM ingredients")
    }
    known_ingredients |= {name.lower() for name, _cat in pending_ingredients}

    existing_recipes = {row[0] for row in conn.execute("SELECT name FROM recipes")}

    seen_names = set()
    for r in RECIPES:
        name = r["name"]
        if name in seen_names:
            problems.append(f"{name}: duplicated inside this script")
        seen_names.add(name)

        if not r["ingredients"]:
            problems.append(f"{name}: no ingredients")

        if not any(i[2] != "optional" for i in r["ingredients"]):
            problems.append(f"{name}: every ingredient is optional, so it would "
                            f"show as makeable for everyone")

        for raw_name, measure, req_type, bottle_type, ing_name, notes in r["ingredients"]:
            label = f"{name} / {raw_name}"

            if req_type not in VALID_REQ_TYPES:
                problems.append(f"{label}: bad requirement_type {req_type!r}")

            if req_type == "bottle_type":
                if bottle_type not in VALID_BOTTLE_TYPES:
                    problems.append(f"{label}: bad bottle_type {bottle_type!r}")
                # Name-matched types resolve by substring against bottle names,
                # so they need a distinctive keyword of at least 4 chars or the
                # matcher can never satisfy them.
                if bottle_type in NAME_MATCH_TYPES:
                    key = (notes or raw_name or "").strip()
                    if len(key) < 4:
                        problems.append(
                            f"{label}: name-matched {bottle_type} needs a longer "
                            f"keyword in notes (got {key!r})"
                        )

            elif req_type == "ingredient":
                if not ing_name:
                    problems.append(f"{label}: requirement_type 'ingredient' with no ingredient_name")
                elif ing_name.lower() not in known_ingredients:
                    problems.append(
                        f"{label}: ingredient_name {ing_name!r} is not in the "
                        f"ingredients table. Add it first or retag."
                    )

            elif req_type == "optional":
                if ing_name and ing_name.lower() not in known_ingredients:
                    problems.append(f"{label}: optional references unknown ingredient {ing_name!r}")

    # Recipe names collide with the catalog only in the sense that we skip them,
    # which is fine, but flag near-misses that suggest an accidental duplicate.
    for r in RECIPES:
        for existing in existing_recipes:
            if r["name"] != existing and r["name"].lower() == existing.lower():
                problems.append(
                    f"{r['name']}: differs from existing recipe {existing!r} only "
                    f"by case, which will create a confusing duplicate"
                )

    return problems


# ---------------------------------------------------------------------------
# Import
# ---------------------------------------------------------------------------

def guard_against_journal_files(db_path):
    """A stale .db-journal or .db-wal next to the database can make SQLite roll
    back committed work on open. That is what happened on 2026-07-23. Refuse to
    run if one is present."""
    bad = []
    for suffix in ("-journal", "-wal", "-shm"):
        path = db_path + suffix
        if os.path.exists(path):
            bad.append(path)
    if bad:
        print("REFUSING TO RUN. Found SQLite side files next to the database:")
        for p in bad:
            print("   ", p)
        print("\nThese can silently roll back committed data. Close anything using")
        print("the database, confirm it shut down cleanly, then remove them.")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Add 46 rum/agave/vodka/brandy/low-ABV recipes.")
    parser.add_argument("--commit", action="store_true",
                        help="Actually write. Without this it is a dry run.")
    parser.add_argument("--db", default=DB_PATH, help="Path to bomu.db")
    args = parser.parse_args()

    db_path = args.db
    guard_against_journal_files(db_path)

    if not os.path.exists(db_path):
        print(f"No database at {db_path}")
        sys.exit(1)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    print(f"Database: {db_path}")
    before = conn.execute("SELECT COUNT(*) FROM recipes").fetchone()[0]
    before_ing = conn.execute("SELECT COUNT(*) FROM ingredients").fetchone()[0]
    print(f"Recipes currently in catalog: {before}")
    print(f"Ingredients currently on the checklist: {before_ing}")
    print()

    # --- work out which new ingredients are actually needed ---------------
    existing_ing = {row[0].lower() for row in conn.execute("SELECT name FROM ingredients")}
    new_ingredients = [(n, c) for n, c in NEW_INGREDIENTS if n.lower() not in existing_ing]

    if new_ingredients:
        print(f"Will add {len(new_ingredients)} new checklist ingredients:")
        for n, c in new_ingredients:
            print(f"    {n:<24} ({c})")
        print("    NOTE: these start UNTICKED for every existing user, so the")
        print("    recipes depending on them stay invisible until people update")
        print("    their Mixers checklist.")
        print()
    else:
        print("All required ingredients already exist. Nothing to add there.")
        print()

    # --- validate ---------------------------------------------------------
    problems = validate(conn, new_ingredients)
    if problems:
        print(f"VALIDATION FAILED ({len(problems)} problems):")
        for p in problems:
            print("   ", p)
        conn.close()
        sys.exit(1)
    print(f"Validation passed for all {len(RECIPES)} recipes.")
    print()

    # --- figure out what is new -------------------------------------------
    existing = {row[0] for row in conn.execute("SELECT name FROM recipes")}
    to_add = [r for r in RECIPES if r["name"] not in existing]
    skipped = [r["name"] for r in RECIPES if r["name"] in existing]

    if skipped:
        print(f"Already present, will skip ({len(skipped)}):")
        for n in skipped:
            print("   ", n)
        print()

    if not to_add and not new_ingredients:
        print("Nothing to do. Catalog is already up to date.")
        conn.close()
        return

    if to_add:
        print(f"Will add {len(to_add)} recipes:")
        for r in to_add:
            n_req = sum(1 for i in r["ingredients"] if i[2] != "optional")
            n_opt = sum(1 for i in r["ingredients"] if i[2] == "optional")
            n_bottles = sum(1 for i in r["ingredients"] if i[2] == "bottle_type")
            print(f"    {r['name']:<26} {n_req} required ({n_bottles} bottles), {n_opt} optional")
        print()

    if not args.commit:
        print("DRY RUN. Nothing was written.")
        print("Re-run with --commit to apply.")
        conn.close()
        return

    # --- write ------------------------------------------------------------
    try:
        cur = conn.cursor()

        for name, category in new_ingredients:
            cur.execute(
                "INSERT INTO ingredients (name, category, in_stock) VALUES (?, ?, 0)",
                (name, category),
            )

        for r in to_add:
            cur.execute(
                """INSERT INTO recipes
                   (name, glass, instructions, image_url, cocktaildb_id, source)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    r["name"],
                    r["glass"],
                    f"{MARKER} {r['instructions']}",
                    None,                    # no image; renders with the fallback card
                    None,                    # not from TheCocktailDB
                    "manual_verified",
                ),
            )
            recipe_id = cur.lastrowid

            for sort_order, (raw_name, measure, req_type, bottle_type,
                             ing_name, notes) in enumerate(r["ingredients"]):
                cur.execute(
                    """INSERT INTO recipe_ingredients
                       (recipe_id, raw_name, raw_measure, requirement_type,
                        bottle_type, ingredient_name, notes, sort_order)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (recipe_id, raw_name, measure, req_type, bottle_type,
                     ing_name, notes, sort_order),
                )

        conn.commit()
    except Exception as exc:
        conn.rollback()
        print(f"FAILED, rolled back: {exc}")
        conn.close()
        sys.exit(1)

    after = conn.execute("SELECT COUNT(*) FROM recipes").fetchone()[0]
    after_ing = conn.execute("SELECT COUNT(*) FROM ingredients").fetchone()[0]
    n_ri = conn.execute("SELECT COUNT(*) FROM recipe_ingredients").fetchone()[0]
    print(f"Done. Recipes {before} -> {after}. Ingredients {before_ing} -> {after_ing}. "
          f"Recipe ingredients now {n_ri}.")
    conn.close()


if __name__ == "__main__":
    main()
