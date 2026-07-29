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
        "note": "Swap one of the Angostura dashes for orange bitters, or add it "
                "alongside. Most pre-Prohibition Manhattan recipes called for orange "
                "bitters and the modern craft-bar house build usually splits the two. "
                "It lifts the vermouth and makes the drink read brighter without "
                "making it sweeter.",
        "source": "Difford's Guide; The PDT Cocktail Book",
    },
    {
        "name": "Brandied or maraschino cherry",
        # Already an optional row in the ingredient list. This entry
        # survives as a TECHNIQUE note only -- no checklist link, or it
        # would show twice on one page under two headings.
        "ingredient": None,
        "measure": None,
        "note": "The cherry is the traditional garnish and it is not just decoration: "
                "the syrup that comes off it changes the last mouthful. A neon "
                "cocktail cherry will do this job badly.",
        "source": "IBA official specification",
    },
],

"Old Fashioned": [
    {
        "name": "Orange bitters",
        "ingredient": "Orange bitters",
        "measure": "1 dash",
        "note": "Added alongside the Angostura, not instead of it. The orange bitters "
                "pick up the oil from the peel and the two together make the citrus "
                "read as part of the drink rather than as decoration.",
        "source": "Difford's Guide",
    },
    {
        "name": "Expressed orange peel",
        "ingredient": "Oranges",
        "measure": "1 wide strip",
        "note": "Squeeze a wide strip of peel skin-side down over the surface so the "
                "oil sprays across the top, then drop it in. This is the classic "
                "build. Muddling orange and cherry into the glass is a post-"
                "Prohibition American addition that most historians treat as a "
                "corruption; the pith adds bitterness and the pulp clouds it.",
        "source": "IBA official specification; Difford's Guide",
    },
],

"Martinez 2": [
    {
        "name": "Orange bitters",
        "ingredient": "Orange bitters",
        "measure": "1 dash",
        "note": "The original calls for Boker's bitters, which vanished for most of "
                "the twentieth century. Orange bitters is the standard substitution "
                "and is what most published modern versions use.",
        "source": "Difford's Guide",
    },
],

"Adonis": [
    {
        "name": "Orange bitters",
        "ingredient": "Orange bitters",
        "measure": "2 dashes",
        "note": "Difford's builds the Adonis with orange bitters as standard. With no "
                "spirit in the glass there is very little holding the sherry and "
                "vermouth apart, and the bitters give the drink an edge it otherwise "
                "lacks.",
        "source": "Difford's Guide",
    },
],

"Champagne Cocktail": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "Expressed over the top and dropped in. The sugar cube and bitters "
                "are already doing the work; the lemon oil is what stops it reading "
                "as sweet.",
        "source": "IBA official specification",
    },
],

# ============================ Garnish upgrades =============================

"Negroni": [
    {
        "name": "Orange bitters",
        "ingredient": "Orange bitters",
        "measure": "1 dash",
        "note": "Not in the Difford's or IBA build, and the named orange-bitters "
                "Negronis (Kingston, Sweet Orange) are separate drinks. It is still "
                "what a lot of bartenders do: one dash lands on the same note as the "
                "orange peel and takes a little of the hard edge off the Campari "
                "without making the drink sweeter. Start with one dash, not two.",
        "source": PRACTICE,
    },
    {
        "name": "Orange twist or slice",
        "ingredient": "Oranges",
        "measure": None,
        "note": "Not lemon. Difford's puts it plainly: \"Always garnish a Negroni "
                "with an orange twist or slice, the use of a lemon is a heinous "
                "crime.\" The orange oil is what softens the Campari on the nose "
                "before you taste it.",
        "source": "Difford's Guide",
    },
],

"Mezcal Negroni": [
    {
        "name": "Expressed orange peel",
        # Already an optional row in the ingredient list. This entry
        # survives as a TECHNIQUE note only -- no checklist link, or it
        # would show twice on one page under two headings.
        "ingredient": None,
        "measure": "1 strip",
        "note": "Same orange rule as the gin original. Express it over the surface "
                "rather than dropping it in dry; the smoke off the mezcal needs "
                "something to meet it on the nose.",
        "source": "Difford's Guide",
    },
],

"Boulevardier": [
    {
        "name": "Orange twist",
        "ingredient": "Oranges",
        "measure": "1 strip",
        "note": "Orange for the Boulevardier, lemon for the Old Pal. The two drinks "
                "are close cousins and the garnish is part of how bartenders tell "
                "them apart on the pass.",
        "source": "Difford's Guide",
    },
],

"Old Pal": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "Lemon, not orange. The Old Pal is drier than the Boulevardier, rye "
                "and dry vermouth rather than bourbon and sweet, and lemon oil keeps "
                "it pointed that way.",
        "source": "Difford's Guide",
    },
],

"Sazerac": [
    {
        "name": "Expressed lemon peel, discarded",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "Squeeze the peel over the glass, wipe the rim, then throw it away "
                "rather than dropping it in. Leaving it in the glass keeps releasing "
                "oil and by the third sip the drink tastes of lemon instead of rye.",
        "source": "Difford's Guide; Sazerac House",
    },
],

"Mint Julep": [
    {
        "name": "Slapped mint bouquet",
        # No checklist link: the recipe already requires mint, so this is a
        # technique note, not a prompt to go and buy something. The migration
        # blocks any enhancement whose ingredient duplicates the spec, and it
        # was right to.
        "ingredient": None,
        "measure": "1 generous sprig",
        "note": "Clap the sprig once between your palms to wake the oil, then plant it "
                "in the ice right next to the straw. You smell the mint on every sip; "
                "muddling it into the drink instead just makes it taste green and "
                "bitter.",
        "source": "Difford's Guide",
    },
],

"Mojito": [
    {
        "name": "Slapped mint sprig",
        # Recipe already requires mint -- technique note, not a shopping prompt.
        "ingredient": None,
        "measure": "1 sprig",
        "note": "The mint already in the drink has given up most of its aroma. A fresh "
                "slapped sprig sitting at the top of the glass is what you actually "
                "smell, and it is why a bar Mojito reads more minty than a home one.",
        "source": "IBA official specification",
    },
],

"Mai Tai": [
    {
        "name": "Spent lime shell and mint",
        "ingredient": "Fresh mint",
        "measure": None,
        "note": "Float the squeezed lime half shell-up like an island and tuck the mint "
                "sprig against it. Trader Vic's own garnish, and the mint has to touch "
                "the shell so the lime oil comes through with it.",
        "source": "Trader Vic's original specification; IBA",
    },
],

"Zombie": [
    {
        "name": "Mint sprig",
        "ingredient": "Fresh mint",
        "measure": "1 sprig",
        "note": "Sitting on the crushed ice, not in the drink. Four rums deep, the mint "
                "is the only thing giving your nose somewhere to go.",
        "source": "Difford's Guide",
    },
],

"Espresso Martini": [
    {
        "name": "Three coffee beans",
        "ingredient": "Coffee",
        "measure": "3 beans",
        "note": "Floated on the crema in a line. Bradsell's own garnish, and the "
                "traditional reading is health, wealth and happiness; the same "
                "three-bean superstition as sambuca con la mosca.",
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
        "note": "Salt only half the rim and leave the other half bare, so you choose "
                "with every sip instead of committing to salt on all of them. Rub the "
                "lime on the outside of the glass only; salt that falls inside "
                "dissolves and makes the whole drink salty.",
        "source": "Difford's Guide",
    },
],

"Tommy's Margarita": [
    {
        "name": "Leave the rim bare",
        "ingredient": None,
        "measure": None,
        "note": "Julio Bermejo's version is served unsalted. The agave syrup is already "
                "carrying the drink and salt flattens it. If you want salt, salt half "
                "the rim.",
        "source": "Difford's Guide",
    },
],

"Sidecar": [
    {
        "name": "Half sugar rim",
        "ingredient": "Sugar (white)",
        "measure": None,
        "note": "Optional even in the classic sources, and worth doing on half the rim "
                "only. A full sugar rim tips an already citrus-forward drink into "
                "dessert.",
        "source": "Difford's Guide; IBA (garnish listed as optional)",
    },
],

"Cosmopolitan": [
    {
        "name": "Flamed orange twist",
        "ingredient": "Oranges",
        "measure": "1 strip",
        "note": "Hold a wide strip skin-side down a few inches over the surface and "
                "squeeze it through a lit match. The oil ignites and lands caramelised "
                "on top. Purely aromatic, and the whole reason the drink smells like "
                "anything other than cranberry.",
        "source": "Difford's Guide",
    },
],

"Bloody Mary": [
    {
        "name": "Celery salt rim",
        "ingredient": "Salt",
        "measure": None,
        "note": "Salt the rim before you build. It seasons every sip from the outside "
                "instead of you chasing the seasoning with more Tabasco once it is "
                "already mixed.",
        "source": "IBA official specification",
    },
    {
        "name": "Black pepper on top",
        "ingredient": "Pepper",
        "measure": "a good grind",
        "note": "Ground over the surface at the end, not stirred in. The aroma sits "
                "right under your nose and it is most of what makes the drink read as "
                "savoury.",
        "source": "IBA official specification",
    },
],

"Bloody Maria": [
    {
        "name": "Celery salt rim",
        "ingredient": "Salt",
        "measure": None,
        "note": "Same as the vodka original. The tequila gives you more to work with "
                "than vodka does, and the salted rim is what ties it to the agave.",
        "source": "IBA official specification (Bloody Mary family)",
    },
],

"Caesar": [
    {
        "name": "Celery salt rim",
        "ingredient": "Salt",
        "measure": None,
        "note": "Non-negotiable in Canada and the thing that most separates a Caesar "
                "from a Bloody Mary made with Clamato. Walter Chell rimmed the glass "
                "from the start in Calgary in 1969.",
        "source": "Mott's Clamato / Walter Chell original",
    },
],

"Moscow Mule": [
    {
        "name": "Mint sprig and lime wedge",
        "ingredient": "Fresh mint",
        "measure": None,
        "note": "Both, not one. The copper mug hides the drink completely, so the "
                "garnish is doing all of the aromatic work before the first sip.",
        "source": "IBA official specification",
    },
],

"Aperol Spritz": [
    {
        "name": "Orange slice",
        "ingredient": "Oranges",
        "measure": "1 slice",
        "note": "A slice dropped in, not a twist. It is the IBA garnish and the extra "
                "surface area keeps giving the drink orange as the ice melts, which "
                "matters in something this long.",
        "source": "IBA official specification",
    },
],

"Americano": [
    {
        "name": "Orange slice",
        "ingredient": "Oranges",
        "measure": "1 slice",
        "note": "Orange for the Americano, the same as its stronger sibling the "
                "Negroni. Some bars add a lemon twist as well; the orange is the one "
                "the IBA specifies.",
        "source": "IBA official specification",
    },
],



"Pina Colada": [
    {
        "name": "Pineapple wedge and cherry",
        "ingredient": "Maraschino cherries",
        "measure": None,
        "note": "The IBA garnish. Cut a notch in the pineapple wedge so it sits on the "
                "rim without sliding, and put the cherry behind it rather than "
                "spearing them together.",
        "source": "IBA official specification",
    },
],

"Penicillin": [
    {
        "name": "Candied ginger",
        "ingredient": None,
        "measure": "1 piece",
        "note": "Sam Ross's own garnish, speared and laid across the rim. It tells you "
                "what the drink is before you taste it, and chewing it after the last "
                "sip is part of the point.",
        "source": "Sam Ross, Milk & Honey; Difford's Guide",
    },
],

"Jungle Bird": [
    {
        "name": "Pineapple wedge",
        "ingredient": None,
        "measure": "1 wedge",
        "note": "Fresh pineapple, not tinned. The drink is already carrying pineapple "
                "juice and Campari; the fresh wedge is the only sweet thing on the nose.",
        "source": "Difford's Guide",
    },
],

"The Last Word": [
    {
        "name": "Brandied cherry",
        "ingredient": "Maraschino cherries",
        "measure": "1",
        "note": "Dropped in, and it echoes the maraschino already in the glass. A "
                "luxardo-style cherry works with the drink; a bright red cocktail "
                "cherry fights it.",
        "source": "Difford's Guide",
    },
],

"Hot Toddy": [
    {
        "name": "Clove-studded lemon",
        "ingredient": "Lemons",
        "measure": "1 slice",
        "note": "Push four or five cloves through a lemon slice and drop it in. The "
                "heat pulls the clove oil out slowly, so the drink changes over the "
                "ten minutes you take to drink it.",
        "source": "Difford's Guide",
    },
],

"Gibson": [
    {
        "name": "Cocktail onions",
        "ingredient": "Cocktail onions",
        "measure": "1 to 3",
        "note": "The onion is the entire difference between a Gibson and a Dry Martini, "
                "so it is not really optional; but the count is yours. Odd numbers "
                "are the bar convention.",
        "source": "Difford's Guide",
    },
],

"Rob Roy": [
    {
        "name": "Brandied or maraschino cherry",
        "ingredient": "Maraschino cherries",
        "measure": "1",
        "note": "A Manhattan garnish on a Manhattan-shaped drink. Some bars use a lemon "
                "twist instead when the Scotch is peaty, on the grounds that a cherry "
                "and smoke do not meet in the middle.",
        "source": "IBA official specification",
    },
],

"Black Manhattan": [
    {
        "name": "Brandied cherry",
        "ingredient": "Maraschino cherries",
        "measure": "1",
        "note": "Todd Smith's original is garnished with a cherry, same as the Manhattan "
                "it is built from. The amaro is already bitter and dark, so the cherry "
                "syrup on the last sip earns its place more here than in the original.",
        "source": "Difford's Guide",
    },
],

"Dark and Stormy": [
    {
        "name": "Lime wedge",
        "ingredient": "Limes",
        "measure": "1 wedge",
        "note": "Squeezed in rather than perched on the rim. The ginger beer is sweet "
                "and the dark rum is sweeter, and without the lime there is nothing "
                "holding the two apart.",
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
        "note": "Only works if you have used egg white, since the drops need a surface "
                "to sit on. Dot them on the foam and draw a cocktail stick through; "
                "it is aromatic, not decorative, and you get the bitters on the nose "
                "before the sour hits.",
        "source": "IBA official specification (Boston Sour variation)",
    },
],

"Pisco Punch": [
    {
        "name": "Pineapple chunk",
        "ingredient": None,
        "measure": "1",
        "note": "Preferably one of the pineapple pieces that steeped in the syrup. The "
                "gum syrup carries the pineapple through the drink and eating the chunk "
                "at the end closes the loop.",
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
        "note": "Expressed and dropped in. There are already two bitters, rye, cognac, "
                "vermouth and Benedictine in the glass; the lemon oil is the only thing "
                "in the drink that is bright.",
        "source": "Difford's Guide",
    },
],

"Paloma": [
    {
        "name": "Half salt rim",
        "ingredient": "Salt",
        "measure": None,
        "note": "Salt on half the rim, lime wedge on the other side. It works the same "
                "way as on a Margarita: grapefruit and salt sharpen each other, and "
                "leaving half bare lets you decide sip by sip.",
        "source": "Difford's Guide",
    },
],

"Irish Coffee": [
    {
        "name": "Grated nutmeg",
        "ingredient": None,
        "measure": "a light grating",
        "note": "Over the cream, never stirred in. Contested: the Buena Vista in San "
                "Francisco, which made the drink famous in the States, serves it bare. "
                "Try it both ways before deciding.",
        "source": "Difford's Guide (listed as an optional garnish)",
    },
],

"Brandy Alexander": [
    {
        "name": "Grated nutmeg",
        "ingredient": None,
        "measure": "a light grating",
        "note": "Grated over the top at the last second. Pre-ground nutmeg has lost "
                "almost everything; a whole nutmeg and a fine grater is the difference "
                "between an aroma and a dusting.",
        "source": "IBA official specification",
    },
],

"Dirty Martini": [
    {
        "name": "Olives",
        "ingredient": "Olives",
        "measure": "1 or 3",
        "note": "Odd numbers, and use the same brine you poured into the drink. A "
                "high-quality olive in cheap brine is a waste; the brine is an "
                "ingredient here, not packaging.",
        "source": "Difford's Guide",
    },
],

"Gimlet": [
    {
        "name": "Lime wedge or wheel",
        "ingredient": "Limes",
        "measure": None,
        "note": "A wheel on the rim reads better than a wedge dropped in, because the "
                "drink is already at its intended sweetness and squeezing more lime in "
                "moves it off balance.",
        "source": "IBA official specification",
    },
],

"French 75": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 long strip",
        "note": "A long spiral in the flute. The champagne is throwing aroma up out of "
                "the glass constantly and the lemon oil rides along with it.",
        "source": "IBA official specification",
    },
],

"Corpse Reviver #2": [
    {
        "name": "Orange twist",
        "ingredient": "Oranges",
        "measure": "1 strip",
        "note": "Expressed over the top. Harry Craddock's warning that four in swift "
                "succession will unrevive the corpse is still the best thing written "
                "about this drink, and the orange oil is what makes the first one "
                "dangerously easy.",
        "source": "Difford's Guide; The Savoy Cocktail Book",
    },
],

"Hemingway Daiquiri": [
    {
        "name": "Lime wheel",
        "ingredient": "Limes",
        "measure": "1 wheel",
        "note": "There is no sugar in this drink beyond the maraschino, so it lands "
                "sharp on purpose. The lime wheel is aromatic only; do not squeeze it "
                "in unless you want it sharper still.",
        "source": "Difford's Guide",
    },
],

"Clover Club": [
    {
        "name": "Raspberries on a stick",
        "ingredient": None,
        "measure": "2 or 3",
        "note": "Speared and laid across the glass. The drink gets its colour from "
                "raspberry syrup and without the fruit on top most people read it as "
                "grenadine, which is a different and worse drink.",
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
        "note": "All three, not one. The Pimm's Cup is closer to a fruit cup than a "
                "cocktail and the garnish is a genuine part of the recipe rather than a "
                "flourish; strip it back to a lemon slice and there is very little "
                "drink left.",
        "source": "IBA official specification",
    },
],

"Singapore Sling": [
    {
        "name": "Pineapple and cherry",
        "ingredient": "Maraschino cherries",
        "measure": None,
        "note": "The Raffles serve is a pineapple wedge with a cherry speared to it. "
                "The drink already contains pineapple juice, so this is continuity "
                "rather than decoration.",
        "source": "IBA official specification",
    },
],

"Sherry Cobbler": [
    {
        "name": "Berries and orange",
        "ingredient": "Oranges",
        "measure": None,
        "note": "Pile the fruit on top of the crushed ice rather than burying it. The "
                "Cobbler was the drink that made the drinking straw popular in the "
                "1800s precisely because of the fruit and ice mound sitting on top.",
        "source": "Difford's Guide",
    },
],

"Queen's Park Swizzle": [
    {
        "name": "Angostura float",
        "ingredient": "Angostura bitters",
        "measure": "6 to 8 dashes",
        "note": "Dashed across the top of the crushed ice after the swizzling, and left "
                "to bleed down through the drink. This is the whole visual and aromatic "
                "signature of the drink; stirring it in loses both.",
        "source": "Difford's Guide; Trader Vic",
    },
],

"Ramos Gin Fizz": [
    {
        "name": "Orange flower on the head",
        "ingredient": None,
        "measure": "1 drop",
        "note": "A single drop on the risen head, if you have orange flower water left "
                "over from building it. The head is the entire point of this drink and "
                "putting the aroma on top of it means you meet it first.",
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
        "note": "Ada Coleman's original at the Savoy. The Fernet is doing something "
                "very assertive and menthol-heavy, and orange oil is the one thing that "
                "meets it without arguing.",
        "source": "Difford's Guide; The Savoy Cocktail Book",
    },
],


"Vesper": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 large strip",
        "note": "Fleming specified it in Casino Royale, \"a large thin slice of lemon "
                "peel\", and it is the only garnish the book names. Not an olive.",
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
        "note": "On the rim, not squeezed in. A Daiquiri is three ingredients balanced "
                "against each other and any extra lime moves it off; the wheel is there "
                "so you get citrus on the nose while the balance stays where you put it.",
        "source": "IBA official specification",
    },
],

"Dry Rob Roy": [
    {
        "name": "Lemon twist, not a cherry",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "The sweet Rob Roy takes a cherry; the dry one takes a lemon twist. "
                "Swapping the garnish with the vermouth is how the two are told apart "
                "on sight, and a cherry in a dry Rob Roy fights the drink rather than "
                "finishing it.",
        "source": "IBA official specification",
    },
],

"Blood and Sand": [
    {
        "name": "Flamed orange peel",
        "ingredient": "Oranges",
        "measure": "1 wide strip",
        "note": "Squeeze a wide strip through a lit match over the surface. There is "
                "already orange juice in the drink, so this is not adding orange, it is "
                "adding the caramelised oil, which is the one thing that meets the "
                "Scotch on the nose.",
        "source": "Difford's Guide",
    },
],

"Revolver": [
    {
        "name": "Flamed orange peel",
        "ingredient": "Oranges",
        "measure": "1 wide strip",
        "note": "Jon Santer's own garnish and effectively part of the recipe. The burnt "
                "orange oil is what stops the coffee liqueur reading as dessert.",
        "source": "Jon Santer's original; Difford's Guide",
    },
],

"Horse's Neck": [
    {
        "name": "Angostura, for a Horse's Neck with a Kick",
        "ingredient": "Angostura bitters",
        "measure": "2 dashes",
        "note": "The bitters version has its own name, which tells you how standard it "
                "is. Two dashes turn a fairly plain highball into something with a "
                "spine. The long lemon spiral down the inside of the glass is the other "
                "half of the drink and is not optional.",
        "source": "Difford's Guide",
    },
],

"Japanese Cocktail": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "Jerry Thomas specified it in 1862 and the drink needs it. Cognac, "
                "orgeat and bitters is a soft, almond-heavy combination with nothing "
                "sharp in it until the lemon oil goes on top.",
        "source": "Jerry Thomas, Bar-Tender's Guide 1862",
    },
],

"Seelbach": [
    {
        "name": "Orange twist",
        "ingredient": "Oranges",
        "measure": "1 strip",
        "note": "With seven dashes each of two bitters already in the glass, the orange "
                "oil is the only bright thing on the drink. Express it over the surface "
                "rather than dropping it in.",
        "source": "Difford's Guide",
    },
],

"Brooklyn": [
    {
        "name": "Brandied cherry",
        "ingredient": "Maraschino cherries",
        "measure": "1",
        "note": "It echoes the maraschino already in the build the way a Manhattan's "
                "cherry does. Use a dark brandied one; a bright red cocktail cherry "
                "sits oddly against a drink this dry.",
        "source": PRACTICE,
    },
],

"Greenpoint": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "Michael McIlroy's original is finished with lemon. Rye, Chartreuse and "
                "sweet vermouth is a heavy, herbal stack and the lemon oil is what "
                "opens it up.",
        "source": "Difford's Guide",
    },
],

"Remember the Maine": [
    {
        "name": "Brandied cherry",
        "ingredient": "Maraschino cherries",
        "measure": "1",
        "note": "Charles H. Baker's drink, and it is a Manhattan underneath the cherry "
                "brandy and absinthe, so it takes a Manhattan's garnish.",
        "source": "Difford's Guide",
    },
],

"Saratoga": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "Equal parts rye, cognac and sweet vermouth is a lot of weight in one "
                "glass. Expressed lemon oil is the cheapest way to give it a lift.",
        "source": PRACTICE,
    },
],

"Scofflaw": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "Grenadine and rye can tip syrupy. The lemon oil on top is what keeps "
                "the drink reading as a sour rather than as a sweet one.",
        "source": PRACTICE,
    },
],

"Bobby Burns Cocktail": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "Expressed and dropped in. The Benedictine is doing something honeyed "
                "and herbal, and lemon oil is what keeps that from going cloying.",
        "source": "Difford's Guide",
    },
],

"Affinity": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "Both vermouths and Scotch make for a dense drink. A twist rather than "
                "a cherry, because the point of a Perfect is that it is drier than the "
                "sweet version.",
        "source": PRACTICE,
    },
],

"Rusty Nail": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "Two ingredients, both sweet-leaning, no citrus anywhere. The twist is "
                "the only thing standing between this and a very heavy drink.",
        "source": "IBA official specification",
    },
],

"Godfather": [
    {
        "name": "Orange twist",
        "ingredient": "Oranges",
        "measure": "1 strip",
        "note": "Scotch and amaretto with nothing to cut them. Orange oil works better "
                "than lemon here because it sits on the same almond-and-marzipan note "
                "rather than arguing with it.",
        "source": PRACTICE,
    },
],

"Scotch Highball": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 long strip",
        "note": "A long strip down the inside of the glass. Soda dilutes aroma faster "
                "than it dilutes flavour, and the twist puts some back.",
        "source": PRACTICE,
    },
],

"Bee's Knees": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "Honey rounds a drink off and can flatten it. The expressed oil gives "
                "the first sip an edge the honey has taken away.",
        "source": PRACTICE,
    },
],

"Gold Rush": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "T.J. Siegal's bourbon Bee's Knees, and it takes the same finish for "
                "the same reason: the honey syrup needs something sharp on top of it.",
        "source": PRACTICE,
    },
],

"Southside": [
    {
        "name": "Mint sprig",
        "ingredient": "Fresh mint",
        "measure": "1 sprig",
        "note": "Slap it and lay it on top. The mint that got shaken into the drink has "
                "given up its aroma already, and this is a drink people describe as "
                "minty entirely because of the sprig they are smelling.",
        "source": "Difford's Guide",
    },
],

"Whiskey Smash": [
    {
        "name": "Mint bouquet and lemon",
        "ingredient": "Fresh mint",
        "measure": "1 generous sprig",
        "note": "A Smash is a Julep with fruit in it and the garnish should be just as "
                "generous. Put the sprig where your nose goes, not on the far side of "
                "the glass.",
        "source": "Difford's Guide",
    },
],

"Bramble": [
    {
        "name": "Lemon slice and a blackberry",
        "ingredient": "Lemons",
        "measure": None,
        "note": "Bradsell's own garnish. The blackberry sits on the crushed ice where "
                "the creme de mure has bled down through the drink, which is the whole "
                "look of the thing.",
        "source": "Difford's Guide; Dick Bradsell's original",
    },
],

"Aviation": [
    {
        "name": "Brandied cherry",
        "ingredient": "Maraschino cherries",
        "measure": "1",
        "note": "Dropped in. It picks up the maraschino liqueur already in the glass, "
                "and in a drink this pale it is also the only colour.",
        "source": PRACTICE,
    },
],

"White Lady": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "Gin, Cointreau and lemon juice is a sharp, clean stack with no aroma "
                "sitting above it. Expressed oil fixes that and costs nothing.",
        "source": PRACTICE,
    },
],

"Pink Lady": [
    {
        "name": "Brandied cherry",
        "ingredient": "Maraschino cherries",
        "measure": "1",
        "note": "On the foam if you have used egg white, so it sits rather than sinks. "
                "The grenadine is already sweet, so use a dark brandied cherry rather "
                "than a bright red one.",
        "source": PRACTICE,
    },
],

"Gin And Tonic": [
    {
        "name": "Angostura, for a Pink Gin and Tonic",
        "ingredient": "Angostura bitters",
        "measure": "2 dashes",
        "note": "Two dashes over the ice before the tonic. It turns the drink pale pink "
                "and adds a dry, spiced note that gives a plain G and T somewhere to go. "
                "Standard enough in the UK to be sold ready-mixed.",
        "source": PRACTICE,
    },
    {
        "name": "Match the garnish to the gin",
        "ingredient": None,
        "measure": None,
        "note": "Lime for a juniper-forward London Dry, lemon or grapefruit for a "
                "citrus-led gin, orange for anything with a heavy spice bill. The "
                "garnish is a much bigger share of a G and T than of most drinks "
                "because there is so little else in the glass.",
        "source": PRACTICE,
    },
],

"Salty Dog": [
    {
        "name": "Half salt rim",
        "ingredient": "Salt",
        "measure": None,
        "note": "The salt is the entire difference between this and a Greyhound, so it "
                "is not really optional. Half the rim still lets you compare the two "
                "from one glass.",
        "source": "IBA official specification",
    },
],

"Greyhound": [
    {
        "name": "Grapefruit twist",
        "ingredient": None,
        "measure": "1 strip",
        "note": "No salt: salt it and you have made a Salty Dog. A grapefruit twist "
                "sharpens the juice without crossing that line.",
        "source": PRACTICE,
    },
],

"Siesta": [
    {
        "name": "Grapefruit twist",
        "ingredient": None,
        "measure": "1 strip",
        "note": "Katie Stipe's drink is a Hemingway Daiquiri built on tequila with "
                "Campari in it. The grapefruit oil ties the Campari to the juice.",
        "source": PRACTICE,
    },
],

"Rosita": [
    {
        "name": "Orange twist",
        "ingredient": "Oranges",
        "measure": "1 strip",
        "note": "It is a tequila Negroni underneath, and it takes the Negroni's orange "
                "for the same reason: it is what softens the Campari before you taste "
                "it.",
        "source": PRACTICE,
    },
],

"Cardinale": [
    {
        "name": "Orange twist",
        "ingredient": "Oranges",
        "measure": "1 strip",
        "note": "A Negroni with dry vermouth instead of sweet, so it lands drier and "
                "needs the orange oil more, not less.",
        "source": PRACTICE,
    },
],

"Negroni Sbagliato": [
    {
        "name": "Orange slice",
        "ingredient": "Oranges",
        "measure": "1 slice",
        "note": "A slice rather than a twist. There is prosecco doing the aromatic work "
                "already and the slice keeps giving the drink orange as it dilutes.",
        "source": PRACTICE,
    },
],

"Milano-Torino": [
    {
        "name": "Orange slice",
        "ingredient": "Oranges",
        "measure": "1 slice",
        "note": "Campari and sweet vermouth, nothing else, so there is very little in "
                "the glass to hide behind. The orange is a real part of the balance.",
        "source": "Difford's Guide",
    },
],

"Bicicletta": [
    {
        "name": "Lemon slice",
        "ingredient": "Lemons",
        "measure": "1 slice",
        "note": "Lemon rather than orange here, because the white wine is already "
                "sharper than a vermouth would be and lemon runs with it.",
        "source": PRACTICE,
    },
],

"Vermouth Cocktail": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "This is a drink made of almost nothing, which is the appeal, and it "
                "means every element counts twice as much. Do not skip the twist.",
        "source": PRACTICE,
    },
],

"Hugo Spritz": [
    {
        "name": "Mint and lime",
        "ingredient": "Fresh mint",
        "measure": None,
        "note": "Both, and the mint should be slapped first. The Hugo was invented in "
                "South Tyrol specifically as a lighter, minty alternative to the Aperol "
                "Spritz, so without the mint you have made something else.",
        "source": "Difford's Guide",
    },
],

"Autumn Garibaldi": [
    {
        "name": "Orange slice",
        "ingredient": "Oranges",
        "measure": "1 slice",
        "note": "The whole trick of a Garibaldi is fluffy, aerated fresh orange juice. "
                "A slice on top continues that; a twist does not really fit the drink.",
        "source": PRACTICE,
    },
],

"Cuba Libre": [
    {
        "name": "Lime wedge, squeezed in",
        "ingredient": "Limes",
        "measure": "1 wedge",
        "note": "Squeezed and dropped, not perched on the rim. The lime is the entire "
                "difference between a Cuba Libre and rum and coke, and leaving it on "
                "the rim means you have made the second one.",
        "source": "IBA official specification",
    },
],

"Batanga": [
    {
        "name": "Salt rim, and stir with the knife",
        "ingredient": "Salt",
        "measure": None,
        "note": "Don Javier Delgado Corona at La Capilla in Tequila stirs every Batanga "
                "with the same knife he cuts the limes with. It is a real technique and "
                "not just theatre: the knife carries lime oil and a little salt into "
                "the drink.",
        "source": "Difford's Guide",
    },
],

"Cantarito": [
    {
        "name": "Chilli-salt rim",
        "ingredient": "Salt",
        "measure": None,
        "note": "Traditionally served in a clay cup with a salted rim, and Tajin or any "
                "chilli salt is the common version. Three citrus juices in one drink "
                "need the salt to hold them together.",
        "source": PRACTICE,
    },
],

"Vampiro": [
    {
        "name": "Chilli-salt rim",
        "ingredient": "Salt",
        "measure": None,
        "note": "The drink is already sangrita, tequila and heat. A chilli salt rim is "
                "how it is served in Guadalajara and it is doing seasoning work, not "
                "decoration.",
        "source": PRACTICE,
    },
],

"Ranch Water": [
    {
        "name": "Lime wedge",
        "ingredient": "Limes",
        "measure": "1 wedge",
        "note": "Three ingredients and one of them is sparkling mineral water, so there "
                "is nothing to hide a missing lime behind. Squeeze it in.",
        "source": PRACTICE,
    },
],

"Tequila Sunrise": [
    {
        "name": "Orange slice and cherry",
        "ingredient": "Maraschino cherries",
        "measure": None,
        "note": "Standard IBA garnish, and the drink is built to be looked at, so it "
                "matters more here than in most. Do not stir after the grenadine goes "
                "in or you lose the gradient.",
        "source": "IBA official specification",
    },
],

"Mexican Mule": [
    {
        "name": "Mint sprig and lime",
        "ingredient": "Fresh mint",
        "measure": None,
        "note": "Same finish as the Moscow Mule it is built from. If you are serving in "
                "copper the garnish is doing all the aromatic work.",
        "source": PRACTICE,
    },
],

"Kentucky Mule": [
    {
        "name": "Mint sprig and lime",
        "ingredient": "Fresh mint",
        "measure": None,
        "note": "The bourbon version sits closer to a Julep than the vodka one does, "
                "which makes the mint less optional here than in the original.",
        "source": PRACTICE,
    },
],

"Jamaican Mule": [
    {
        "name": "Mint sprig and lime",
        "ingredient": "Fresh mint",
        "measure": None,
        "note": "Funky Jamaican rum and ginger beer is a loud combination. The mint "
                "gives your nose somewhere else to be.",
        "source": PRACTICE,
    },
],

"Mamie Taylor": [
    {
        "name": "Lemon wedge",
        "ingredient": "Lemons",
        "measure": "1 wedge",
        "note": "Lemon, not lime; that is what separates a Mamie Taylor from the Mule "
                "family it otherwise resembles.",
        "source": PRACTICE,
    },
],

"Painkiller": [
    {
        "name": "Grated nutmeg",
        "ingredient": None,
        "measure": "a generous grating",
        "note": "Pusser's own serve and effectively part of the recipe. Grate it fresh "
                "over the top; the aroma is the first thing you get and the drink is "
                "noticeably flatter without it.",
        "source": "Pusser's Rum official serve",
    },
],

"Planter's Punch": [
    {
        "name": "Grated nutmeg",
        "ingredient": None,
        "measure": "a light grating",
        "note": "Nutmeg over the top is standard across the old Planter's Punch recipes "
                "and it is what makes the drink taste older than its ingredients.",
        "source": "Difford's Guide",
    },
],

"Fish House Punch": [
    {
        "name": "Grated nutmeg",
        "ingredient": None,
        "measure": "a light grating",
        "note": "Over the bowl, not each cup, so it perfumes the whole thing. An "
                "eighteenth-century punch convention and it belongs on this one.",
        "source": PRACTICE,
    },
],

"Bee's Kiss": [
    {
        "name": "Grated nutmeg",
        "ingredient": None,
        "measure": "a light grating",
        "note": "Rum, honey and cream is soft all the way through with nothing to catch "
                "on. Nutmeg is the standard fix for exactly that problem.",
        "source": PRACTICE,
    },
],

"Hurricane": [
    {
        "name": "Orange slice and cherry",
        "ingredient": "Maraschino cherries",
        "measure": None,
        "note": "Pat O'Brien's serve in New Orleans. It is a big sweet drink and the "
                "orange is doing more than decorating.",
        "source": PRACTICE,
    },
],

"Mary Pickford": [
    {
        "name": "Brandied cherry",
        "ingredient": "Maraschino cherries",
        "measure": "1",
        "note": "It echoes the maraschino liqueur in the build. A good dark cherry, not "
                "a neon one, or the drink reads as much sweeter than it is.",
        "source": PRACTICE,
    },
],

"El Presidente": [
    {
        "name": "Orange twist",
        "ingredient": "Oranges",
        "measure": "1 strip",
        "note": "There is already curacao in the glass, so the twist continues a note "
                "the drink is making rather than adding a new one.",
        "source": "Difford's Guide",
    },
],

"Bacardi Cocktail": [
    {
        "name": "Lime wedge",
        "ingredient": "Limes",
        "measure": "1 wedge",
        "note": "It is a Daiquiri with grenadine, so it wants the same finish, and the "
                "grenadine makes the citrus lift more useful here than in the original.",
        "source": PRACTICE,
    },
],

"Ti' Punch": [
    {
        "name": "The lime disc, skin and all",
        "ingredient": "Limes",
        "measure": "1 thick disc",
        "note": "Cut a coin of lime with the peel attached, squeeze it and drop it in "
                "whole. The peel oil is a required part of the drink in Martinique, "
                "which is why it is cut this way rather than as a wedge.",
        "source": "Difford's Guide",
    },
],

"Suffering Bastard": [
    {
        "name": "Mint and cucumber",
        "ingredient": "Fresh mint",
        "measure": None,
        "note": "Joe Scialom's Cairo original is garnished with both. The cucumber is "
                "unusual and it is the thing that keeps a gin-and-brandy-and-ginger "
                "drink from feeling heavy.",
        "source": "Difford's Guide",
    },
],

"Fog Cutter": [
    {
        "name": "Mint sprig and orange",
        "ingredient": "Fresh mint",
        "measure": None,
        "note": "Trader Vic's, and it needs a big garnish because the sherry float on "
                "top is the first thing you taste and mint is what meets it.",
        "source": PRACTICE,
    },
],

"Chi-Chi": [
    {
        "name": "Pineapple wedge and cherry",
        "ingredient": "Maraschino cherries",
        "measure": None,
        "note": "A Pina Colada made with vodka, so it takes the Colada's garnish. "
                "Notch the pineapple so it sits on the rim.",
        "source": PRACTICE,
    },
],

"Blue Hurricane": [
    {
        "name": "Orange slice and cherry",
        "ingredient": "Maraschino cherries",
        "measure": None,
        "note": "The drink is bright blue and entirely about how it looks, so the "
                "garnish is not a detail here.",
        "source": PRACTICE,
    },
],

"Sex on the Beach": [
    {
        "name": "Orange slice",
        "ingredient": "Oranges",
        "measure": "1 slice",
        "note": "IBA garnish. Peach schnapps and two juices is a soft, sweet stack and "
                "the fresh orange on the rim is sharper than anything in the glass.",
        "source": "IBA official specification",
    },
],

"Lemon Drop": [
    {
        "name": "Sugar rim and lemon twist",
        "ingredient": "Sugar (white)",
        "measure": None,
        "note": "Rim half the glass. The whole drink is a lemon sweet in liquid form "
                "and the sugar rim is the reference; without it the name stops making "
                "sense.",
        "source": PRACTICE,
    },
],

"Long Island Iced Tea": [
    {
        "name": "Lemon wedge",
        "ingredient": "Lemons",
        "measure": "1 wedge",
        "note": "Squeezed in. Five spirits and cola is a lot of sweetness, and the "
                "lemon in the build is usually gone by the time the ice has moved.",
        "source": "IBA official specification",
    },
],

"Kalimotxo": [
    {
        "name": "Lemon wedge",
        "ingredient": "Lemons",
        "measure": "1 wedge",
        "note": "Common in Spain and it does real work: red wine and cola is sweeter "
                "than either on its own and the lemon is the only thing cutting it.",
        "source": PRACTICE,
    },
],

"New York Sour": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "Under the wine float, not on top of it, so you do not disturb the "
                "layer. The float is the drink's whole visual point.",
        "source": PRACTICE,
    },
],

"Bourbon Renewal": [
    {
        "name": "Lemon wheel",
        "ingredient": "Lemons",
        "measure": "1 wheel",
        "note": "Jeffrey Morgenthaler's drink. Creme de cassis and bourbon both lean "
                "sweet and dark, and the lemon keeps it a sour rather than a dessert.",
        "source": PRACTICE,
    },
],

"Brown Derby": [
    {
        "name": "Grapefruit twist",
        "ingredient": None,
        "measure": "1 strip",
        "note": "Grapefruit oil is much more assertive than grapefruit juice and this "
                "drink has plenty of honey syrup to stand up to it.",
        "source": PRACTICE,
    },
],

"Ward Eight": [
    {
        "name": "Orange slice and cherry",
        "ingredient": "Maraschino cherries",
        "measure": None,
        "note": "The traditional Boston serve. It is a Whiskey Sour with grenadine and "
                "the fruit garnish is part of how it was always presented.",
        "source": PRACTICE,
    },
],

"Between the Sheets": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "A Sidecar with rum added, so it takes the Sidecar's finish. Skip the "
                "sugar rim here; there is already more going on in the glass.",
        "source": PRACTICE,
    },
],

"Harvard": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "A brandy Manhattan in all but name. Cognac and sweet vermouth is "
                "rounder than rye and vermouth, so lemon rather than a cherry.",
        "source": PRACTICE,
    },
],

"Grasshopper": [
    {
        "name": "Grated chocolate or a mint leaf",
        "ingredient": "Fresh mint",
        "measure": None,
        "note": "Either, not both. The drink is mint and chocolate liqueur with cream "
                "and it is completely smooth, so the garnish is the only texture and "
                "the only aroma on it.",
        "source": PRACTICE,
    },
],

"Toasted Almond": [
    {
        "name": "Grated nutmeg",
        "ingredient": None,
        "measure": "a light grating",
        "note": "Amaretto, coffee liqueur and cream with nothing sharp in it anywhere. "
                "Nutmeg is the standard answer to a cream drink that has gone flat.",
        "source": PRACTICE,
    },
],

"Kir Royale": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "Cassis is very sweet and champagne hides it more than it cuts it. A "
                "twist over the top is the cheapest correction available.",
        "source": PRACTICE,
    },
],

"Mimosa": [
    {
        "name": "Orange twist",
        "ingredient": "Oranges",
        "measure": "1 strip",
        "note": "Expressed over the flute. Orange juice loses its aroma within minutes "
                "of being squeezed and the oil from the peel does not.",
        "source": PRACTICE,
    },
],

"Corpse Reviver No. 1": [
    {
        "name": "Orange twist",
        "ingredient": "Oranges",
        "measure": "1 strip",
        "note": "Cognac, calvados and sweet vermouth is an apple-and-brandy stack with "
                "no citrus in it at all. The twist is the only bright note available.",
        "source": PRACTICE,
    },
],

"American Beauty": [
    {
        "name": "Mint sprig",
        "ingredient": "Fresh mint",
        "measure": "1 sprig",
        "note": "Tucked beside the red wine float. It is a drink built to look like a "
                "rose and the mint reads as the leaf.",
        "source": PRACTICE,
    },
],

"Vodka Martini": [
    {
        "name": "Orange bitters",
        "ingredient": "Orange bitters",
        "measure": "1 dash",
        "note": "The gin Martini carried orange bitters as standard until the mid "
                "twentieth century. Vodka gives you even less to work with than gin "
                "does, so one dash buys more here than it does in the original.",
        "source": PRACTICE,
    },
],

"Vodka Gimlet": [
    {
        "name": "Lime wheel",
        "ingredient": "Limes",
        "measure": "1 wheel",
        "note": "On the rim rather than squeezed in, same as the gin version. The drink "
                "is already balanced and extra lime moves it.",
        "source": PRACTICE,
    },
],

"Kamikaze": [
    {
        "name": "Lime wheel",
        "ingredient": "Limes",
        "measure": "1 wheel",
        "note": "Vodka, triple sec and lime in equal parts is sharper than it sounds. "
                "The wheel is aromatic; do not squeeze it in as well.",
        "source": PRACTICE,
    },
],

"Cape Codder": [
    {
        "name": "Lime wedge",
        "ingredient": "Limes",
        "measure": "1 wedge",
        "note": "Squeezed in. Vodka and cranberry is two ingredients and one of them is "
                "sweetened juice, so the lime is most of what makes it drinkable.",
        "source": "IBA official specification",
    },
],

"Sea breeze": [
    {
        "name": "Lime wedge",
        "ingredient": "Limes",
        "measure": "1 wedge",
        "note": "Grapefruit and cranberry are both already tart, but sweet-tart. The "
                "lime is a different kind of sharp and it is what wakes the drink up.",
        "source": "IBA official specification",
    },
],

"Woo Woo": [
    {
        "name": "Lime wedge",
        "ingredient": "Limes",
        "measure": "1 wedge",
        "note": "Peach schnapps and cranberry with no citrus anywhere in the build. "
                "Squeeze the lime in or the drink is sweet all the way down.",
        "source": PRACTICE,
    },
],

"Screwdriver": [
    {
        "name": "Orange slice",
        "ingredient": "Oranges",
        "measure": "1 slice",
        "note": "Two ingredients, so there is nothing else to improve. Fresh orange on "
                "the rim is the entire difference between this and a glass of juice "
                "with vodka in it.",
        "source": "IBA official specification",
    },
],

"Caipirinha": [
    {
        "name": "Muddle skin-side down",
        "ingredient": None,
        "measure": None,
        "note": "Press the lime wedges with the skin facing the muddler so you are "
                "expressing oil rather than grinding pith. Overworked pith is why a "
                "home Caipirinha often turns bitter and a bar one does not.",
        "source": PRACTICE,
    },
],

"Canchanchara": [
    {
        "name": "Lime wedge",
        "ingredient": "Limes",
        "measure": "1 wedge",
        "note": "Honey rounds the drink off and the lime in the build gets buried in "
                "it. A wedge on the side lets you sharpen it to taste.",
        "source": PRACTICE,
    },
],

"Chet Baker": [
    {
        "name": "Orange twist",
        "ingredient": "Oranges",
        "measure": "1 strip",
        "note": "Sam Ross's drink. Rum, sweet vermouth, honey and Angostura is warm all "
                "the way through and orange oil is what gives it an edge.",
        "source": PRACTICE,
    },
],

"Oaxaca Old Fashioned": [
    {
        "name": "Flamed orange peel",
        "ingredient": "Oranges",
        "measure": "1 wide strip",
        "note": "Phil Ward's original calls for a flamed orange twist. Burnt orange oil "
                "and mezcal smoke are the same kind of note and they compound rather "
                "than compete.",
        "source": "Difford's Guide; Phil Ward's original",
    },
],

"Tequila Old Fashioned": [
    {
        "name": "Orange twist",
        "ingredient": "Oranges",
        "measure": "1 wide strip",
        "note": "Same finish as the whiskey original. Express it over the surface; "
                "agave and orange oil sit together very comfortably.",
        "source": PRACTICE,
    },
],

"Rum Old Fashioned": [
    {
        "name": "Orange twist",
        "ingredient": "Oranges",
        "measure": "1 wide strip",
        "note": "Aged rum carries more vanilla and caramel than bourbon does, so the "
                "orange oil has more to lift here, not less.",
        "source": PRACTICE,
    },
],

"Brandy Sour": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "Expressed over the top. Cognac is softer than whiskey and a Brandy "
                "Sour can read a little flat without something sharp above it.",
        "source": PRACTICE,
    },
],

"Tequila Sour": [
    {
        "name": "Lime wheel",
        "ingredient": "Limes",
        "measure": "1 wheel",
        "note": "Lime rather than lemon on the garnish, even if the build uses lemon. "
                "It points the drink back at the agave.",
        "source": PRACTICE,
    },
],

"Vodka Sour": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "Vodka contributes no aroma of its own, so a Vodka Sour is entirely "
                "lemon and sugar. The expressed oil is the only thing that gives it a "
                "top note.",
        "source": PRACTICE,
    },
],

"Nikolaschka": [
    {
        "name": "Bite the lemon first",
        "ingredient": None,
        "measure": None,
        "note": "The order is the drink: fold the sugared, coffee-topped lemon slice "
                "into your mouth, chew, then drink the brandy. Taken the other way "
                "round it is just brandy with a garnish.",
        "source": "Difford's Guide",
    },
],

"Airmail": [
    {
        "name": "Lime twist",
        "ingredient": "Limes",
        "measure": "1 strip",
        "note": "Honey and champagne both round a drink off. Lime oil is sharper than "
                "the lime juice already in the build and it keeps the top end awake.",
        "source": PRACTICE,
    },
],

"Bamboo": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "Sherry and dry vermouth is about 15% and very delicate. Anything "
                "heavier than expressed lemon oil would flatten it.",
        "source": "Difford's Guide",
    },
],

"Algonquin": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "The pineapple juice reads dry and slightly savoury in this drink "
                "rather than tropical, and lemon oil keeps it pointed that way.",
        "source": PRACTICE,
    },
],

"Cameron's Kick": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "Two whiskies and orgeat is a dense, nutty drink. Expressed lemon is "
                "the lightest possible correction and the right one.",
        "source": PRACTICE,
    },
],

"Pegu Club": [
    {
        "name": "Lime twist",
        "ingredient": "Limes",
        "measure": "1 strip",
        "note": "There are already two bitters and lime juice in the build. The twist "
                "is aromatic only, so express it and drop it rather than squeezing it.",
        "source": "Difford's Guide",
    },
],

"Pornstar Martini": [
    {
        "name": "Half a passion fruit",
        "ingredient": None,
        "measure": "1/2",
        "note": "Floated cut-side up on the surface. Douglas Ankrah's serve, and the "
                "shot of prosecco on the side is meant to be drunk alternately with the "
                "cocktail rather than poured in.",
        "source": "Difford's Guide",
    },
],

"Morning Glory Fizz": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "Scotch, absinthe and egg white with soda on top. The twist goes on the "
                "risen head where you will actually smell it.",
        "source": PRACTICE,
    },
],

"Oreo Mudslide": [
    {
        "name": "Crushed Oreo rim",
        "ingredient": None,
        "measure": None,
        "note": "Wet the rim with chocolate sauce and roll it in crushed cookie. The "
                "drink is a milkshake and it should be dressed like one; there is no "
                "understated version of this.",
        "source": PRACTICE,
    },
],

"Chatham Artillery Punch": [
    {
        "name": "Lemon wheels in the bowl",
        "ingredient": "Lemons",
        "measure": None,
        "note": "Float them on the ice block rather than putting one in each cup. A "
                "punch is served from the bowl and the aroma should come off the bowl.",
        "source": PRACTICE,
    },
],

"Brandy Cobbler": [
    {
        "name": "Fruit piled on the ice",
        "ingredient": "Oranges",
        "measure": None,
        "note": "Heap it on top of the crushed ice rather than burying it. The Cobbler "
                "is the drink that popularised the drinking straw in the 1800s, and the "
                "reason was the mound of fruit and ice you had to drink under.",
        "source": "Difford's Guide",
    },
],

"Brandy Daisy": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "A Daisy is a sour with a liqueur sweetener, so it sits closer to sweet "
                "than a plain sour does. Lemon oil on top is the correction.",
        "source": PRACTICE,
    },
],

"Bay Breeze": [
    {
        "name": "Lime wedge",
        "ingredient": "Limes",
        "measure": "1 wedge",
        "note": "Pineapple and cranberry are both sweet-tart with no real sharpness. "
                "The lime is the only thing in reach that provides it.",
        "source": PRACTICE,
    },
],

"Matador": [
    {
        "name": "Lime wedge",
        "ingredient": "Limes",
        "measure": "1 wedge",
        "note": "Tinned pineapple juice is noticeably sweeter than fresh. If that is "
                "what you are using, squeeze the lime in rather than perching it.",
        "source": PRACTICE,
    },
],

"Black Russian": [
    {
        "name": "Orange twist",
        "ingredient": "Oranges",
        "measure": "1 strip",
        "note": "Vodka and coffee liqueur, and one of those contributes no aroma at "
                "all. Orange oil sits on coffee well and gives the drink a top note it "
                "otherwise does not have.",
        "source": PRACTICE,
    },
],

"French Connection": [
    {
        "name": "Orange twist",
        "ingredient": "Oranges",
        "measure": "1 strip",
        "note": "Cognac and amaretto, both sweet-leaning, nothing sharp anywhere. Same "
                "problem and same fix as the Godfather.",
        "source": PRACTICE,
    },
],

}
