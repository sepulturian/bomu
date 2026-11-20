# -*- coding: utf-8 -*-
"""
"Make it your own" copy: genuine optional bartender riffs and upgrades
for recipes that benefit from one. Loaded by migrate_enhancements.py,
which writes it into the `recipe_enhancements` table.

WHY THIS IS NOT IN recipe_ingredients
-------------------------------------
`recipe_ingredients` holds the recipe itself (and its standard optional garnishes,
which sit in the Pour list with an `optional` badge and never affect makeability).
`recipe_enhancements` holds optional bartender twists and riffs that change or
dress up the drink beyond its standard build.

The matcher never reads this table. Nothing in here can change what anybody can
make, which is both the design and the way the migration is verified.

RULES THIS FILE FOLLOWS
-----------------------
1. Nothing is invented, and the reader is always told which kind of claim they
   are reading. Every entry carries a `source`:
       a named source   "Difford's Guide", "IBA official specification", etc.
       PRACTICE         "Common bar practice, not a printed spec" (renders as
                        "Bartender's habit" on the recipe page).
2. Scope is genuine optional riffs, bitters, and garnish upgrades only. Standard
   classic garnishes belong in `recipe_ingredients` (`requirement_type = 'optional'`).
   Never anti-riffs, core techniques already in the steps/tip, or ingredients
   already shown in `recipe_ingredients`.
3. Every `ingredient` key must already exist in the `ingredients` checklist table
   (49 rows) and must NOT duplicate anything in that recipe's `recipe_ingredients`.
4. Plain English for someone at home: 1 to 2 natural sentences saying what to
   add and why it works. No em-dashes, no menu fluff, and no source names inside `note`.

FIELD REFERENCE
---------------
name        Shown in bold. Written as a concrete garnish or addition.
ingredient  Exact key into `ingredients` checklist table, or None. Drives the
            "In your bar" / "Needs X" tag.
measure     Optional, right-aligned ("1 dash", "1 wide strip", etc.).
note        What to do and why it works in the drink.
source      Named publication/spec, or PRACTICE.
"""

PRACTICE = "Common bar practice, not a printed spec"

ENHANCEMENTS = {

# ============================ Bitters & Flavor Riffs =======================

"Manhattan": [
    {
        "name": "Orange bitters",
        "ingredient": "Orange bitters",
        "measure": "1 dash",
        "note": "Swap one dash of the Angostura for orange bitters, or use a dash "
                "of each. It pulls a warm citrus-and-spice note out of the sweet "
                "vermouth without making the glass any sweeter.",
        "source": "Difford's Guide; The PDT Cocktail Book",
    },
],

"Old Fashioned": [
    {
        "name": "Orange bitters",
        "ingredient": "Orange bitters",
        "measure": "1 dash",
        "note": "Add a dash alongside the Angostura instead of replacing it. "
                "It ties the bourbon to the orange peel on top so you taste "
                "citrus all the way to the bottom of the glass.",
        "source": "Difford's Guide",
    },
],

"Martinez": [
    {
        "name": "Orange bitters",
        "ingredient": "Orange bitters",
        "measure": "1 dash",
        "note": "Nineteenth-century Martinez recipes called for an old Dutch orange "
                "bitters that disappeared for decades. A dash of modern orange "
                "bitters gets you right back to that spiced citrus finish.",
        "source": "Difford's Guide",
    },
],

"Negroni": [
    {
        "name": "Orange bitters",
        "ingredient": "Orange bitters",
        "measure": "1 dash",
        "note": "Not part of the classic three-bottle build, though plenty of "
                "bartenders sneak a dash in before stirring. It puts dry orange "
                "spice inside the drink itself, not just on the nose.",
        "source": PRACTICE,
    },
],

"Gin And Tonic": [
    {
        "name": "Angostura, for a Pink Gin and Tonic",
        "ingredient": "Angostura bitters",
        "measure": "2 dashes",
        "note": "Dash Angostura over the ice before pouring the tonic. It turns "
                "the glass pale pink and adds a dry clove-and-cinnamon bite that "
                "makes a Tuesday-night G&T feel like a proper cocktail.",
        "source": PRACTICE,
    },
],

"Ramos Gin Fizz": [
    {
        "name": "Orange flower water on the foam",
        "ingredient": None,
        "measure": "1 drop",
        "note": "If you actually have orange flower water in the cupboard, put one "
                "drop directly on top of the foam head at the end so the floral "
                "aroma hits before every sip.",
        "source": "Difford's Guide",
    },
],

# ============================ Citrus & Peel Swaps ==========================

"Rosita": [
    {
        "name": "Orange twist instead of lemon",
        "ingredient": "Oranges",
        "measure": "1 strip",
        "note": "The printed recipe calls for a lemon twist, which keeps the "
                "finish sharp. If you want a rounder, warmer aroma over the "
                "Campari and tequila, express an orange peel instead.",
        "source": PRACTICE,
    },
],

"Black Russian": [
    {
        "name": "Orange twist",
        "ingredient": "Oranges",
        "measure": "1 strip",
        "note": "Normally served bare over ice, but coffee and orange are old "
                "friends. Squeezing a strip of orange peel over the glass gives "
                "it an espresso-and-zest aroma that wakes the whole drink up.",
        "source": PRACTICE,
    },
],

"French Connection": [
    {
        "name": "Orange twist",
        "ingredient": "Oranges",
        "measure": "1 strip",
        "note": "Cognac and amaretto over ice can lean pretty sweet after a few "
                "sips. Expressing a fresh orange peel over the top cuts through "
                "the almond sugar with bitter citrus oil.",
        "source": PRACTICE,
    },
],

"Godfather": [
    {
        "name": "Orange twist",
        "ingredient": "Oranges",
        "measure": "1 strip",
        "note": "Squeeze a strip of orange peel over the rocks and drop it in. "
                "Fresh orange oil bridges the gap between smoky Scotch and sweet "
                "amaretto.",
        "source": PRACTICE,
    },
],

"Harvard": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "Cognac and sweet vermouth are softer and rounder than a rye "
                "Manhattan. Squeezing a strip of lemon peel over the glass gives "
                "the finish a sharper edge.",
        "source": PRACTICE,
    },
],

"Brandy Daisy": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "Pomegranate grenadine makes a Daisy rounder than a regular sour. "
                "Giving a strip of lemon peel a quick twist over the glass puts "
                "fresh lemon oil right back on top.",
        "source": PRACTICE,
    },
],

"Algonquin": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "Express a strip of lemon peel over the coupe before serving. It "
                "leans into the dry rye and vermouth and keeps the pineapple "
                "from smelling like a beach drink.",
        "source": PRACTICE,
    },
],

"Airmail": [
    {
        "name": "Lime twist",
        "ingredient": "Limes",
        "measure": "1 strip",
        "note": "If you don't have fresh mint on hand, twist a strip of lime peel "
                "over the flute instead so the rising Champagne bubbles carry "
                "fresh lime oil to the rim.",
        "source": PRACTICE,
    },
],

"Cosmopolitan": [
    {
        "name": "Flamed orange twist",
        "ingredient": "Oranges",
        "measure": "1 strip",
        "note": "Hold a wide strip of orange peel near a lit match and pinch it "
                "so the oils spark across the drink. That toasted orange aroma "
                "is Toby Cecchini's original 1988 finishing touch.",
        "source": "Difford's Guide",
    },
],

# ============================ Rims, Spices & Finishing Touches =============

"Ward Eight": [
    {
        "name": "Brandied cherry",
        "ingredient": "Maraschino cherries",
        "measure": "1",
        "note": "Drop a dark brandied cherry into the glass alongside the orange "
                "twist. It plays right into the pomegranate grenadine and gives "
                "you a boozy reward at the bottom.",
        "source": PRACTICE,
    },
],

"Bloody Mary": [
    {
        "name": "Celery salt rim",
        "ingredient": "Salt",
        "measure": None,
        "note": "Rub a cut lime around half the rim and roll it in celery salt "
                "before pouring. You get a savoury hit on the lips without "
                "making the tomato mix itself too salty.",
        "source": "IBA official specification",
    },
    {
        "name": "Black pepper on top",
        "ingredient": "Pepper",
        "measure": "a good grind",
        "note": "Crack fresh black pepper directly across the ice at the very "
                "end so the pepper hits your nose on the first sip instead of "
                "disappearing into the tomato juice.",
        "source": "IBA official specification",
    },
],

"Mexican Mule": [
    {
        "name": "Mint sprig",
        "ingredient": "Fresh mint",
        "measure": "1 sprig",
        "note": "Give a sprig of fresh mint a gentle slap against your palm and "
                "tuck it in beside the lime wedge. Mint, ginger beer, and blanco "
                "tequila smell fantastic together.",
        "source": PRACTICE,
    },
],

"Planter's Punch": [
    {
        "name": "Grated nutmeg",
        "ingredient": None,
        "measure": "a light grating",
        "note": "Grate fresh nutmeg across the top of the ice right before "
                "serving. Dry spice over dark rum and citrus is an old Caribbean "
                "signature that makes the whole glass smell warmer.",
        "source": "Difford's Guide",
    },
],

"Grasshopper": [
    {
        "name": "Grated dark chocolate",
        "ingredient": None,
        "measure": "a light shaving",
        "note": "Run a microplane or vegetable peeler across a square of dark "
                "chocolate over the coupe. Bittersweet cocoa shavings cut the "
                "sweet mint cream and look great on the pale green top.",
        "source": PRACTICE,
    },
],

"Irish Coffee": [
    {
        "name": "Grated nutmeg",
        "ingredient": None,
        "measure": "a light grating",
        "note": "San Francisco's Buena Vista serves their cream collar bare, "
                "while plenty of Irish pubs grate fresh nutmeg over the top. "
                "Try a pinch on the cream once and see which camp you're in.",
        "source": "Difford's Guide (listed as an optional garnish)",
    },
],

"Oreo Mudslide": [
    {
        "name": "Crushed Oreo rim",
        "ingredient": None,
        "measure": None,
        "note": "Dip the rim of the glass in chocolate syrup and roll it in "
                "crushed Oreo crumbs before pouring. If you're already blending "
                "ice cream and cookies with vodka, you might as well commit.",
        "source": PRACTICE,
    },
],

"Toasted Almond": [
    {
        "name": "Grated nutmeg",
        "ingredient": None,
        "measure": "a light grating",
        "note": "Amaretto, coffee liqueur, and cream are rich and sweet on their "
                "own. A quick grating of fresh nutmeg on top adds a dry, woody "
                "aroma that suits the roasted almond.",
        "source": PRACTICE,
    },
],

}
