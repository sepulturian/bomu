# -*- coding: utf-8 -*-
"""
"Make it your own" copy: documented optional additions for recipes that have
one. Loaded by migrate_enhancements.py, which writes it into the
`recipe_enhancements` table.

WHY THIS IS NOT IN recipe_ingredients
-------------------------------------
On 2026-07-26 twelve orphaned bitters rows were found sitting in
`recipe_ingredients` with nothing in the method mentioning them. Six were kept
because they are genuinely part of the drink; seven were removed because they
were plausible-sounding and not part of it. That cleanup drew a line between
"this is the recipe" and "this is a thing you could also do", and putting
suggestions back into the same table would rub the line out again.

The matcher never reads this table. Nothing in here can change what anybody can
make, which is both the design and the way the migration is verified.

RULES THIS FILE FOLLOWS
-----------------------
1. Nothing is invented, and the reader is always told which kind of claim they
   are reading. Every entry carries a `source`, and the source is rendered on
   the page. Two kinds are allowed:

       a named source   "Difford's Guide", "IBA official specification",
                        a book, a named bartender. The variation is printed
                        somewhere and can be looked up.
       PRACTICE         standard behind a bar, not in any spec this was
                        checked against. Renders as "Common bar practice, not
                        a printed spec" so nobody mistakes it for a citation.

   What is NOT allowed is an entry with no source at all, or a PRACTICE entry
   dressed up as a citation. This app has a history of being confidently wrong
   (the Grape Soda label, the Vodka Cruiser tagged as vodka) and a plausible
   invented suggestion is indistinguishable from a real one to the reader. The
   distinction being visible on the page is what makes the looser bar safe.

2. Scope is bitters and garnish upgrades only. Rinses, floats, saline and egg
   white are out: they change the drink rather than finishing it, and a
   suggestion that changes the drink belongs in the catalog as its own recipe.

3. An enhancement must not duplicate something the recipe already shows, in
   either the required or the optional rows. The migration enforces this
   against the live database rather than trusting the list below, because the
   local bomu.db is a stale 100-recipe copy and cannot be trusted about what a
   live recipe contains. Where the ingredient is already on the page but the
   TECHNIQUE is the point, the entry keeps its note and drops its `ingredient`
   link.

4. Plenty of recipes still get nothing. Silence is a valid answer and a
   suggestion that says nothing is worse than no suggestion. Same precedent as
   the 46 recipes with no tip.

5. Written for someone at home, not behind a bar (rewritten 2026-11-15). Two
   plain sentences: what to do, then why. No source names in the note (no
   "Difford's", "IBA", "the build"), no unexplained bar words ("express",
   "pith", "muddle", "slap", "float" as a noun, "serve" as a noun), no
   bartender names a reader can't place. The page shows the source only as a
   tag: "By the book" for a named source, "Bartender's habit" for PRACTICE.
   Simplifying must not add a claim the source didn't make.

ON THE NEGRONI
--------------
It gets orange bitters, marked PRACTICE. Difford's Negroni is three ingredients
and no bitters, and the orange-bitters versions (Kingston Negroni, Sweet Orange
Negroni) are separate named drinks -- so this is not a citation and is not
presented as one. It is on the page because it is what people actually do, and
the source line says exactly that.

FIELD REFERENCE
---------------
name        Shown in bold. Written as a thing you add, not a category.
ingredient  Exact key into the `ingredients` checklist table, or None. Drives
            the "in your stock" line. MUST already exist -- adding a checklist
            row is a real cost, it starts unticked for every existing user.
measure     Optional, right-aligned. "2 dashes", "1 wide strip".
note        Why you would bother, and what it changes. One or two sentences.
source      Where the variation is documented, or PRACTICE.
"""

# Rendered verbatim under an entry. Deliberately wordy: "Common bar practice"
# alone reads like a citation at a glance, and the whole point of the looser
# bar is that the reader can tell the difference without thinking about it.
PRACTICE = "Common bar practice, not a printed spec"

ENHANCEMENTS = {

# ============================ Bitters ======================================

"Manhattan": [
    {
        "name": "Orange bitters",
        "ingredient": "Orange bitters",
        "measure": "1 dash",
        "note": "Use it in place of one Angostura dash, or alongside it. "
                "It brightens the vermouth without making the drink any "
                "sweeter.",
        "source": "Difford's Guide; The PDT Cocktail Book",
    },
    {
        "name": "Brandied or maraschino cherry",
        # Already an optional row in the ingredient list. This entry
        # survives as a TECHNIQUE note only -- no checklist link, or it
        # would show twice on one page under two headings.
        "ingredient": None,
        "measure": None,
        "note": "The traditional garnish, and the syrup it gives off "
                "changes the last sip. A dark brandied cherry does this "
                "far better than a neon red one.",
        "source": "IBA official specification",
    },
],

"Old Fashioned": [
    {
        "name": "Orange bitters",
        "ingredient": "Orange bitters",
        "measure": "1 dash",
        "note": "Add it alongside the Angostura, not instead of it. It "
                "picks up the orange peel so the citrus tastes like part "
                "of the drink.",
        "source": "Difford's Guide",
    },
    {
        "name": "Orange peel, squeezed over",
        "ingredient": "Oranges",
        "measure": "1 wide strip",
        "note": "Squeeze a wide strip of peel over the drink so the oil "
                "sprays the top, then drop it in. Don't mash orange into "
                "the glass, which turns it bitter and cloudy.",
        "source": "IBA official specification; Difford's Guide",
    },
],

"Martinez 2": [
    {
        "name": "Orange bitters",
        "ingredient": "Orange bitters",
        "measure": "1 dash",
        "note": "The original used a brand of bitters that disappeared "
                "for most of the 1900s. Orange bitters is the usual "
                "stand-in today.",
        "source": "Difford's Guide",
    },
],

"Adonis": [
    {
        "name": "Orange bitters",
        "ingredient": "Orange bitters",
        "measure": "2 dashes",
        "note": "With no spirit in it, the sherry and vermouth can blur "
                "together. The bitters give the drink the edge it "
                "otherwise lacks.",
        "source": "Difford's Guide",
    },
],

"Champagne Cocktail": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "Squeeze it over the top and drop it in. The lemon oil "
                "stops the sugar cube from making the drink taste sweet.",
        "source": "IBA official specification",
    },
],

# ============================ Garnish upgrades =============================

"Negroni": [
    {
        "name": "Orange bitters",
        "ingredient": "Orange bitters",
        "measure": "1 dash",
        "note": "Not part of the classic recipe, but plenty of bartenders"
                " add it. It picks up the orange peel and softens the "
                "Campari without making it sweeter.",
        "source": PRACTICE,
    },
    {
        "name": "Orange twist or slice",
        "ingredient": "Oranges",
        "measure": None,
        "note": "Use orange, not lemon. Its oils soften the Campari "
                "before you even take a sip.",
        "source": "Difford's Guide",
    },
],

"Mezcal Negroni": [
    {
        "name": "Orange peel, squeezed over",
        # Already an optional row in the ingredient list. This entry
        # survives as a TECHNIQUE note only -- no checklist link, or it
        # would show twice on one page under two headings.
        "ingredient": None,
        "measure": "1 strip",
        "note": "Orange, same as the gin Negroni. Squeeze the peel over "
                "the drink so its oil meets the mezcal's smoke.",
        "source": "Difford's Guide",
    },
],

"Boulevardier": [
    {
        "name": "Orange twist",
        "ingredient": "Oranges",
        "measure": "1 strip",
        "note": "Orange here, lemon for its close cousin the Old Pal. The"
                " garnish is how bartenders tell the two apart at a "
                "glance.",
        "source": "Difford's Guide",
    },
],

"Old Pal": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "Lemon, not orange. This is the drier cousin of the "
                "Boulevardier, and lemon keeps it that way.",
        "source": "Difford's Guide",
    },
],

"Sazerac": [
    {
        "name": "Lemon peel, squeezed and tossed",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "Squeeze the peel over the glass, wipe it round the rim, "
                "then throw it away. Left in, it keeps giving off oil "
                "until you taste lemon instead of rye.",
        "source": "Difford's Guide; Sazerac House",
    },
],

"Mint Julep": [
    {
        "name": "Big mint sprig",
        # No checklist link: the recipe already requires mint, so this is a
        # technique note, not a prompt to go and buy something. The migration
        # blocks any enhancement whose ingredient duplicates the spec, and it
        # was right to.
        "ingredient": None,
        "measure": "1 generous sprig",
        "note": "Clap the sprig between your palms, then stand it in the "
                "ice next to the straw. You smell mint on every sip, "
                "without the bitterness of crushing it into the drink.",
        "source": "Difford's Guide",
    },
],

"Mojito": [
    {
        "name": "Fresh mint sprig on top",
        # Recipe already requires mint -- technique note, not a shopping prompt.
        "ingredient": None,
        "measure": "1 sprig",
        "note": "Clap a fresh sprig between your palms and stand it on "
                "top. The mint in the drink has lost most of its smell, "
                "so this sprig is what you actually smell.",
        "source": "IBA official specification",
    },
],

"Mai Tai": [
    {
        "name": "Squeezed lime shell and mint",
        "ingredient": "Fresh mint",
        "measure": None,
        "note": "Float the squeezed lime half dome-up and tuck the mint "
                "right against it. Touching the shell, the mint picks up "
                "the lime oil, and this is the drink's classic garnish.",
        "source": "Trader Vic's original specification; IBA",
    },
],

"Zombie": [
    {
        "name": "Mint sprig",
        "ingredient": "Fresh mint",
        "measure": "1 sprig",
        "note": "Rest it on the ice, not in the drink. With four rums in "
                "the glass, the mint gives your nose something fresh.",
        "source": "Difford's Guide",
    },
],

"Espresso Martini": [
    {
        "name": "Three coffee beans",
        "ingredient": "Coffee",
        "measure": "3 beans",
        "note": "Float them in a line on the foam, as the drink's creator"
                " did. Tradition says they stand for health, wealth and "
                "happiness.",
        "source": "Difford's Guide; Dick Bradsell's original",
    },
],

"Margarita": [
    {
        "name": "Half salt rim",
        # Already an optional row in the ingredient list. This entry
        # survives as a TECHNIQUE note only -- no checklist link, or it
        # would show twice on one page under two headings.
        "ingredient": None,
        "measure": None,
        "note": "Salt only half the rim so you can choose with every sip."
                " Rub lime on the outside of the glass only, or salt "
                "falls in and the drink turns salty.",
        "source": "Difford's Guide",
    },
],

"Tommy's Margarita": [
    {
        "name": "Leave the rim bare",
        "ingredient": None,
        "measure": None,
        "note": "The original is served with no salt, which would flatten"
                " the agave syrup. If you want some, salt half the rim.",
        "source": "Difford's Guide",
    },
],

"Sidecar": [
    {
        "name": "Half sugar rim",
        "ingredient": "Sugar (white)",
        "measure": None,
        "note": "Optional even in the old recipes, and best on half the "
                "rim. A full sugar rim pushes this drink into dessert.",
        "source": "Difford's Guide; IBA (garnish listed as optional)",
    },
],

"Cosmopolitan": [
    {
        "name": "Flamed orange twist",
        "ingredient": "Oranges",
        "measure": "1 strip",
        "note": "Squeeze a wide strip of peel through a lit match over "
                "the drink, so the oil flares and lands toasted on top. "
                "Without it, all you smell is cranberry.",
        "source": "Difford's Guide",
    },
],

"Bloody Mary": [
    {
        "name": "Celery salt rim",
        "ingredient": "Salt",
        "measure": None,
        "note": "Rim the glass before you pour. It seasons every sip, so "
                "you are not chasing the flavour with extra Tabasco "
                "later.",
        "source": "IBA official specification",
    },
    {
        "name": "Black pepper on top",
        "ingredient": "Pepper",
        "measure": "a good grind",
        "note": "Grind it over the top at the end instead of stirring it "
                "in. The smell is most of what makes the drink taste "
                "savoury.",
        "source": "IBA official specification",
    },
],

"Bloody Maria": [
    {
        "name": "Celery salt rim",
        "ingredient": "Salt",
        "measure": None,
        "note": "Same as the vodka version. The salt is what ties the "
                "drink back to the tequila.",
        "source": "IBA official specification (Bloody Mary family)",
    },
],

"Caesar": [
    {
        "name": "Celery salt rim",
        "ingredient": "Salt",
        "measure": None,
        "note": "In Canada this isn't optional, and it's what sets a "
                "Caesar apart from a Bloody Mary. The glass has been "
                "rimmed since the drink was invented in Calgary in 1969.",
        "source": "Mott's Clamato / Walter Chell original",
    },
],

"Moscow Mule": [
    {
        "name": "Mint sprig and lime wedge",
        "ingredient": "Fresh mint",
        "measure": None,
        "note": "Use both. The copper mug hides the drink, so the garnish"
                " is all you smell before the first sip.",
        "source": "IBA official specification",
    },
],

"Aperol Spritz": [
    {
        "name": "Orange slice",
        "ingredient": "Oranges",
        "measure": "1 slice",
        "note": "Drop in a slice, not a twist. In a tall drink like this,"
                " it keeps adding orange as the ice melts.",
        "source": "IBA official specification",
    },
],

"Americano": [
    {
        "name": "Orange slice",
        "ingredient": "Oranges",
        "measure": "1 slice",
        "note": "Orange, same as its stronger sibling the Negroni. Some "
                "bars add a lemon twist too, but orange is the standard.",
        "source": "IBA official specification",
    },
],



"Pina Colada": [
    {
        "name": "Pineapple wedge and cherry",
        "ingredient": "Maraschino cherries",
        "measure": None,
        "note": "Cut a notch in the pineapple wedge so it sits on the rim"
                " without sliding. Put the cherry behind it rather than "
                "on the same cocktail stick.",
        "source": "IBA official specification",
    },
],

"Penicillin": [
    {
        "name": "Candied ginger",
        "ingredient": None,
        "measure": "1 piece",
        "note": "The creator's own garnish, laid across the rim on a "
                "cocktail stick. It tells you what's coming, and you eat "
                "it after the last sip.",
        "source": "Sam Ross, Milk & Honey; Difford's Guide",
    },
],

"Jungle Bird": [
    {
        "name": "Pineapple wedge",
        "ingredient": None,
        "measure": "1 wedge",
        "note": "Use fresh pineapple, not tinned. It's the only sweet "
                "smell sitting over the juice and Campari.",
        "source": "Difford's Guide",
    },
],

"The Last Word": [
    {
        "name": "Brandied cherry",
        "ingredient": "Maraschino cherries",
        "measure": "1",
        "note": "A dark brandied cherry matches the cherry liqueur "
                "already in the glass. A bright red cocktail cherry "
                "clashes with it.",
        "source": "Difford's Guide",
    },
],

"Hot Toddy": [
    {
        "name": "Clove-studded lemon",
        "ingredient": "Lemons",
        "measure": "1 slice",
        "note": "Push four or five cloves into a lemon slice and drop it "
                "in. The heat draws the clove out slowly, so the drink "
                "changes as you sip.",
        "source": "Difford's Guide",
    },
],

"Gibson": [
    {
        "name": "Cocktail onions",
        "ingredient": "Cocktail onions",
        "measure": "1 to 3",
        "note": "The onion is what makes it a Gibson rather than a "
                "Martini, so it's hardly optional. How many is up to you,"
                " but bartenders stick to odd numbers.",
        "source": "Difford's Guide",
    },
],

"Rob Roy": [
    {
        "name": "Brandied or maraschino cherry",
        "ingredient": "Maraschino cherries",
        "measure": "1",
        "note": "The same garnish as a Manhattan. With a smoky Scotch, "
                "some bars use a lemon twist instead.",
        "source": "IBA official specification",
    },
],

"Black Manhattan": [
    {
        "name": "Brandied cherry",
        "ingredient": "Maraschino cherries",
        "measure": "1",
        "note": "A cherry, same as the Manhattan it comes from. The sweet"
                " syrup on the last sip balances the dark, bitter amaro.",
        "source": "Difford's Guide",
    },
],

"Dark and Stormy": [
    {
        "name": "Lime wedge",
        "ingredient": "Limes",
        "measure": "1 wedge",
        "note": "Squeeze it in rather than leaving it on the rim. Ginger "
                "beer and dark rum are both sweet, and the lime keeps "
                "them in check.",
        "source": "IBA official specification",
    },
],

"Whiskey Sour": [
    {
        "name": "Angostura on the foam",
        # Already an optional row in the ingredient list. This entry
        # survives as a TECHNIQUE note only -- no checklist link, or it
        # would show twice on one page under two headings.
        "ingredient": None,
        "measure": "3 drops",
        "note": "Only if you used egg white, since the drops need foam to"
                " sit on. Dot them on and drag a cocktail stick through, "
                "so you smell the bitters first.",
        "source": "IBA official specification (Boston Sour variation)",
    },
],

"Pisco Punch": [
    {
        "name": "Pineapple chunk",
        "ingredient": None,
        "measure": "1",
        "note": "Ideally a piece that soaked in the pineapple syrup. Eat "
                "it when you finish the drink.",
        "source": "Difford's Guide",
    },
],

"Vieux Carré": [
    {
        "name": "Lemon twist",
        # Already an optional row in the ingredient list. This entry
        # survives as a TECHNIQUE note only -- no checklist link, or it
        # would show twice on one page under two headings.
        "ingredient": None,
        "measure": "1 strip",
        "note": "Squeeze it over the top and drop it in. Everything else "
                "in this drink is dark and rich, and the lemon is the "
                "only bright note.",
        "source": "Difford's Guide",
    },
],

"Paloma": [
    {
        "name": "Half salt rim",
        "ingredient": "Salt",
        "measure": None,
        "note": "Salt half the rim and put a lime wedge on the other "
                "side. Grapefruit and salt sharpen each other, and the "
                "bare half lets you choose.",
        "source": "Difford's Guide",
    },
],

"Irish Coffee": [
    {
        "name": "Grated nutmeg",
        "ingredient": None,
        "measure": "a light grating",
        "note": "Grate it over the cream, never stir it in. The San "
                "Francisco bar that made the drink famous in America "
                "serves it without, so try it both ways.",
        "source": "Difford's Guide (listed as an optional garnish)",
    },
],

"Brandy Alexander": [
    {
        "name": "Grated nutmeg",
        "ingredient": None,
        "measure": "a light grating",
        "note": "Grate it over the top just before serving. Pre-ground "
                "nutmeg has lost almost all its smell, so use a whole "
                "one.",
        "source": "IBA official specification",
    },
],

"Dirty Martini": [
    {
        "name": "Olives",
        "ingredient": "Olives",
        "measure": "1 or 3",
        "note": "Use one or three, and the same brine that went into the "
                "drink. The brine is an ingredient here, so a good olive "
                "in cheap brine is wasted.",
        "source": "Difford's Guide",
    },
],

"Gimlet": [
    {
        "name": "Lime wheel",
        "ingredient": "Limes",
        "measure": None,
        "note": "Perch a wheel on the rim rather than squeezing a wedge "
                "in. The drink is already balanced, and extra lime throws"
                " it off.",
        "source": "IBA official specification",
    },
],

"French 75": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 long strip",
        "note": "Drop a long spiral of peel into the flute. The bubbles "
                "carry the lemon oil up to your nose.",
        "source": "IBA official specification",
    },
],

"Corpse Reviver #2": [
    {
        "name": "Orange twist",
        "ingredient": "Oranges",
        "measure": "1 strip",
        "note": "Squeeze it over the top. The old warning is that four in"
                " a row will un-revive the corpse, and the orange oil "
                "makes the first one go down dangerously easily.",
        "source": "Difford's Guide; The Savoy Cocktail Book",
    },
],

"Hemingway Daiquiri": [
    {
        "name": "Lime wheel",
        "ingredient": "Limes",
        "measure": "1 wheel",
        "note": "This drink has almost no sugar, so it's meant to be "
                "sharp. The wheel is just for the smell, so don't squeeze"
                " it in unless you want it sharper.",
        "source": "Difford's Guide",
    },
],

"Clover Club": [
    {
        "name": "Raspberries on a stick",
        "ingredient": None,
        "measure": "2 or 3",
        "note": "Lay two or three on a cocktail stick across the glass. "
                "Without them, people mistake the raspberry colour for "
                "grenadine.",
        "source": "Difford's Guide",
    },
],

"Pimm's Cup": [
    {
        "name": "Cucumber, orange and mint",
        # Already an optional row in the ingredient list. This entry
        # survives as a TECHNIQUE note only -- no checklist link, or it
        # would show twice on one page under two headings.
        "ingredient": None,
        "measure": None,
        "note": "Use all three. The fruit is part of this drink, not "
                "decoration, and without it there's not much left.",
        "source": "IBA official specification",
    },
],

"Singapore Sling": [
    {
        "name": "Pineapple and cherry",
        "ingredient": "Maraschino cherries",
        "measure": None,
        "note": "A pineapple wedge with a cherry on the same cocktail "
                "stick, as the Singapore hotel it comes from serves it. "
                "There's pineapple juice in the drink, so it fits.",
        "source": "IBA official specification",
    },
],

"Sherry Cobbler": [
    {
        "name": "Berries and orange",
        "ingredient": "Oranges",
        "measure": None,
        "note": "Pile the fruit on top of the crushed ice, not under it. "
                "That mound of fruit and ice is why this drink made "
                "drinking straws popular in the 1800s.",
        "source": "Difford's Guide",
    },
],

"Queen's Park Swizzle": [
    {
        "name": "Angostura on top",
        "ingredient": "Angostura bitters",
        "measure": "6 to 8 dashes",
        "note": "Dash it over the top after stirring and let it bleed "
                "down through the ice. That red layer is the drink's "
                "signature, so don't stir it in.",
        "source": "Difford's Guide; Trader Vic",
    },
],

"Ramos Gin Fizz": [
    {
        "name": "Orange flower water on the foam",
        "ingredient": None,
        "measure": "1 drop",
        "note": "One drop on the foam, if you have some left from making "
                "the drink. The foam is the whole point here, so that's "
                "where the smell should be.",
        "source": "Difford's Guide",
    },
],

"Hanky Panky": [
    {
        "name": "Orange twist",
        # Already an optional row in the ingredient list. This entry
        # survives as a TECHNIQUE note only -- no checklist link, or it
        # would show twice on one page under two headings.
        "ingredient": None,
        "measure": "1 strip",
        "note": "The original garnish from the Savoy hotel in London, "
                "where the drink was created. Fernet is strong and minty,"
                " and orange is the one thing that sits well with it.",
        "source": "Difford's Guide; The Savoy Cocktail Book",
    },
],


"Vesper": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 large strip",
        "note": "James Bond orders it with a large, thin slice of lemon "
                "peel in Casino Royale. Not an olive.",
        "source": "Ian Fleming, Casino Royale; Difford's Guide",
    },
],

# ==================== Second pass, looser bar ==============================
# Everything below was added when the evidence bar moved from "documented
# variation only" to "documented or widely-accepted practice". Entries sourced
# to PRACTICE are the ones that only exist because of that move; they are
# labelled on the page and a reader can tell them apart at a glance.

"Daiquiri": [
    {
        "name": "Lime wheel",
        "ingredient": "Limes",
        "measure": "1 wheel",
        "note": "Perch it on the rim, don't squeeze it in. A Daiquiri is "
                "a tight balance of three ingredients, and extra lime "
                "tips it.",
        "source": "IBA official specification",
    },
],

"Dry Rob Roy": [
    {
        "name": "Lemon twist, not a cherry",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "The sweet Rob Roy gets a cherry, the dry one gets lemon."
                " A cherry would clash with the drier drink.",
        "source": "IBA official specification",
    },
],

"Blood and Sand": [
    {
        "name": "Flamed orange peel",
        "ingredient": "Oranges",
        "measure": "1 wide strip",
        "note": "Squeeze a wide strip of peel through a lit match over "
                "the drink. There's orange juice in it already, but the "
                "toasted oil is what pairs with the Scotch.",
        "source": "Difford's Guide",
    },
],

"Revolver": [
    {
        "name": "Flamed orange peel",
        "ingredient": "Oranges",
        "measure": "1 wide strip",
        "note": "Squeeze a wide strip of peel through a lit match over "
                "the drink. It's the creator's own garnish, and the "
                "toasted oil stops the coffee liqueur tasting like "
                "dessert.",
        "source": "Jon Santer's original; Difford's Guide",
    },
],

"Horse's Neck": [
    {
        "name": "Angostura, for a Horse's Neck with a Kick",
        "ingredient": "Angostura bitters",
        "measure": "2 dashes",
        "note": "Two dashes give a plain whiskey and ginger ale some "
                "backbone, and this version even has its own name. The "
                "long lemon spiral down the glass isn't optional either.",
        "source": "Difford's Guide",
    },
],

"Japanese Cocktail": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "It's in the original 1862 recipe. Cognac and almond "
                "syrup are soft, and the lemon oil is the only sharp "
                "thing on top.",
        "source": "Jerry Thomas, Bar-Tender's Guide 1862",
    },
],

"Seelbach": [
    {
        "name": "Orange twist",
        "ingredient": "Oranges",
        "measure": "1 strip",
        "note": "With fourteen dashes of bitters already in, the orange "
                "is the only bright note. Squeeze it over the top rather "
                "than just dropping it in.",
        "source": "Difford's Guide",
    },
],

"Brooklyn": [
    {
        "name": "Brandied cherry",
        "ingredient": "Maraschino cherries",
        "measure": "1",
        "note": "It matches the cherry liqueur in the drink, the way a "
                "Manhattan's cherry does. Use a dark brandied one, since "
                "a bright red one tastes out of place.",
        "source": PRACTICE,
    },
],

"Greenpoint": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "The original is finished with lemon. Rye, Chartreuse and"
                " sweet vermouth are heavy and herbal, and the lemon "
                "opens them up.",
        "source": "Difford's Guide",
    },
],

"Remember the Maine": [
    {
        "name": "Brandied cherry",
        "ingredient": "Maraschino cherries",
        "measure": "1",
        "note": "Underneath the cherry brandy and absinthe, this is a "
                "Manhattan. So it gets a Manhattan's cherry.",
        "source": "Difford's Guide",
    },
],

"Saratoga": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "Rye, cognac and sweet vermouth is a heavy mix. A lemon "
                "twist is the cheapest way to lighten it.",
        "source": PRACTICE,
    },
],

"Scofflaw": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "Grenadine and rye can turn syrupy. The lemon oil keeps "
                "it tasting like a sour, not a sweet drink.",
        "source": PRACTICE,
    },
],

"Bobby Burns Cocktail": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "Squeeze it over the top and drop it in. It keeps the "
                "honeyed, herbal Benedictine from getting cloying.",
        "source": "Difford's Guide",
    },
],

"Affinity": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "Scotch and two vermouths make a dense drink. Use a twist"
                " rather than a cherry, because mixing sweet and dry "
                "vermouth is meant to make it drier.",
        "source": PRACTICE,
    },
],

"Rusty Nail": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "Two sweet-leaning ingredients and no citrus at all. The "
                "twist is what stops it feeling heavy.",
        "source": "IBA official specification",
    },
],

"Godfather": [
    {
        "name": "Orange twist",
        "ingredient": "Oranges",
        "measure": "1 strip",
        "note": "Scotch and amaretto with nothing to cut them. Orange "
                "suits the almond flavour better than lemon does.",
        "source": PRACTICE,
    },
],

"Scotch Highball": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 long strip",
        "note": "Run a long strip of peel down the inside of the glass. "
                "Soda washes out a drink's smell quickly, and the twist "
                "puts some back.",
        "source": PRACTICE,
    },
],

"Bee's Knees": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "Honey can make a drink taste flat. The lemon oil gives "
                "the first sip back its edge.",
        "source": PRACTICE,
    },
],

"Gold Rush": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "This is basically a Bee's Knees made with bourbon. The "
                "honey needs something sharp on top, same as there.",
        "source": PRACTICE,
    },
],

"Southside": [
    {
        "name": "Mint sprig",
        "ingredient": "Fresh mint",
        "measure": "1 sprig",
        "note": "Clap a sprig between your palms and lay it on top. The "
                "mint shaken into the drink has lost its smell, so this "
                "sprig is what makes it taste minty.",
        "source": "Difford's Guide",
    },
],

"Whiskey Smash": [
    {
        "name": "Big mint sprig and lemon",
        "ingredient": "Fresh mint",
        "measure": "1 generous sprig",
        "note": "Be as generous with the mint as you would on a Mint "
                "Julep. Put it where your nose goes, not on the far side "
                "of the glass.",
        "source": "Difford's Guide",
    },
],

"Bramble": [
    {
        "name": "Lemon slice and a blackberry",
        "ingredient": "Lemons",
        "measure": None,
        "note": "The creator's own garnish. The blackberry sits on the "
                "ice where the blackberry liqueur bleeds down through the"
                " drink.",
        "source": "Difford's Guide; Dick Bradsell's original",
    },
],

"Aviation": [
    {
        "name": "Brandied cherry",
        "ingredient": "Maraschino cherries",
        "measure": "1",
        "note": "Drop it in. It matches the cherry liqueur in the drink, "
                "and it's the only colour in such a pale glass.",
        "source": PRACTICE,
    },
],

"White Lady": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "Gin, Cointreau and lemon is sharp and clean but has very"
                " little smell. Squeezing lemon peel over the top fixes "
                "that for free.",
        "source": PRACTICE,
    },
],

"Pink Lady": [
    {
        "name": "Brandied cherry",
        "ingredient": "Maraschino cherries",
        "measure": "1",
        "note": "Rest it on the foam if you used egg white, so it doesn't"
                " sink. The grenadine is sweet enough, so pick a dark "
                "brandied cherry over a bright red one.",
        "source": PRACTICE,
    },
],

"Gin And Tonic": [
    {
        "name": "Angostura, for a Pink Gin and Tonic",
        "ingredient": "Angostura bitters",
        "measure": "2 dashes",
        "note": "Two dashes over the ice before the tonic turn the drink "
                "pale pink and add a dry, spiced note. It's common enough"
                " in the UK to be sold ready-mixed.",
        "source": PRACTICE,
    },
    {
        "name": "Match the garnish to the gin",
        "ingredient": None,
        "measure": None,
        "note": "Lime for a classic piney gin, lemon or grapefruit for a "
                "citrusy one, orange for a spicy one. There's so little "
                "else in the glass that the garnish really matters.",
        "source": PRACTICE,
    },
],

"Salty Dog": [
    {
        "name": "Half salt rim",
        "ingredient": "Salt",
        "measure": None,
        "note": "The salt is what makes it a Salty Dog and not a "
                "Greyhound. Salt half the rim and you can taste both from"
                " one glass.",
        "source": "IBA official specification",
    },
],

"Greyhound": [
    {
        "name": "Grapefruit twist",
        "ingredient": None,
        "measure": "1 strip",
        "note": "No salt, or it becomes a Salty Dog. A grapefruit twist "
                "sharpens the juice instead.",
        "source": PRACTICE,
    },
],

"Siesta": [
    {
        "name": "Grapefruit twist",
        "ingredient": None,
        "measure": "1 strip",
        "note": "Think of a Hemingway Daiquiri made with tequila and a "
                "splash of Campari. The grapefruit oil ties the Campari "
                "to the juice.",
        "source": PRACTICE,
    },
],

"Rosita": [
    {
        "name": "Orange twist",
        "ingredient": "Oranges",
        "measure": "1 strip",
        "note": "This is a tequila Negroni underneath. It takes the same "
                "orange, which softens the Campari before you sip.",
        "source": PRACTICE,
    },
],

"Cardinale": [
    {
        "name": "Orange twist",
        "ingredient": "Oranges",
        "measure": "1 strip",
        "note": "A Negroni with dry vermouth instead of sweet. Being "
                "drier, it needs the orange oil even more.",
        "source": PRACTICE,
    },
],

"Negroni Sbagliato": [
    {
        "name": "Orange slice",
        "ingredient": "Oranges",
        "measure": "1 slice",
        "note": "A slice, not a twist. The prosecco already carries the "
                "smell, and the slice keeps adding orange as the ice "
                "melts.",
        "source": PRACTICE,
    },
],

"Milano-Torino": [
    {
        "name": "Orange slice",
        "ingredient": "Oranges",
        "measure": "1 slice",
        "note": "Just Campari and sweet vermouth, so there's nothing to "
                "hide behind. The orange is a real part of the balance.",
        "source": "Difford's Guide",
    },
],

"Bicicletta": [
    {
        "name": "Lemon slice",
        "ingredient": "Lemons",
        "measure": "1 slice",
        "note": "Lemon, not orange, here. White wine is already sharper "
                "than vermouth, and lemon goes with that.",
        "source": PRACTICE,
    },
],

"Vermouth Cocktail": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "The drink is almost nothing, which is the appeal, so "
                "every detail counts. Don't skip the twist.",
        "source": PRACTICE,
    },
],

"Hugo Spritz": [
    {
        "name": "Mint and lime",
        "ingredient": "Fresh mint",
        "measure": None,
        "note": "Use both, and clap the mint between your palms first. "
                "The Hugo was invented as a lighter, minty alternative to"
                " the Aperol Spritz, so the mint is the point.",
        "source": "Difford's Guide",
    },
],

"Autumn Garibaldi": [
    {
        "name": "Orange slice",
        "ingredient": "Oranges",
        "measure": "1 slice",
        "note": "A Garibaldi is all about fluffy, frothy fresh orange "
                "juice. A slice on top fits, but a twist doesn't really.",
        "source": PRACTICE,
    },
],

"Cuba Libre": [
    {
        "name": "Lime wedge, squeezed in",
        "ingredient": "Limes",
        "measure": "1 wedge",
        "note": "Squeeze it and drop it in, don't leave it on the rim. "
                "The lime is the only difference between this and a plain"
                " rum and coke.",
        "source": "IBA official specification",
    },
],

"Batanga": [
    {
        "name": "Salt rim, and stir with the knife",
        "ingredient": "Salt",
        "measure": None,
        "note": "The Mexican bar famous for this drink stirs it with the "
                "knife used to cut the limes. It's not just for show: the"
                " knife carries lime oil and salt into the glass.",
        "source": "Difford's Guide",
    },
],

"Cantarito": [
    {
        "name": "Chilli-salt rim",
        "ingredient": "Salt",
        "measure": None,
        "note": "Traditionally served in a clay cup with a salted rim, "
                "often Tajín or another chilli salt. The salt holds the "
                "three citrus juices together.",
        "source": PRACTICE,
    },
],

"Vampiro": [
    {
        "name": "Chilli-salt rim",
        "ingredient": "Salt",
        "measure": None,
        "note": "This is how it's served in Guadalajara. The salt is "
                "seasoning here, not decoration.",
        "source": PRACTICE,
    },
],

"Ranch Water": [
    {
        "name": "Lime wedge",
        "ingredient": "Limes",
        "measure": "1 wedge",
        "note": "With only three ingredients, one of them fizzy water, "
                "you can't hide a missing lime. Squeeze it in.",
        "source": PRACTICE,
    },
],

"Tequila Sunrise": [
    {
        "name": "Orange slice and cherry",
        "ingredient": "Maraschino cherries",
        "measure": None,
        "note": "This drink is made to be looked at, so the garnish "
                "matters more than usual. Don't stir after the grenadine "
                "goes in, or you lose the sunrise.",
        "source": "IBA official specification",
    },
],

"Mexican Mule": [
    {
        "name": "Mint sprig and lime",
        "ingredient": "Fresh mint",
        "measure": None,
        "note": "Same garnish as the Moscow Mule. In a copper mug, it's "
                "all you smell.",
        "source": PRACTICE,
    },
],

"Kentucky Mule": [
    {
        "name": "Mint sprig and lime",
        "ingredient": "Fresh mint",
        "measure": None,
        "note": "The bourbon version is closer to a Mint Julep. That "
                "makes the mint matter more here than in the vodka "
                "original.",
        "source": PRACTICE,
    },
],

"Jamaican Mule": [
    {
        "name": "Mint sprig and lime",
        "ingredient": "Fresh mint",
        "measure": None,
        "note": "Funky Jamaican rum and ginger beer is a loud mix. The "
                "mint gives your nose somewhere else to go.",
        "source": PRACTICE,
    },
],

"Mamie Taylor": [
    {
        "name": "Lemon wedge",
        "ingredient": "Lemons",
        "measure": "1 wedge",
        "note": "Lemon, not lime. That's what sets it apart from the Mule"
                " family it otherwise looks like.",
        "source": PRACTICE,
    },
],

"Painkiller": [
    {
        "name": "Grated nutmeg",
        "ingredient": None,
        "measure": "a generous grating",
        "note": "Grate it fresh over the top, the way the rum brand tied "
                "to this drink serves it. The drink is noticeably flatter"
                " without it.",
        "source": "Pusser's Rum official serve",
    },
],

"Planter's Punch": [
    {
        "name": "Grated nutmeg",
        "ingredient": None,
        "measure": "a light grating",
        "note": "Nutmeg on top is standard in the old recipes. It's what "
                "makes the drink taste older than its ingredients.",
        "source": "Difford's Guide",
    },
],

"Fish House Punch": [
    {
        "name": "Grated nutmeg",
        "ingredient": None,
        "measure": "a light grating",
        "note": "Grate it over the bowl, not each cup, so it scents the "
                "whole punch. It's an 18th-century punch habit that suits"
                " this one.",
        "source": PRACTICE,
    },
],

"Bee's Kiss": [
    {
        "name": "Grated nutmeg",
        "ingredient": None,
        "measure": "a light grating",
        "note": "Rum, honey and cream are soft all the way through. "
                "Nutmeg is the usual fix for exactly that.",
        "source": PRACTICE,
    },
],

"Hurricane": [
    {
        "name": "Orange slice and cherry",
        "ingredient": "Maraschino cherries",
        "measure": None,
        "note": "This is how it's served at the New Orleans bar it comes "
                "from. It's a big sweet drink, and the orange does real "
                "work.",
        "source": PRACTICE,
    },
],

"Mary Pickford": [
    {
        "name": "Brandied cherry",
        "ingredient": "Maraschino cherries",
        "measure": "1",
        "note": "It matches the cherry liqueur in the drink. Use a dark "
                "cherry, not a neon one, or the drink tastes much sweeter"
                " than it is.",
        "source": PRACTICE,
    },
],

"El Presidente": [
    {
        "name": "Orange twist",
        "ingredient": "Oranges",
        "measure": "1 strip",
        "note": "There's already orange liqueur in the glass. The twist "
                "builds on a flavour that's there instead of adding a new"
                " one.",
        "source": "Difford's Guide",
    },
],

"Bacardi Cocktail": [
    {
        "name": "Lime wedge",
        "ingredient": "Limes",
        "measure": "1 wedge",
        "note": "This is a Daiquiri with grenadine, so it takes the same "
                "lime. The grenadine makes a little extra citrus more "
                "welcome here.",
        "source": PRACTICE,
    },
],

"Ti' Punch": [
    {
        "name": "The lime disc, skin and all",
        "ingredient": "Limes",
        "measure": "1 thick disc",
        "note": "Cut a coin of lime with the skin on, squeeze it and drop"
                " it in whole. In Martinique, the oil from the peel is "
                "part of the drink.",
        "source": "Difford's Guide",
    },
],

"Suffering Bastard": [
    {
        "name": "Mint and cucumber",
        "ingredient": "Fresh mint",
        "measure": None,
        "note": "Its creator in Cairo garnished it with both. The "
                "cucumber keeps a gin, brandy and ginger drink from "
                "feeling heavy.",
        "source": "Difford's Guide",
    },
],

"Fog Cutter": [
    {
        "name": "Mint sprig and orange",
        "ingredient": "Fresh mint",
        "measure": None,
        "note": "Go big here. The sherry floated on top is the first "
                "thing you taste, and the mint is what meets it.",
        "source": PRACTICE,
    },
],

"Chi-Chi": [
    {
        "name": "Pineapple wedge and cherry",
        "ingredient": "Maraschino cherries",
        "measure": None,
        "note": "A Piña Colada made with vodka, so it gets the same "
                "garnish. Notch the pineapple so it sits on the rim.",
        "source": PRACTICE,
    },
],

"Blue Hurricane": [
    {
        "name": "Orange slice and cherry",
        "ingredient": "Maraschino cherries",
        "measure": None,
        "note": "The drink is bright blue and all about looks. So the "
                "garnish isn't a small detail here.",
        "source": PRACTICE,
    },
],

"Sex on the Beach": [
    {
        "name": "Orange slice",
        "ingredient": "Oranges",
        "measure": "1 slice",
        "note": "The standard garnish. Fresh orange on the rim is sharper"
                " than anything in this soft, sweet drink.",
        "source": "IBA official specification",
    },
],

"Lemon Drop": [
    {
        "name": "Sugar rim and lemon twist",
        "ingredient": "Sugar (white)",
        "measure": None,
        "note": "Sugar half the rim. The drink is a lemon candy in a "
                "glass, and without the sugar the name stops making "
                "sense.",
        "source": PRACTICE,
    },
],

"Long Island Iced Tea": [
    {
        "name": "Lemon wedge",
        "ingredient": "Lemons",
        "measure": "1 wedge",
        "note": "Squeeze it in. Five spirits and cola is a lot of "
                "sweetness, and the lemon in the recipe fades once the "
                "ice starts melting.",
        "source": "IBA official specification",
    },
],

"Kalimotxo": [
    {
        "name": "Lemon wedge",
        "ingredient": "Lemons",
        "measure": "1 wedge",
        "note": "Common in Spain, and it does real work. Red wine and "
                "cola are sweeter together than apart, and the lemon is "
                "the only thing cutting them.",
        "source": PRACTICE,
    },
],

"New York Sour": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "Drop it in before the red wine goes on top, so you don't"
                " break the layer. That red layer is the whole look of "
                "the drink.",
        "source": PRACTICE,
    },
],

"Bourbon Renewal": [
    {
        "name": "Lemon wheel",
        "ingredient": "Lemons",
        "measure": "1 wheel",
        "note": "Blackcurrant liqueur and bourbon both lean sweet and "
                "dark. The lemon keeps it a sour, not a dessert.",
        "source": PRACTICE,
    },
],

"Brown Derby": [
    {
        "name": "Grapefruit twist",
        "ingredient": None,
        "measure": "1 strip",
        "note": "Grapefruit peel oil is much stronger than the juice. "
                "There's plenty of honey in this drink to stand up to it.",
        "source": PRACTICE,
    },
],

"Ward Eight": [
    {
        "name": "Orange slice and cherry",
        "ingredient": "Maraschino cherries",
        "measure": None,
        "note": "This is how it has traditionally been served in Boston. "
                "It's a Whiskey Sour with grenadine, and it has always "
                "come with the fruit.",
        "source": PRACTICE,
    },
],

"Between the Sheets": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "A Sidecar with rum added, so it gets the same garnish. "
                "Skip the sugar rim here, as there's already plenty going"
                " on.",
        "source": PRACTICE,
    },
],

"Harvard": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "A brandy Manhattan in all but name. Cognac is rounder "
                "than rye, so lemon suits it better than a cherry.",
        "source": PRACTICE,
    },
],

"Grasshopper": [
    {
        "name": "Grated chocolate or a mint leaf",
        "ingredient": "Fresh mint",
        "measure": None,
        "note": "Pick one, not both. The drink is completely smooth, so "
                "the garnish is its only texture and its only smell.",
        "source": PRACTICE,
    },
],

"Toasted Almond": [
    {
        "name": "Grated nutmeg",
        "ingredient": None,
        "measure": "a light grating",
        "note": "Amaretto, coffee liqueur and cream, with nothing sharp "
                "anywhere. Nutmeg is the usual fix for a creamy drink "
                "that tastes flat.",
        "source": PRACTICE,
    },
],

"Kir Royale": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "Blackcurrant liqueur is very sweet, and champagne hides "
                "that more than it cuts it. A twist over the top is the "
                "easy fix.",
        "source": PRACTICE,
    },
],

"Mimosa": [
    {
        "name": "Orange twist",
        "ingredient": "Oranges",
        "measure": "1 strip",
        "note": "Squeeze it over the glass. Orange juice loses its smell "
                "minutes after squeezing, but the peel oil doesn't.",
        "source": PRACTICE,
    },
],

"Corpse Reviver No. 1": [
    {
        "name": "Orange twist",
        "ingredient": "Oranges",
        "measure": "1 strip",
        "note": "Cognac, calvados and sweet vermouth have no citrus at "
                "all. The twist is the only bright note.",
        "source": PRACTICE,
    },
],

"American Beauty": [
    {
        "name": "Mint sprig",
        "ingredient": "Fresh mint",
        "measure": "1 sprig",
        "note": "Tuck it beside the red wine sitting on top. The drink is"
                " meant to look like a rose, and the mint is the leaf.",
        "source": PRACTICE,
    },
],

"Vodka Martini": [
    {
        "name": "Orange bitters",
        "ingredient": "Orange bitters",
        "measure": "1 dash",
        "note": "Gin Martinis came with orange bitters as standard until "
                "the mid-1900s. Vodka has even less flavour than gin, so "
                "one dash does more here.",
        "source": PRACTICE,
    },
],

"Vodka Gimlet": [
    {
        "name": "Lime wheel",
        "ingredient": "Limes",
        "measure": "1 wheel",
        "note": "On the rim, not squeezed in, same as the gin version. "
                "The drink is already balanced, and extra lime tips it.",
        "source": PRACTICE,
    },
],

"Kamikaze": [
    {
        "name": "Lime wheel",
        "ingredient": "Limes",
        "measure": "1 wheel",
        "note": "Equal parts vodka, triple sec and lime is sharper than "
                "it sounds. The wheel is just for the smell, so don't "
                "squeeze it in.",
        "source": PRACTICE,
    },
],

"Cape Codder": [
    {
        "name": "Lime wedge",
        "ingredient": "Limes",
        "measure": "1 wedge",
        "note": "Squeeze it in. With just vodka and sweetened cranberry, "
                "the lime is most of what makes it drinkable.",
        "source": "IBA official specification",
    },
],

"Sea breeze": [
    {
        "name": "Lime wedge",
        "ingredient": "Limes",
        "measure": "1 wedge",
        "note": "Grapefruit and cranberry are tart but also sweet. Lime "
                "is a cleaner kind of sharp, and it wakes the drink up.",
        "source": "IBA official specification",
    },
],

"Woo Woo": [
    {
        "name": "Lime wedge",
        "ingredient": "Limes",
        "measure": "1 wedge",
        "note": "Peach schnapps and cranberry with no citrus at all. "
                "Squeeze the lime in, or it's sweet all the way down.",
        "source": PRACTICE,
    },
],

"Screwdriver": [
    {
        "name": "Orange slice",
        "ingredient": "Oranges",
        "measure": "1 slice",
        "note": "With only two ingredients, there's little else to "
                "change. Fresh orange on the rim is what stops it being "
                "juice with vodka in it.",
        "source": "IBA official specification",
    },
],

"Caipirinha": [
    {
        "name": "Press the lime gently",
        "ingredient": None,
        "measure": None,
        "note": "Press the lime just enough to get the juice and oil out,"
                " without mashing the white part under the skin. Mashing "
                "that is why homemade ones often taste bitter.",
        "source": PRACTICE,
    },
],

"Canchanchara": [
    {
        "name": "Lime wedge",
        "ingredient": "Limes",
        "measure": "1 wedge",
        "note": "The honey tends to bury the lime in the recipe. A wedge "
                "on the side lets you sharpen it to taste.",
        "source": PRACTICE,
    },
],

"Chet Baker": [
    {
        "name": "Orange twist",
        "ingredient": "Oranges",
        "measure": "1 strip",
        "note": "Rum, sweet vermouth, honey and bitters are warm all the "
                "way through. The orange oil gives it an edge.",
        "source": PRACTICE,
    },
],

"Oaxaca Old Fashioned": [
    {
        "name": "Flamed orange peel",
        "ingredient": "Oranges",
        "measure": "1 wide strip",
        "note": "The original calls for it: squeeze the peel through a "
                "lit match over the drink. Toasted orange and mezcal "
                "smoke build on each other.",
        "source": "Difford's Guide; Phil Ward's original",
    },
],

"Tequila Old Fashioned": [
    {
        "name": "Orange twist",
        "ingredient": "Oranges",
        "measure": "1 wide strip",
        "note": "Same garnish as the whiskey original. Squeeze it over "
                "the top, since orange and agave sit well together.",
        "source": PRACTICE,
    },
],

"Rum Old Fashioned": [
    {
        "name": "Orange twist",
        "ingredient": "Oranges",
        "measure": "1 wide strip",
        "note": "Aged rum has more vanilla and caramel than bourbon. That"
                " gives the orange oil more to lift, not less.",
        "source": PRACTICE,
    },
],

"Brandy Sour": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "Squeeze it over the top. Cognac is softer than whiskey, "
                "so a Brandy Sour can taste flat without something sharp.",
        "source": PRACTICE,
    },
],

"Tequila Sour": [
    {
        "name": "Lime wheel",
        "ingredient": "Limes",
        "measure": "1 wheel",
        "note": "Lime on top, even if the drink uses lemon juice. It "
                "points the drink back at the tequila.",
        "source": PRACTICE,
    },
],

"Vodka Sour": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "Vodka has no smell of its own, so this drink is all "
                "lemon and sugar. The peel oil gives it something to "
                "smell.",
        "source": PRACTICE,
    },
],

"Nikolaschka": [
    {
        "name": "Bite the lemon first",
        "ingredient": None,
        "measure": None,
        "note": "Put the sugared, coffee-topped lemon slice in your "
                "mouth, chew, then drink the brandy. The other way round,"
                " it's just brandy with a garnish.",
        "source": "Difford's Guide",
    },
],

"Airmail": [
    {
        "name": "Lime twist",
        "ingredient": "Limes",
        "measure": "1 strip",
        "note": "Honey and champagne both soften a drink. Lime peel oil "
                "is sharper than the juice and keeps it lively.",
        "source": PRACTICE,
    },
],

"Bamboo": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "Sherry and dry vermouth make a light, delicate drink. "
                "Anything heavier than a lemon twist would flatten it.",
        "source": "Difford's Guide",
    },
],

"Algonquin": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "The pineapple here tastes dry and slightly savoury, not "
                "tropical. The lemon oil keeps it that way.",
        "source": PRACTICE,
    },
],

"Cameron's Kick": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "Two whiskies and almond syrup make a dense, nutty drink."
                " A lemon twist is the lightest fix, and the right one.",
        "source": PRACTICE,
    },
],

"Pegu Club": [
    {
        "name": "Lime twist",
        "ingredient": "Limes",
        "measure": "1 strip",
        "note": "There's already lime juice and two kinds of bitters in "
                "the drink. The twist is just for the smell, so squeeze "
                "the peel over it and drop it in.",
        "source": "Difford's Guide",
    },
],

"Pornstar Martini": [
    {
        "name": "Half a passion fruit",
        "ingredient": None,
        "measure": "1/2",
        "note": "Float it cut-side up on top. The shot of prosecco on the"
                " side is meant to be sipped in turn with the cocktail, "
                "not poured in.",
        "source": "Difford's Guide",
    },
],

"Morning Glory Fizz": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "Scotch, absinthe and egg white, topped with soda. Put "
                "the twist on the foam, where you'll actually smell it.",
        "source": PRACTICE,
    },
],

"Oreo Mudslide": [
    {
        "name": "Crushed Oreo rim",
        "ingredient": None,
        "measure": None,
        "note": "Wet the rim with chocolate sauce and roll it in crushed "
                "cookies. It's a milkshake, so dress it like one.",
        "source": PRACTICE,
    },
],

"Chatham Artillery Punch": [
    {
        "name": "Lemon wheels in the bowl",
        "ingredient": "Lemons",
        "measure": None,
        "note": "Float them on the ice in the bowl, not one per cup. A "
                "punch is served from the bowl, so the smell should come "
                "from there.",
        "source": PRACTICE,
    },
],

"Brandy Cobbler": [
    {
        "name": "Fruit piled on the ice",
        "ingredient": "Oranges",
        "measure": None,
        "note": "Heap it on top of the crushed ice, not under it. That "
                "mound of fruit and ice is why the Cobbler made drinking "
                "straws popular in the 1800s.",
        "source": "Difford's Guide",
    },
],

"Brandy Daisy": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "A Daisy is a sour sweetened with liqueur, so it's "
                "sweeter than a plain sour. Lemon oil on top balances it.",
        "source": PRACTICE,
    },
],

"Bay Breeze": [
    {
        "name": "Lime wedge",
        "ingredient": "Limes",
        "measure": "1 wedge",
        "note": "Pineapple and cranberry are sweet-tart with no real "
                "bite. Squeeze the lime in to give it some.",
        "source": PRACTICE,
    },
],

"Matador": [
    {
        "name": "Lime wedge",
        "ingredient": "Limes",
        "measure": "1 wedge",
        "note": "Tinned pineapple juice is a lot sweeter than fresh. If "
                "that's what you're using, squeeze the lime in.",
        "source": PRACTICE,
    },
],

"Black Russian": [
    {
        "name": "Orange twist",
        "ingredient": "Oranges",
        "measure": "1 strip",
        "note": "Vodka adds no smell, so all you get is coffee liqueur. "
                "Orange oil goes well with coffee and gives the drink "
                "something fresh to smell.",
        "source": PRACTICE,
    },
],

"French Connection": [
    {
        "name": "Orange twist",
        "ingredient": "Oranges",
        "measure": "1 strip",
        "note": "Cognac and amaretto, both sweet, with nothing sharp "
                "anywhere. Same problem and same fix as the Godfather.",
        "source": PRACTICE,
    },
],

}
