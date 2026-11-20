# -*- coding: utf-8 -*-
"""
"Make it your own" copy: genuine optional bartender riffs and garnish
upgrades for recipes that benefit from one. Loaded by migrate_enhancements.py,
which writes it into the `recipe_enhancements` table.

WHY THIS IS NOT IN recipe_ingredients
-------------------------------------
`recipe_ingredients` holds the recipe itself (and its classic optional garnishes).
`recipe_enhancements` holds optional bartender twists and finishing touches that
aren't already listed in the Pour List, How to mix steps, or Worth knowing tip.

The matcher never reads this table. Nothing in here can change what anybody can
make, which is both the design and the way the migration is verified.

RULES THIS FILE FOLLOWS
-----------------------
1. Nothing is invented, and the reader is always told which kind of claim they
   are reading. Every entry carries a `source`:
       a named source   "Difford's Guide", "IBA official specification", etc.
       PRACTICE         "Common bar practice, not a printed spec" (renders as
                        "Bartender's habit" on the recipe page).
2. Scope is genuine optional riffs, bitters, and garnish upgrades only. Never
   anti-riffs, core techniques already in the steps/tip, or ingredients already
   shown in `recipe_ingredients`.
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

# ============================ Bitters ======================================

"Manhattan": [
    {
        "name": "Orange bitters",
        "ingredient": "Orange bitters",
        "measure": "1 dash",
        "note": "Swap one dash of the Angostura for orange bitters, or use a dash "
                "of each. It brings out a warm orange note in the sweet vermouth "
                "without making the drink any sweeter.",
        "source": "Difford's Guide; The PDT Cocktail Book",
    },
],

"Old Fashioned": [
    {
        "name": "Orange bitters",
        "ingredient": "Orange bitters",
        "measure": "1 dash",
        "note": "Add a dash alongside the Angostura instead of replacing it. "
                "It ties the whiskey to the orange peel on top so you get citrus "
                "all the way down the glass.",
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
                "bitters gets you very close to that original spiced citrus finish.",
        "source": "Difford's Guide",
    },
],

# ============================ Negroni & Cousins ============================

"Negroni": [
    {
        "name": "Orange bitters",
        "ingredient": "Orange bitters",
        "measure": "1 dash",
        "note": "Not part of the classic recipe, though plenty of bartenders add a "
                "dash before stirring. It puts a little orange spice into the drink "
                "itself, not just on top.",
        "source": PRACTICE,
    },
    {
        "name": "Orange twist or slice",
        "ingredient": "Oranges",
        "measure": None,
        "note": "Stick with orange rather than lemon. Squeezing the peel over the "
                "glass leaves fresh orange oil on top, which softens the first hit "
                "of Campari.",
        "source": "Difford's Guide",
    },
],

"Rosita": [
    {
        "name": "Orange twist",
        "ingredient": "Oranges",
        "measure": "1 strip",
        "note": "If you want a rounder aroma than the standard lemon twist, use a "
                "strip of orange peel instead. Orange oil suits the Campari and "
                "both vermouths really well.",
        "source": PRACTICE,
    },
],

# ============================ Spirit-Forward Classics ======================

"Black Russian": [
    {
        "name": "Orange twist",
        "ingredient": "Oranges",
        "measure": "1 strip",
        "note": "Vodka stays in the background here and lets the coffee liqueur lead. "
                "Squeezing a strip of orange peel over the ice adds an orange-and-espresso "
                "aroma that fits right in.",
        "source": PRACTICE,
    },
],

"French Connection": [
    {
        "name": "Orange twist",
        "ingredient": "Oranges",
        "measure": "1 strip",
        "note": "Cognac and amaretto together are quite rich and sweet. Expressing "
                "an orange peel over the ice cuts through the almond sweetness with "
                "fresh citrus oil.",
        "source": PRACTICE,
    },
],

"Godfather": [
    {
        "name": "Orange twist",
        "ingredient": "Oranges",
        "measure": "1 strip",
        "note": "Squeeze a strip of orange peel over the glass and drop it in. "
                "Orange oil bridges the gap between smoky Scotch and sweet almond "
                "liqueur.",
        "source": PRACTICE,
    },
],

"Harvard": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "Squeeze a strip of lemon peel over the drink, either instead of "
                "the cherry or beside it. Cognac is softer than rye, and the lemon "
                "oil sharpens the finish.",
        "source": PRACTICE,
    },
],

# ============================ Whiskey & Brandy Sours =======================

"Brandy Daisy": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "Grenadine makes a Daisy sweeter than a standard sour. Giving a "
                "lemon peel a quick twist over the glass puts fresh lemon scent "
                "right on top.",
        "source": PRACTICE,
    },
],

"Brandy Sour": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "Squeeze a strip of lemon peel over the foam right before serving. "
                "Brandy is rounder and softer than whiskey, so a bit of peel oil "
                "on top gives it a cleaner edge.",
        "source": PRACTICE,
    },
],

"Cameron's Kick": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "Two whiskies and almond orgeat make a fairly rich sour. A thin "
                "lemon twist expressed over the top keeps the nose fresh and "
                "citrusy.",
        "source": PRACTICE,
    },
],

"Gold Rush": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "Honey makes this warmer and fuller than a standard Whiskey Sour. "
                "A quick squeeze of lemon peel over the ice adds a sharp citrus "
                "scent to the first sip.",
        "source": PRACTICE,
    },
],

"Vodka Sour": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "Vodka has almost no aroma of its own, especially under a layer of "
                "egg-white foam. Squeezing a lemon peel over the top gives the "
                "drink a clean lemon smell.",
        "source": PRACTICE,
    },
],

"Ward Eight": [
    {
        "name": "Brandied cherry",
        "ingredient": "Maraschino cherries",
        "measure": "1",
        "note": "Drop a dark brandied cherry into the glass alongside the orange "
                "twist. It fits naturally with the pomegranate grenadine and gives "
                "you a boozy bite at the end.",
        "source": PRACTICE,
    },
],

# ============================ Gin, Vodka & Agave Sours / Stirred ===========

"Algonquin": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "Express a strip of lemon peel over the top before serving. It "
                "leans into the dry side of the rye and vermouth and keeps the "
                "pineapple from smelling too sweet.",
        "source": PRACTICE,
    },
],

"Bacardi Cocktail": [
    {
        "name": "Lime wedge",
        "ingredient": "Limes",
        "measure": "1 wedge",
        "note": "Grenadine makes this slightly sweeter than a plain Daiquiri. "
                "Resting a lime wedge on the rim lets you squeeze in a little "
                "extra acid if your grenadine runs sweet.",
        "source": PRACTICE,
    },
],

"Bramble": [
    {
        "name": "Lemon slice and a blackberry",
        "ingredient": "Lemons",
        "measure": None,
        "note": "Dick Bradsell's original London garnish is a fresh lemon slice "
                "and a ripe blackberry set directly on the crushed ice where the "
                "blackberry liqueur is poured.",
        "source": "Difford's Guide; Dick Bradsell's original",
    },
],

"Clover Club": [
    {
        "name": "Raspberries on a stick",
        "ingredient": None,
        "measure": "2 or 3",
        "note": "Skewer two or three fresh raspberries on a pick and lay it across "
                "the rim. They sit nicely over the pink foam and echo the berry "
                "sweetness inside.",
        "source": "Difford's Guide",
    },
],

"Corpse Reviver #2": [
    {
        "name": "Orange twist",
        "ingredient": "Oranges",
        "measure": "1 strip",
        "note": "Squeeze a strip of orange peel over the coupe and discard it, or "
                "drop it in. The orange oil picks up the Cointreau and sits nicely "
                "over the absinthe rinse.",
        "source": "Difford's Guide; The Savoy Cocktail Book",
    },
],

"Cosmopolitan": [
    {
        "name": "Flamed orange twist",
        "ingredient": "Oranges",
        "measure": "1 strip",
        "note": "Hold a wide strip of orange peel near a lit match and pinch it "
                "so the oils spark across the top of the drink. The toasted orange "
                "scent makes a huge difference over the cranberry.",
        "source": "Difford's Guide",
    },
],

"Daiquiri": [
    {
        "name": "Lime wheel",
        "ingredient": "Limes",
        "measure": "1 wheel",
        "note": "Clip a thin lime wheel to the rim instead of a wedge. The acid "
                "is already balanced in the shaker, so you just want the smell of "
                "fresh lime peel without extra juice.",
        "source": "IBA official specification",
    },
],

"Hemingway Daiquiri": [
    {
        "name": "Lime wheel",
        "ingredient": "Limes",
        "measure": "1 wheel",
        "note": "This drink is already plenty tart from the lime and grapefruit. "
                "Use a thin wheel on the rim for aroma rather than a wedge meant "
                "for squeezing.",
        "source": "Difford's Guide",
    },
],

"Kamikaze": [
    {
        "name": "Lime wheel",
        "ingredient": "Limes",
        "measure": "1 wheel",
        "note": "Equal parts vodka, triple sec, and lime juice is already sharp "
                "enough. A thin lime wheel on the rim adds fresh peel aroma without "
                "throwing off the ratio.",
        "source": PRACTICE,
    },
],

"Matador": [
    {
        "name": "Lime wedge",
        "ingredient": "Limes",
        "measure": "1 wedge",
        "note": "Canned pineapple juice varies a lot in sweetness. Putting a fresh "
                "lime wedge on the rim lets you add another squeeze of lime if the "
                "pineapple tastes heavy.",
        "source": PRACTICE,
    },
],

"Pegu Club": [
    {
        "name": "Lime twist",
        "ingredient": "Limes",
        "measure": "1 strip",
        "note": "The lime juice and two kinds of bitters already do the work in "
                "the glass. Squeeze a strip of lime peel over the top for a little "
                "extra citrus oil on the nose.",
        "source": "Difford's Guide",
    },
],

"Pink Lady": [
    {
        "name": "Brandied cherry",
        "ingredient": "Maraschino cherries",
        "measure": "1",
        "note": "Drop a dark brandied cherry into the bottom of the coupe or set "
                "it on a pick. A proper dark cherry suits the gin and cream much "
                "better than a neon-red jar cherry.",
        "source": PRACTICE,
    },
],

"Tequila Sour": [
    {
        "name": "Lime wheel",
        "ingredient": "Limes",
        "measure": "1 wheel",
        "note": "Even though the drink is shaken with lemon juice, a thin lime "
                "wheel on the rim smells right at home with the tequila.",
        "source": PRACTICE,
    },
],

"The Last Word": [
    {
        "name": "Brandied cherry",
        "ingredient": "Maraschino cherries",
        "measure": "1",
        "note": "Set a dark brandied cherry in the bottom of the coupe before "
                "straining. It ties in with the maraschino liqueur and gives you "
                "a nice final bite after the herbal finish.",
        "source": "Difford's Guide",
    },
],

"White Lady": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "Gin, Cointreau, and lemon juice shake up very clean but don't "
                "give off much scent once chilled. Squeezing a fresh lemon peel "
                "over the glass fixes that right away.",
        "source": PRACTICE,
    },
],

# ============================ Champagne & Spritzes =========================

"Airmail": [
    {
        "name": "Lime twist",
        "ingredient": "Limes",
        "measure": "1 strip",
        "note": "Honey and Champagne round out the rum and lime. Twisting a strip "
                "of lime peel over the flute puts fresh citrus oil right into the "
                "rising bubbles.",
        "source": PRACTICE,
    },
],

"French 75": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 long strip",
        "note": "Squeeze a long spiral of lemon peel over the top and drop it into "
                "the flute. As the Champagne bubbles rise, they carry the lemon "
                "oil straight up to the rim.",
        "source": "IBA official specification",
    },
],

"Kir Royale": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "Crème de cassis is rich and sweet on its own. Expressing a strip "
                "of lemon peel over the flute adds a dry citrus scent without "
                "souring the wine.",
        "source": PRACTICE,
    },
],

"Mimosa": [
    {
        "name": "Orange twist",
        "ingredient": "Oranges",
        "measure": "1 strip",
        "note": "Even fresh-squeezed orange juice loses the smell of the peel "
                "pretty quickly. Twisting a strip of orange zest over the flute "
                "puts that aroma back on top.",
        "source": PRACTICE,
    },
],

"Morning Glory Fizz": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "Between the Scotch, the absinthe, and the egg white, a lot is "
                "going on in this glass. Expressing a lemon peel over the foam "
                "keeps the first smell clean and fresh.",
        "source": PRACTICE,
    },
],

"Ramos Gin Fizz": [
    {
        "name": "Orange flower water on the foam",
        "ingredient": None,
        "measure": "1 drop",
        "note": "If you have orange flower water in the cupboard, put one drop "
                "directly on top of the foam head at the end. You smell the floral "
                "note before every sip.",
        "source": "Difford's Guide",
    },
],

# ============================ Highballs, Mules & Savory ====================

"Bloody Mary": [
    {
        "name": "Celery salt rim",
        "ingredient": "Salt",
        "measure": None,
        "note": "Rub a cut lemon or lime around the rim and dip it in celery salt "
                "before building the drink. It gives every sip a savoury edge "
                "without overloading the tomato juice with extra salt.",
        "source": "IBA official specification",
    },
    {
        "name": "Black pepper on top",
        "ingredient": "Pepper",
        "measure": "a good grind",
        "note": "Add a fresh crack of black pepper across the top of the ice at "
                "the very end. You smell the pepper immediately rather than losing "
                "it all inside the tomato mix.",
        "source": "IBA official specification",
    },
],

"Gin And Tonic": [
    {
        "name": "Angostura, for a Pink Gin and Tonic",
        "ingredient": "Angostura bitters",
        "measure": "2 dashes",
        "note": "Add two good dashes of Angostura over the ice before pouring the "
                "tonic. It turns the drink pale pink and adds a dry clove-and-cinnamon "
                "note that works great with gin.",
        "source": PRACTICE,
    },
],

"Greyhound": [
    {
        "name": "Grapefruit twist",
        "ingredient": None,
        "measure": "1 strip",
        "note": "If you want to keep the rim unsalted, peel a strip of grapefruit "
                "zest and squeeze it over the ice. The peel oil adds a bitter "
                "citrus smell that juice alone doesn't have.",
        "source": PRACTICE,
    },
],

"Mexican Mule": [
    {
        "name": "Mint sprig",
        "ingredient": "Fresh mint",
        "measure": "1 sprig",
        "note": "Slap a sprig of fresh mint gently against your hand and tuck it "
                "in next to the lime wedge. Mint and ginger beer smell great "
                "together over tequila.",
        "source": PRACTICE,
    },
],

"Moscow Mule": [
    {
        "name": "Mint sprig and lime wedge",
        "ingredient": "Fresh mint",
        "measure": None,
        "note": "Tuck a sprig of fresh mint right next to a lime wedge in the ice. "
                "You can't see the drink through a copper mug, so the smell of "
                "mint and lime is what hits you first.",
        "source": "IBA official specification",
    },
],

"Screwdriver": [
    {
        "name": "Orange slice",
        "ingredient": "Oranges",
        "measure": "1 slice",
        "note": "Since there are only two ingredients in the glass, putting a fresh "
                "orange slice or wheel on the rim gives you real peel aroma and "
                "makes it feel less like plain breakfast juice.",
        "source": "IBA official specification",
    },
],

"Sea breeze": [
    {
        "name": "Lime wedge",
        "ingredient": "Limes",
        "measure": "1 wedge",
        "note": "Cranberry and grapefruit can still taste fairly sweet depending "
                "on the carton. A fresh lime wedge on the rim lets you squeeze in "
                "a bit more tartness.",
        "source": "IBA official specification",
    },
],

# ============================ Tiki, Tropical & Rum =========================

"Blue Hurricane": [
    {
        "name": "Orange slice and cherry",
        "ingredient": "Maraschino cherries",
        "measure": None,
        "note": "An electric-blue rum drink is already leaning into vacation mode. "
                "Pinning an orange slice and a cherry to the rim finishes the classic "
                "hurricane-glass look.",
        "source": PRACTICE,
    },
],

"Jungle Bird": [
    {
        "name": "Pineapple wedge",
        "ingredient": None,
        "measure": "1 wedge",
        "note": "If you carved a fresh pineapple, notch a wedge onto the rim. "
                "The sweet fruit smell works nicely above the bitter Campari and "
                "dark rum.",
        "source": "Difford's Guide",
    },
],

"Mai Tai": [
    {
        "name": "Squeezed lime shell and mint",
        "ingredient": "Fresh mint",
        "measure": None,
        "note": "Trader Vic's original garnish was half a juiced lime shell set "
                "dome-side up on the crushed ice with a sprig of fresh mint tucked "
                "beside it, meant to look like a little island and palm tree.",
        "source": "Trader Vic's original specification; IBA",
    },
],

"Mint Julep": [
    {
        "name": "Big mint sprig",
        "ingredient": None,
        "measure": "1 generous sprig",
        "note": "Give a thick bunch of mint a gentle slap between your hands and "
                "push it into the crushed ice right beside the straw so your nose "
                "is buried in mint whenever you take a sip.",
        "source": "Difford's Guide",
    },
],

"Penicillin": [
    {
        "name": "Candied ginger",
        "ingredient": None,
        "measure": "1 piece",
        "note": "Spear a piece of crystallized ginger on a pick and rest it across "
                "the rim. It matches the ginger and peat smoke inside and gives "
                "you a chewy, spicy bite at the end.",
        "source": "Sam Ross, Milk & Honey; Difford's Guide",
    },
],

"Planter's Punch": [
    {
        "name": "Grated nutmeg",
        "ingredient": None,
        "measure": "a light grating",
        "note": "Grate a little fresh nutmeg across the top of the ice before "
                "serving. Nutmeg and dark rum are an old Caribbean pairing, and "
                "the dry spice keeps the fruit juice from smelling flat.",
        "source": "Difford's Guide",
    },
],

"Tequila Sunrise": [
    {
        "name": "Orange slice and cherry",
        "ingredient": "Maraschino cherries",
        "measure": None,
        "note": "An orange slice and a cherry on the rim match the red-and-orange "
                "layers in the glass and give the drink its classic 1970s look.",
        "source": "IBA official specification",
    },
],

"Zombie": [
    {
        "name": "Mint sprig",
        "ingredient": "Fresh mint",
        "measure": "1 sprig",
        "note": "Push a fresh sprig of mint into the crushed ice right next to the "
                "straw. With three rums plus overproof 151 in the glass, the smell "
                "of fresh mint lightens the first impression.",
        "source": "Difford's Guide",
    },
],

# ============================ Coffee & Dessert =============================

"Grasshopper": [
    {
        "name": "Grated chocolate or a mint leaf",
        "ingredient": "Fresh mint",
        "measure": None,
        "note": "Shave a little dark chocolate over the top or float a single fresh "
                "mint leaf in the centre. Either one leans into the mint-chocolate "
                "flavour and dresses up the green coupe.",
        "source": PRACTICE,
    },
],

"Irish Coffee": [
    {
        "name": "Grated nutmeg",
        "ingredient": None,
        "measure": "a light grating",
        "note": "Some bartenders grate a little fresh nutmeg onto the cold cream "
                "collar without stirring it in. The Buena Vista in San Francisco "
                "serves theirs plain, so try it once and see which you prefer.",
        "source": "Difford's Guide (listed as an optional garnish)",
    },
],

"Oreo Mudslide": [
    {
        "name": "Crushed Oreo rim",
        "ingredient": None,
        "measure": None,
        "note": "Dip the rim of the glass in chocolate sauce and roll it in crushed "
                "Oreo crumbs before pouring. If you're already blending ice cream "
                "and cookies with vodka, you might as well commit.",
        "source": PRACTICE,
    },
],

"Toasted Almond": [
    {
        "name": "Grated nutmeg",
        "ingredient": None,
        "measure": "a light grating",
        "note": "Amaretto, coffee liqueur, and cream are sweet and heavy on their "
                "own. A quick grating of fresh nutmeg on top adds a dry, woody "
                "spice that suits the almond.",
        "source": PRACTICE,
    },
],

}
