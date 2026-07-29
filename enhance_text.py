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
1. Nothing is invented. Every entry carries a `source` naming where the
   variation is documented. If no source can be named, the entry does not
   exist. This is the same rule as about_text.py and it exists for the same
   reason: this app already has a history of being confidently wrong (the
   Grape Soda label, the Vodka Cruiser tagged as vodka), and a plausible
   invented suggestion is indistinguishable from a real one to the reader.
2. Scope is bitters and garnish upgrades only. Rinses, floats, saline and egg
   white were considered and left out -- most are undocumented bar practice,
   which is a looser bar than this file uses.
3. An enhancement must not duplicate something the recipe already requires.
   The migration enforces this against the live database rather than trusting
   the list below, because the local bomu.db is a stale 100-recipe copy and
   cannot be trusted about what a live recipe contains.
4. Most recipes get nothing. 171 recipes, well under half have an entry. Same
   precedent as the 46 recipes with no tip: silence is a valid answer and a
   suggestion that says nothing is worse than no suggestion.

NOT INCLUDED, DELIBERATELY
--------------------------
The Negroni does not get orange bitters. It was the example that prompted this
work, and it does not clear the bar. Difford's Negroni is three ingredients and
no bitters; the orange-bitters versions (Kingston Negroni, Sweet Orange Negroni)
are separate named drinks, not a documented variation of the standard build.
The Negroni does get a garnish entry, because Difford's is emphatic about it.

FIELD REFERENCE
---------------
name        Shown in bold. Written as a thing you add, not a category.
ingredient  Exact key into the `ingredients` checklist table, or None. Drives
            the "in your stock" line. MUST already exist -- adding a checklist
            row is a real cost, it starts unticked for every existing user.
measure     Optional, right-aligned. "2 dashes", "1 wide strip".
note        Why you would bother, and what it changes. One or two sentences.
source      Where the variation is documented.
"""

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

}
