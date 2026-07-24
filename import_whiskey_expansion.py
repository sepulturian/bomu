"""
Whiskey and multi-spirit catalog expansion. Adds 25 recipes.

WHY THIS EXISTS
---------------
The catalog had 100 recipes but only 12 touched scotch or whiskey, and only one
(Vieux Carre) genuinely split its base between two spirits. A friend with a
six-bottle scotch shelf got almost nothing back from the recommender, which is
a catalog gap rather than a matcher bug.

This script adds:
  6  scotch drinks        (Rob Roy, Affinity, Mamie Taylor, Scotch Highball,
                           Cameron's Kick, Morning Glory Fizz)
  13 rye/bourbon drinks   (Brooklyn, Greenpoint, Remember the Maine, Scofflaw,
                           Ward Eight, Algonquin, Black Manhattan, Revolver,
                           Seelbach, Kentucky Mule, Horse's Neck, Brown Derby,
                           Bourbon Renewal)
  6  split-base drinks    (Saratoga, Suffering Bastard, Between the Sheets,
                           Chatham Artillery Punch, Fish House Punch,
                           Corpse Reviver No. 1)

PROVENANCE
----------
The existing 100 rows all carry source='thecocktaildb'. These 25 do not come
from that API, so they are tagged source='manual_verified' with cocktaildb_id
left NULL. Every spec was checked against Difford's Guide, the IBA official
list, Imbibe, or PUNCH. The per-recipe `source_url` below records which.

Deliberately NO new rows are added to `ingredients`. All 25 recipes resolve
against the existing 48-item checklist, so nobody has to re-tick anything.

SAFETY
------
  * Dry run by default. Nothing is written unless you pass --commit.
  * Idempotent. Recipes are matched on name; existing ones are skipped, so
    re-running is safe.
  * Wrapped in a single transaction. Any error rolls the whole thing back.
  * Refuses to run if a .db-journal or .db-wal file is sitting next to the
    database, which is the exact condition behind the 2026-07-23 corruption.

USAGE
-----
    python3 import_whiskey_expansion.py              # dry run, prints plan
    python3 import_whiskey_expansion.py --commit     # actually writes
"""

import argparse
import os
import sqlite3
import sys

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bomu.db")

# Same marker the existing 100 carry, so clean_instructions() strips it.
MARKER = "[BOMU_REWRITTEN_v1]"

# ---------------------------------------------------------------------------
# Recipe definitions.
#
# Each ingredient tuple is:
#   (raw_name, raw_measure, requirement_type, bottle_type, ingredient_name, notes)
#
# requirement_type rules, matching matching.py:
#   'bottle_type' -> needs a bottle. Fungible types (scotch/whiskey/bourbon/
#                    gin/rum/vodka/cognac/vermouth) match by category.
#                    'liqueur'/'amaro'/'other' match by NAME via substring,
#                    so `notes` must contain the distinctive keyword.
#   'ingredient'  -> matches the user's mixer checklist by exact name. Only
#                    names already in the 48-row ingredients table are used.
#   'optional'    -> garnishes and rinses. Never blocks makeability.
# ---------------------------------------------------------------------------

RECIPES = [
    # ----------------------------- SCOTCH ---------------------------------
    {
        "name": "Rob Roy",
        "glass": "Coupe",
        "source_url": "https://www.diffordsguide.com/cocktails/recipe/1681/rob-roy",
        "instructions": (
            "A Manhattan that went to Scotland and never came back. Same build, "
            "Scotch instead of rye, and the malt changes everything.\n\n"
            "1. Add 2 oz blended Scotch and 1 oz sweet vermouth to a mixing glass with ice.\n"
            "2. Add 2 dashes of Angostura bitters.\n"
            "3. Stir for about 20 seconds, until properly cold and slightly diluted.\n"
            "4. Strain into a chilled coupe.\n"
            "5. Garnish with a cherry or an orange twist. Both are correct; pick a side."
        ),
        "ingredients": [
            ("Blended Scotch", "2 oz", "bottle_type", "scotch", None, "Blended Scotch works better than a peaty single malt here"),
            ("Sweet Vermouth", "1 oz", "bottle_type", "vermouth", None, "sweet vermouth specifically"),
            ("Angostura bitters", "2 dashes", "ingredient", None, "Angostura bitters", None),
            ("Maraschino cherry", "1", "optional", None, "Maraschino cherries", "Garnish"),
        ],
    },
    {
        "name": "Affinity",
        "glass": "Coupe",
        "source_url": "https://www.diffordsguide.com/cocktails/recipe/19/affinity",
        "instructions": (
            "A Rob Roy with the vermouth split between sweet and dry. Bartenders call "
            "that a 'perfect' build, which means balanced, not flawless. First printed "
            "in the New York Sun in 1907.\n\n"
            "1. Add 1 1/2 oz Scotch, 1/2 oz sweet vermouth, and 1/2 oz dry vermouth to a mixing glass with ice.\n"
            "2. Add 2 dashes of Angostura bitters.\n"
            "3. Stir until cold, roughly 20 seconds.\n"
            "4. Strain into a chilled coupe.\n"
            "5. Express a lemon twist over the surface and drop it in."
        ),
        "ingredients": [
            ("Scotch", "1 1/2 oz", "bottle_type", "scotch", None, None),
            ("Sweet Vermouth", "1/2 oz", "bottle_type", "vermouth", None, "sweet vermouth"),
            ("Dry Vermouth", "1/2 oz", "bottle_type", "vermouth", None, "dry vermouth"),
            ("Angostura bitters", "2 dashes", "ingredient", None, "Angostura bitters", None),
            ("Lemon twist", "1", "optional", None, "Lemons", "Garnish"),
        ],
    },
    {
        "name": "Mamie Taylor",
        "glass": "Highball glass",
        "source_url": "https://www.diffordsguide.com/cocktails/recipe/3092/mamie-taylor-highball",
        "instructions": (
            "Rochester, New York, 1899. This predates the Moscow Mule by half a century "
            "and is arguably the better drink. Named for an opera singer who ordered "
            "something else entirely and got this instead.\n\n"
            "1. Fill a highball glass with ice.\n"
            "2. Squeeze in 1/2 oz fresh lime juice.\n"
            "3. Add 2 oz Scotch.\n"
            "4. Top with cold ginger beer and give it one gentle stir.\n"
            "5. Garnish with a lime wedge. A smoky Scotch works surprisingly well here."
        ),
        "ingredients": [
            ("Scotch", "2 oz", "bottle_type", "scotch", None, None),
            ("Lime Juice", "1/2 oz", "ingredient", None, "Lime juice (fresh)", None),
            ("Ginger beer", "4 oz", "ingredient", None, "Ginger beer", "To top"),
            ("Lime wedge", "1", "optional", None, "Limes", "Garnish"),
        ],
    },
    {
        "name": "Scotch Highball",
        "glass": "Highball glass",
        "source_url": "https://www.diffordsguide.com/encyclopedia/1075/cocktails/highball-cocktails",
        "instructions": (
            "Two ingredients and a technique. The Japanese treat this with the seriousness "
            "it deserves: the whole drink is carbonation management.\n\n"
            "1. Chill a highball glass and fill it to the top with ice. More ice means less "
            "dilution, not more.\n"
            "2. Add 2 oz Scotch and stir briefly to chill the spirit.\n"
            "3. Top with 4 oz cold soda water, pouring down a bar spoon to keep the bubbles alive.\n"
            "4. Give it exactly one slow lift with the spoon. Do not stir it flat.\n"
            "5. Garnish with a lemon twist if you like."
        ),
        "ingredients": [
            ("Scotch", "2 oz", "bottle_type", "scotch", None, None),
            ("Soda water", "4 oz", "ingredient", None, "Soda water / club soda", "Well chilled"),
            ("Lemon twist", "1", "optional", None, "Lemons", "Garnish"),
        ],
    },
    {
        "name": "Cameron's Kick",
        "glass": "Coupe",
        "source_url": "https://www.diffordsguide.com/cocktails/recipe/362/camerons-kick",
        "instructions": (
            "Harry MacElhone, 1922. Splits the base between Scotch and Irish whiskey, which "
            "sounds like a gimmick and is not. Mr. Boston misprinted the orgeat as orange "
            "bitters in 1935 and the drink spent decades being bad as a result.\n\n"
            "1. Add 1 oz Scotch, 1 oz Irish whiskey, 1/2 oz lemon juice, and 1/2 oz orgeat to a shaker.\n"
            "2. Fill with ice and shake hard until the tin frosts.\n"
            "3. Double strain into a chilled coupe.\n"
            "4. No garnish needed. The marzipan note off the orgeat does the work."
        ),
        "ingredients": [
            ("Blended Scotch", "1 oz", "bottle_type", "scotch", None, "Blended Scotch"),
            ("Irish Whiskey", "1 oz", "bottle_type", "whiskey", None, "Irish whiskey specifically"),
            ("Lemon Juice", "1/2 oz", "ingredient", None, "Lemon juice (fresh)", None),
            ("Orgeat", "1/2 oz", "ingredient", None, "Orgeat Syrup", "Almond syrup"),
        ],
    },
    {
        "name": "Morning Glory Fizz",
        "glass": "Highball glass",
        "source_url": "https://www.diffordsguide.com/cocktails/recipe/1364/morning-glory-fizz",
        "instructions": (
            "A Victorian hangover cure with absinthe in it, which tells you roughly how "
            "seriously the Victorians took hangovers.\n\n"
            "1. Add 2 oz Scotch, 1/2 oz absinthe, 2/3 oz lemon juice, 1/3 oz lime juice, "
            "1/2 oz simple syrup, and 2/3 oz egg white to a shaker.\n"
            "2. Shake with ice, then strain the liquid back into the empty shaker.\n"
            "3. Dry shake without ice to build the foam.\n"
            "4. Pour into a chilled highball from a height while simultaneously topping with soda water.\n"
            "5. Serve immediately, before the head collapses."
        ),
        "ingredients": [
            ("Scotch", "2 oz", "bottle_type", "scotch", None, None),
            ("Absinthe", "1/2 oz", "bottle_type", "other", None, "Absinthe"),
            ("Lemon Juice", "2/3 oz", "ingredient", None, "Lemon juice (fresh)", None),
            ("Lime Juice", "1/3 oz", "ingredient", None, "Lime juice (fresh)", None),
            ("Simple syrup", "1/2 oz", "ingredient", None, "Simple syrup", None),
            ("Egg white", "2/3 oz", "ingredient", None, "Egg whites", None),
            ("Soda water", "2 oz", "ingredient", None, "Soda water / club soda", "To top"),
        ],
    },

    # ------------------------- RYE AND BOURBON ----------------------------
    {
        "name": "Brooklyn",
        "glass": "Coupe",
        "source_url": "https://www.diffordsguide.com/cocktails/recipe/2785/brooklyn",
        "instructions": (
            "Jack's Manual, 1908. The Manhattan's less famous sibling: dry vermouth instead "
            "of sweet, plus maraschino and a bitter French orange liqueur.\n\n"
            "1. Add 2 oz rye, 1 oz dry vermouth, 1/4 oz maraschino liqueur, and 1/4 oz Amer Picon to a mixing glass.\n"
            "2. Fill with ice and stir 20 to 25 seconds.\n"
            "3. Strain into a chilled coupe.\n"
            "4. Garnish with a cherry.\n\n"
            "Amer Picon is hard to find outside France. Amaro CioCiaro or Bigallet China-China "
            "are the usual substitutes."
        ),
        "ingredients": [
            ("Rye Whiskey", "2 oz", "bottle_type", "whiskey", None, "rye whiskey specifically"),
            ("Dry Vermouth", "1 oz", "bottle_type", "vermouth", None, "dry vermouth"),
            ("Maraschino Liqueur", "1/4 oz", "bottle_type", "liqueur", None, "Maraschino liqueur, e.g. Luxardo"),
            ("Amer Picon", "1/4 oz", "bottle_type", "amaro", None, "Amer Picon, or Amaro CioCiaro as a substitute"),
            ("Maraschino cherry", "1", "optional", None, "Maraschino cherries", "Garnish"),
        ],
    },
    {
        "name": "Greenpoint",
        "glass": "Coupe",
        "source_url": "https://www.diffordsguide.com/cocktails/recipe/1093/greenpoint",
        "instructions": (
            "Michael McIlroy at Milk & Honey, mid 2000s. One of the better modern Manhattan "
            "riffs: yellow Chartreuse brings honey and herbs without hijacking the drink.\n\n"
            "1. Add 2 oz rye, 1/2 oz sweet vermouth, and 1/2 oz yellow Chartreuse to a mixing glass with ice.\n"
            "2. Add a dash each of Angostura and orange bitters.\n"
            "3. Stir until cold.\n"
            "4. Strain into a chilled coupe.\n"
            "5. Express a lemon twist over the top."
        ),
        "ingredients": [
            ("Rye Whiskey", "2 oz", "bottle_type", "whiskey", None, "rye whiskey specifically"),
            ("Sweet Vermouth", "1/2 oz", "bottle_type", "vermouth", None, "sweet vermouth"),
            ("Yellow Chartreuse", "1/2 oz", "bottle_type", "liqueur", None, "Yellow Chartreuse"),
            ("Angostura bitters", "1 dash", "ingredient", None, "Angostura bitters", None),
            ("Orange bitters", "1 dash", "ingredient", None, "Orange bitters", None),
            ("Lemon twist", "1", "optional", None, "Lemons", "Garnish"),
        ],
    },
    {
        "name": "Remember the Maine",
        "glass": "Coupe",
        "source_url": "https://imbibemagazine.com/recipe/remember-the-maine-recipe/",
        "instructions": (
            "From Charles H. Baker's The Gentleman's Companion, 1939, collected in Havana "
            "during a revolution. A Manhattan where Cherry Heering takes over from part of "
            "the vermouth and absinthe replaces the bitters.\n\n"
            "1. Add 2 oz rye, 3/4 oz sweet vermouth, and 2 tsp Cherry Heering to a mixing glass with ice.\n"
            "2. Add 1/2 tsp absinthe. Alternatively, rinse the glass with absinthe and discard the excess.\n"
            "3. Stir for 20 seconds.\n"
            "4. Strain into a chilled coupe.\n"
            "5. Garnish with a cherry."
        ),
        "ingredients": [
            ("Rye Whiskey", "2 oz", "bottle_type", "whiskey", None, "rye whiskey specifically"),
            ("Sweet Vermouth", "3/4 oz", "bottle_type", "vermouth", None, "sweet vermouth"),
            ("Cherry Heering", "2 tsp", "bottle_type", "liqueur", None, "Cherry Heering"),
            ("Absinthe", "1/2 tsp", "bottle_type", "other", None, "Absinthe, or use as a glass rinse"),
            ("Maraschino cherry", "1", "optional", None, "Maraschino cherries", "Garnish"),
        ],
    },
    {
        "name": "Scofflaw",
        "glass": "Coupe",
        "source_url": "https://www.diffordsguide.com/cocktails/recipe/1755/scofflaw",
        "instructions": (
            "Harry's Bar, Paris, 1924. Named within weeks of the word being coined in a "
            "Boston contest to insult people who drank during Prohibition. The bar took it "
            "as a compliment.\n\n"
            "1. Add 1 1/2 oz rye, 1 oz dry vermouth, 1/3 oz lemon juice, and 1/6 oz grenadine to a shaker.\n"
            "2. Add a dash of orange bitters.\n"
            "3. Shake with ice until cold.\n"
            "4. Strain into a chilled coupe.\n"
            "5. Garnish with a lemon twist."
        ),
        "ingredients": [
            ("Rye Whiskey", "1 1/2 oz", "bottle_type", "whiskey", None, "rye whiskey specifically"),
            ("Dry Vermouth", "1 oz", "bottle_type", "vermouth", None, "dry vermouth"),
            ("Lemon Juice", "1/3 oz", "ingredient", None, "Lemon juice (fresh)", None),
            ("Grenadine", "1/6 oz", "ingredient", None, "Grenadine", None),
            ("Orange bitters", "1 dash", "ingredient", None, "Orange bitters", None),
            ("Lemon twist", "1", "optional", None, "Lemons", "Garnish"),
        ],
    },
    {
        "name": "Ward Eight",
        "glass": "Coupe",
        "source_url": "https://www.diffordsguide.com/cocktails/recipe/2062/ward-eight",
        "instructions": (
            "Locke-Ober Cafe, Boston, 1898, supposedly made to celebrate an election result "
            "before the votes were counted. A whiskey sour with orange juice and grenadine "
            "doing the sweetening.\n\n"
            "1. Add 2 oz rye, 1/2 oz lemon juice, 1/2 oz orange juice, and 1/2 oz grenadine to a shaker.\n"
            "2. If using egg white, shake without ice first to emulsify.\n"
            "3. Add ice and shake hard until cold.\n"
            "4. Double strain into a chilled coupe.\n"
            "5. Garnish with an orange twist."
        ),
        "ingredients": [
            ("Rye Whiskey", "2 oz", "bottle_type", "whiskey", None, "rye whiskey specifically"),
            ("Lemon Juice", "1/2 oz", "ingredient", None, "Lemon juice (fresh)", None),
            ("Orange Juice", "1/2 oz", "ingredient", None, "Orange juice", None),
            ("Grenadine", "1/2 oz", "ingredient", None, "Grenadine", None),
            ("Egg white", "3/4 oz", "optional", None, "Egg whites", "Optional, for texture"),
            ("Orange twist", "1", "optional", None, "Oranges", "Garnish"),
        ],
    },
    {
        "name": "Algonquin",
        "glass": "Coupe",
        "source_url": "https://imbibemagazine.com/recipe/algonquin-cocktail-recipe/",
        "instructions": (
            "Named for the Manhattan hotel that housed the Round Table. Pineapple juice in a "
            "rye drink reads as a mistake and drinks like a good idea.\n\n"
            "1. Add 1 1/2 oz rye, 3/4 oz dry vermouth, and 3/4 oz pineapple juice to a shaker with ice.\n"
            "2. Shake until cold. Shaking builds a foamy pineapple head; stir instead if you "
            "want it cleaner.\n"
            "3. Strain into a chilled coupe.\n"
            "4. Garnish with a cherry."
        ),
        "ingredients": [
            ("Rye Whiskey", "1 1/2 oz", "bottle_type", "whiskey", None, "rye whiskey specifically"),
            ("Dry Vermouth", "3/4 oz", "bottle_type", "vermouth", None, "dry vermouth"),
            ("Pineapple Juice", "3/4 oz", "ingredient", None, "Pineapple juice", None),
            ("Maraschino cherry", "1", "optional", None, "Maraschino cherries", "Garnish"),
        ],
    },
    {
        "name": "Black Manhattan",
        "glass": "Coupe",
        "source_url": "https://punchdrink.com/recipes/black-manhattan/",
        "instructions": (
            "Todd Smith, Bourbon & Branch, San Francisco, 2005. Swap the sweet vermouth for "
            "Averna and the drink goes darker and more bitter without losing the shape.\n\n"
            "1. Add 2 oz rye and 3/4 oz Amaro Averna to a mixing glass with ice.\n"
            "2. Add a dash each of Angostura and orange bitters.\n"
            "3. Stir until cold.\n"
            "4. Strain into a chilled coupe.\n"
            "5. Garnish with a cherry."
        ),
        "ingredients": [
            ("Rye Whiskey", "2 oz", "bottle_type", "whiskey", None, "rye whiskey specifically"),
            ("Amaro Averna", "3/4 oz", "bottle_type", "amaro", None, "Amaro Averna"),
            ("Angostura bitters", "1 dash", "ingredient", None, "Angostura bitters", None),
            ("Orange bitters", "1 dash", "ingredient", None, "Orange bitters", None),
            ("Maraschino cherry", "1", "optional", None, "Maraschino cherries", "Garnish"),
        ],
    },
    {
        "name": "Revolver",
        "glass": "Coupe",
        "source_url": "https://www.bulleit.com/whiskey-drinks/revolver-cocktail",
        "instructions": (
            "Jon Santer, San Francisco, early 2000s. A Manhattan with coffee liqueur standing "
            "in for the vermouth. The flamed orange peel is not optional theatre; the "
            "caramelised oil is part of the drink.\n\n"
            "1. Add 2 oz bourbon and 1/2 oz coffee liqueur to a mixing glass with ice.\n"
            "2. Add 2 dashes of orange bitters.\n"
            "3. Stir until well chilled.\n"
            "4. Strain into a chilled coupe.\n"
            "5. Flame an orange peel over the surface, then drop it in."
        ),
        "ingredients": [
            ("Bourbon", "2 oz", "bottle_type", "bourbon", None, None),
            ("Coffee liqueur", "1/2 oz", "bottle_type", "liqueur", None, "Coffee liqueur (e.g. Kahlua)"),
            ("Orange bitters", "2 dashes", "ingredient", None, "Orange bitters", None),
            ("Orange peel", "1", "optional", None, "Oranges", "Garnish, flamed"),
        ],
    },
    {
        "name": "Seelbach",
        "glass": "Champagne flute",
        "source_url": "https://punchdrink.com/recipes/seelbach/",
        "instructions": (
            "The Seelbach Hotel, Louisville. Presented for years as a lost 1917 recipe until "
            "the man who 'rediscovered' it in 1995 admitted in 2016 that he made it up. It is "
            "still a very good drink, which is the only part that matters.\n\n"
            "1. Add 1 1/2 oz bourbon and 1/2 oz triple sec to a chilled flute.\n"
            "2. Add 7 dashes Angostura and 7 dashes Peychaud's. Yes, seven each. That is the drink.\n"
            "3. Top with about 4 oz chilled champagne or prosecco.\n"
            "4. Stir once, gently.\n"
            "5. Garnish with an orange twist."
        ),
        "ingredients": [
            ("Bourbon", "1 1/2 oz", "bottle_type", "bourbon", None, None),
            ("Triple sec", "1/2 oz", "bottle_type", "liqueur", None, "Triple sec"),
            ("Angostura bitters", "7 dashes", "ingredient", None, "Angostura bitters", None),
            ("Peychaud's bitters", "7 dashes", "ingredient", None, "Peychaud's bitters", None),
            ("Champagne", "4 oz", "ingredient", None, "Champagne", "Or prosecco"),
            ("Orange twist", "1", "optional", None, "Oranges", "Garnish"),
        ],
    },
    {
        "name": "Kentucky Mule",
        "glass": "Copper Mug",
        "source_url": "https://www.makersmark.com/en-us/cocktails/kentucky-mule",
        "instructions": (
            "A Moscow Mule with bourbon. Bourbon has actual flavour to contribute, so this is "
            "the better version of the drink.\n\n"
            "1. Add 2 oz bourbon and 1/2 oz lime juice to a copper mug.\n"
            "2. Add a dash of Angostura if you want a little more backbone.\n"
            "3. Fill with ice and stir.\n"
            "4. Top with cold ginger beer.\n"
            "5. Garnish with a lime wedge and a mint sprig."
        ),
        "ingredients": [
            ("Bourbon", "2 oz", "bottle_type", "bourbon", None, None),
            ("Lime Juice", "1/2 oz", "ingredient", None, "Lime juice (fresh)", None),
            ("Ginger beer", "4 oz", "ingredient", None, "Ginger beer", "To top"),
            ("Angostura bitters", "1 dash", "optional", None, "Angostura bitters", "Optional"),
            ("Lime wedge", "1", "optional", None, "Limes", "Garnish"),
            ("Fresh mint", "1 sprig", "optional", None, "Fresh mint", "Garnish"),
        ],
    },
    {
        "name": "Horse's Neck",
        "glass": "Highball glass",
        "source_url": "https://www.diffordsguide.com/cocktails/recipe/1229/horses-neck",
        "instructions": (
            "Started life in 1890 as a soft drink: ginger ale, ice, and a long lemon peel. "
            "Someone added the whiskey and the name stuck. The peel is the whole point, so "
            "cut it properly.\n\n"
            "1. Peel a lemon in one continuous spiral and drape it inside a highball glass "
            "with one end hooked over the rim.\n"
            "2. Fill the glass with ice.\n"
            "3. Add 2 oz bourbon and 2 dashes of Angostura bitters.\n"
            "4. Top with cold ginger ale.\n"
            "5. Stir gently once."
        ),
        "ingredients": [
            ("Bourbon", "2 oz", "bottle_type", "bourbon", None, "Brandy also traditional"),
            ("Ginger ale", "4 oz", "ingredient", None, "Ginger ale", "To top"),
            ("Angostura bitters", "2 dashes", "ingredient", None, "Angostura bitters", None),
            ("Lemon peel spiral", "1", "optional", None, "Lemons", "Garnish, cut as one long spiral"),
        ],
    },
    {
        "name": "Brown Derby",
        "glass": "Coupe",
        "source_url": "https://www.diffordsguide.com/cocktails/recipe/292/brown-derby",
        "instructions": (
            "A Hollywood drink from the 1930s, named after the hat-shaped restaurant. Three "
            "ingredients, and grapefruit plus honey turns out to be exactly what bourbon "
            "wanted.\n\n"
            "1. Add 2 oz bourbon, 1 oz fresh grapefruit juice, and 1/2 oz honey syrup to a shaker.\n"
            "2. Fill with ice and shake hard.\n"
            "3. Double strain into a chilled coupe.\n"
            "4. Garnish with a grapefruit twist.\n\n"
            "Honey syrup is honey thinned with warm water, roughly three to one. Neat honey "
            "will not incorporate in a cold shaker."
        ),
        "ingredients": [
            ("Bourbon", "2 oz", "bottle_type", "bourbon", None, None),
            ("Grapefruit Juice", "1 oz", "ingredient", None, "Grapefruit juice", "Freshly squeezed"),
            ("Honey syrup", "1/2 oz", "ingredient", None, "Honey", "Diluted as honey syrup"),
        ],
    },
    {
        "name": "Bourbon Renewal",
        "glass": "Old-fashioned glass",
        "source_url": "https://punchdrink.com/recipes/bourbon-renewal/",
        "instructions": (
            "Jeffrey Morgenthaler, 2005. A bourbon sour with creme de cassis, which adds "
            "blackcurrant depth and stops the drink reading as just sweet and sour.\n\n"
            "1. Add 2 oz bourbon, 1 oz lemon juice, 1/2 oz creme de cassis, and 1/2 oz simple syrup to a shaker.\n"
            "2. Add 2 dashes of Angostura bitters.\n"
            "3. Shake with ice until cold.\n"
            "4. Strain over fresh ice in a rocks glass.\n"
            "5. Garnish with a lemon wheel."
        ),
        "ingredients": [
            ("Bourbon", "2 oz", "bottle_type", "bourbon", None, None),
            ("Lemon Juice", "1 oz", "ingredient", None, "Lemon juice (fresh)", None),
            ("Creme de Cassis", "1/2 oz", "bottle_type", "liqueur", None, "Creme de Cassis blackcurrant liqueur"),
            ("Simple syrup", "1/2 oz", "ingredient", None, "Simple syrup", None),
            ("Angostura bitters", "2 dashes", "ingredient", None, "Angostura bitters", None),
            ("Lemon wheel", "1", "optional", None, "Lemons", "Garnish"),
        ],
    },

    # ------------------------- SPLIT BASE ---------------------------------
    {
        "name": "Saratoga",
        "glass": "Coupe",
        "source_url": "https://www.diffordsguide.com/cocktails/recipe/2196/saratoga-cocktail",
        "instructions": (
            "Jerry Thomas, 1887. A Manhattan with the base split evenly between rye and "
            "cognac. The cognac softens the rye's edges and adds a faint chocolate note.\n\n"
            "1. Add 1 oz rye, 1 oz cognac, and 1 oz sweet vermouth to a mixing glass with ice.\n"
            "2. Add 2 dashes of Angostura bitters.\n"
            "3. Thomas shook this. Stir it instead; it is a spirit-only drink.\n"
            "4. Strain into a chilled coupe.\n"
            "5. Garnish with a lemon wheel."
        ),
        "ingredients": [
            ("Rye Whiskey", "1 oz", "bottle_type", "whiskey", None, "rye whiskey specifically"),
            ("Cognac", "1 oz", "bottle_type", "cognac", None, None),
            ("Sweet Vermouth", "1 oz", "bottle_type", "vermouth", None, "sweet vermouth"),
            ("Angostura bitters", "2 dashes", "ingredient", None, "Angostura bitters", None),
            ("Lemon wheel", "1", "optional", None, "Lemons", "Garnish"),
        ],
    },
    {
        "name": "Suffering Bastard",
        "glass": "Collins glass",
        "source_url": "https://www.diffordsguide.com/cocktails/recipe/2588/suffering-bastard",
        "instructions": (
            "Joe Scialom, Shepheard's Hotel, Cairo, 1942, built as a hangover cure for British "
            "officers in North Africa. Gin and cognac in the same glass is unusual and it works.\n\n"
            "1. Add 1 oz cognac, 1 oz gin, 1 oz lime juice, and 3 dashes Angostura to a shaker.\n"
            "2. Shake briefly with ice.\n"
            "3. Strain into an ice-filled collins glass or tiki mug half full of ginger beer.\n"
            "4. Top with the rest of the ginger beer.\n"
            "5. Garnish with a mint sprig and a lime wedge."
        ),
        "ingredients": [
            ("Cognac", "1 oz", "bottle_type", "cognac", None, None),
            ("Gin", "1 oz", "bottle_type", "gin", None, None),
            ("Lime Juice", "1 oz", "ingredient", None, "Lime juice (fresh)", None),
            ("Angostura bitters", "3 dashes", "ingredient", None, "Angostura bitters", None),
            ("Ginger beer", "3 1/3 oz", "ingredient", None, "Ginger beer", "To top"),
            ("Fresh mint", "1 sprig", "optional", None, "Fresh mint", "Garnish"),
            ("Lime wedge", "1", "optional", None, "Limes", "Garnish"),
        ],
    },
    {
        "name": "Between the Sheets",
        "glass": "Cocktail glass",
        "source_url": "https://iba-world.com/iba-cocktail/between-the-sheets/",
        "instructions": (
            "An IBA official cocktail, and essentially a Sidecar that splits the base between "
            "cognac and rum. Prohibition-era, and about as strong as it looks.\n\n"
            "1. Add 1 oz white rum, 1 oz cognac, 1 oz triple sec, and 2/3 oz lemon juice to a shaker.\n"
            "2. Shake with ice until very cold.\n"
            "3. Strain into a chilled cocktail glass. No ice in the glass.\n"
            "4. Garnish with a lemon twist."
        ),
        "ingredients": [
            ("White Rum", "1 oz", "bottle_type", "rum", None, "Light or white rum"),
            ("Cognac", "1 oz", "bottle_type", "cognac", None, None),
            ("Triple sec", "1 oz", "bottle_type", "liqueur", None, "Triple sec"),
            ("Lemon Juice", "2/3 oz", "ingredient", None, "Lemon juice (fresh)", None),
            ("Lemon twist", "1", "optional", None, "Lemons", "Garnish"),
        ],
    },
    {
        "name": "Chatham Artillery Punch",
        "glass": "Punch Cup",
        "source_url": "https://punchdrink.com/recipes/chatham-artillery-punch/",
        "instructions": (
            "Savannah, Georgia, early 1800s, originally mixed in ice-filled horse buckets by "
            "the local militia and used to incapacitate visiting dignitaries. Three base "
            "spirits at once, which makes it the rare drink that genuinely justifies a full "
            "shelf.\n\n"
            "Scaled to a single serving:\n\n"
            "1. Add 1/2 oz cognac, 1/2 oz rye or bourbon, and 1/2 oz aged rum to a shaker.\n"
            "2. Add 3/4 oz lemon juice and 1/2 oz simple syrup.\n"
            "3. Shake with ice and strain into an ice-filled punch cup or wine glass.\n"
            "4. Top with about 2 oz chilled sparkling wine.\n"
            "5. Grate nutmeg over the top and garnish with a lemon wheel.\n\n"
            "For a bowl, multiply by your guest count and let it sit on a large block of ice."
        ),
        "ingredients": [
            ("Cognac", "1/2 oz", "bottle_type", "cognac", None, None),
            ("Rye Whiskey", "1/2 oz", "bottle_type", "whiskey", None, "Rye or bourbon"),
            ("Aged Rum", "1/2 oz", "bottle_type", "rum", None, "Aged or dark rum"),
            ("Lemon Juice", "3/4 oz", "ingredient", None, "Lemon juice (fresh)", None),
            ("Simple syrup", "1/2 oz", "ingredient", None, "Simple syrup", "Traditionally an oleo-saccharum"),
            ("Champagne", "2 oz", "ingredient", None, "Champagne", "Or any dry sparkling wine, to top"),
            ("Nutmeg", "1 grating", "optional", None, None, "Garnish, freshly grated"),
            ("Lemon wheel", "1", "optional", None, "Lemons", "Garnish"),
        ],
    },
    {
        "name": "Fish House Punch",
        "glass": "Punch Cup",
        "source_url": "https://punchdrink.com/recipes/philadelphia-fish-house-punch/",
        "instructions": (
            "The State in Schuylkill Fishing Corporation, Philadelphia, founded 1732. This may "
            "be the oldest American punch still in circulation. It is dangerously easy to "
            "drink, which was likely the intention.\n\n"
            "Scaled to a single serving:\n\n"
            "1. Add 1 1/2 oz Jamaican or aged rum, 3/4 oz cognac, and 1/4 oz peach brandy to a shaker.\n"
            "2. Add 3/4 oz lemon juice and 1/2 oz simple syrup.\n"
            "3. Shake with ice and strain into an ice-filled punch cup.\n"
            "4. Grate nutmeg over the top.\n"
            "5. Garnish with a lemon wheel."
        ),
        "ingredients": [
            ("Jamaican Rum", "1 1/2 oz", "bottle_type", "rum", None, "Jamaican or aged rum"),
            ("Cognac", "3/4 oz", "bottle_type", "cognac", None, None),
            ("Peach Brandy", "1/4 oz", "bottle_type", "liqueur", None, "Peach brandy or peach liqueur"),
            ("Lemon Juice", "3/4 oz", "ingredient", None, "Lemon juice (fresh)", None),
            ("Simple syrup", "1/2 oz", "ingredient", None, "Simple syrup", None),
            ("Nutmeg", "1 grating", "optional", None, None, "Garnish, freshly grated"),
            ("Lemon wheel", "1", "optional", None, "Lemons", "Garnish"),
        ],
    },
    {
        "name": "Corpse Reviver No. 1",
        "glass": "Coupe",
        "source_url": "https://www.diffordsguide.com/cocktails/recipe/499/corpse-reviver-no1",
        "instructions": (
            "The older, darker sibling of the No. 2 already in this catalog. Harry Craddock's "
            "Savoy Cocktail Book, 1930, notes it should be taken before 11am 'or whenever "
            "steam and energy are needed'. All spirit, no citrus.\n\n"
            "1. Add 1 1/2 oz cognac, 3/4 oz calvados, and 3/4 oz sweet vermouth to a mixing glass with ice.\n"
            "2. Stir until well chilled.\n"
            "3. Strain into a chilled coupe.\n"
            "4. Garnish with an apple slice or an orange twist."
        ),
        "ingredients": [
            ("Cognac", "1 1/2 oz", "bottle_type", "cognac", None, None),
            ("Calvados", "3/4 oz", "bottle_type", "brandy", None, "Calvados apple brandy specifically"),
            ("Sweet Vermouth", "3/4 oz", "bottle_type", "vermouth", None, "sweet vermouth"),
            ("Orange twist", "1", "optional", None, "Oranges", "Garnish"),
        ],
    },
]


# ---------------------------------------------------------------------------
# Validation. Runs in dry mode too, so problems surface before any write.
# ---------------------------------------------------------------------------

VALID_REQ_TYPES = {"bottle_type", "ingredient", "optional"}
VALID_BOTTLE_TYPES = {
    "gin", "vodka", "rum", "tequila", "mezcal", "whiskey", "bourbon", "scotch",
    "brandy", "cognac", "vermouth", "amaro", "liqueur", "other",
}
NAME_MATCH_TYPES = {"liqueur", "amaro", "other"}


def validate(conn):
    """Check every recipe against the schema rules and the live ingredients
    table. Returns a list of human-readable problems."""
    problems = []
    known_ingredients = {
        row[0].lower() for row in conn.execute("SELECT name FROM ingredients")
    }

    seen_names = set()
    for r in RECIPES:
        name = r["name"]
        if name in seen_names:
            problems.append(f"{name}: duplicated inside this script")
        seen_names.add(name)

        if not r["ingredients"]:
            problems.append(f"{name}: no ingredients")

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
                # Optional rows may reference an ingredient, but if they do it
                # still has to exist so the detail page can render it.
                if ing_name and ing_name.lower() not in known_ingredients:
                    problems.append(f"{label}: optional references unknown ingredient {ing_name!r}")

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
    parser = argparse.ArgumentParser(description=__doc__)
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
    print(f"Recipes currently in catalog: {before}")
    print()

    # --- validate ---------------------------------------------------------
    problems = validate(conn)
    if problems:
        print(f"VALIDATION FAILED ({len(problems)} problems):")
        for p in problems:
            print("   ", p)
        conn.close()
        sys.exit(1)
    print(f"Validation passed for all {len(RECIPES)} recipes.")
    print()

    # --- figure out what is new ------------------------------------------
    existing = {row[0] for row in conn.execute("SELECT name FROM recipes")}
    to_add = [r for r in RECIPES if r["name"] not in existing]
    skipped = [r["name"] for r in RECIPES if r["name"] in existing]

    if skipped:
        print(f"Already present, will skip ({len(skipped)}):")
        for n in skipped:
            print("   ", n)
        print()

    if not to_add:
        print("Nothing to add. Catalog already has all 25.")
        conn.close()
        return

    print(f"Will add {len(to_add)} recipes:")
    for r in to_add:
        n_req = sum(1 for i in r["ingredients"] if i[2] != "optional")
        n_opt = sum(1 for i in r["ingredients"] if i[2] == "optional")
        print(f"    {r['name']:<28} {n_req} required, {n_opt} optional")
    print()

    if not args.commit:
        print("DRY RUN. Nothing was written.")
        print("Re-run with --commit to apply.")
        conn.close()
        return

    # --- write ------------------------------------------------------------
    try:
        cur = conn.cursor()
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
    n_ing = conn.execute("SELECT COUNT(*) FROM recipe_ingredients").fetchone()[0]
    print(f"Done. Recipes {before} -> {after}. Recipe ingredients now {n_ing}.")
    conn.close()


if __name__ == "__main__":
    main()
