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
2. Scope is genuine optional riffs, bitters, and garnish upgrades only—never
   anti-riffs, core techniques already in the steps/tip, or ingredients already
   shown in `recipe_ingredients`.
3. Every `ingredient` key must already exist in the `ingredients` checklist table
   (49 rows) and must NOT duplicate anything in that recipe's `recipe_ingredients`.
4. Plain English for someone at home: 1–2 warm, inviting sentences saying what to
   add and why it makes the glass even better. No source names inside `note`.

FIELD REFERENCE
---------------
name        Shown in bold. Written as a concrete garnish or addition.
ingredient  Exact key into `ingredients` checklist table, or None. Drives the
            "In your bar" / "Needs X" tag.
measure     Optional, right-aligned ("1 dash", "1 wide strip", etc.).
note        What to do and why it elevates the drink.
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
        "note": "Swap out one dash of Angostura for orange bitters, or add a dash "
                "alongside it. It lifts the sweet vermouth with bright citrus "
                "spice without nudging the drink any sweeter.",
        "source": "Difford's Guide; The PDT Cocktail Book",
    },
],

"Old Fashioned": [
    {
        "name": "Orange bitters",
        "ingredient": "Orange bitters",
        "measure": "1 dash",
        "note": "Dash it in right beside the Angostura rather than replacing it. "
                "It echoes the fresh orange peel on top so citrus runs gently "
                "all the way through the whiskey.",
        "source": "Difford's Guide",
    },
],

"Martinez": [
    {
        "name": "Orange bitters",
        "ingredient": "Orange bitters",
        "measure": "1 dash",
        "note": "Early Martinez specs relied on a heritage bitters brand that "
                "vanished for much of the twentieth century. A dash of orange "
                "bitters brings back that lively, rounded warmth.",
        "source": "Difford's Guide",
    },
],

# ============================ Negroni & Cousins ============================

"Negroni": [
    {
        "name": "Orange bitters",
        "ingredient": "Orange bitters",
        "measure": "1 dash",
        "note": "A bartender's quiet upgrade: one dash stirred straight into the "
                "glass weaves warm spiced citrus through every sip rather than "
                "resting only on the aroma.",
        "source": PRACTICE,
    },
    {
        "name": "Orange twist or slice",
        "ingredient": "Oranges",
        "measure": None,
        "note": "Reach for orange, not lemon—squeezing a fresh peel over the glass "
                "lays bright oils across the surface that greet your nose first "
                "and tame Campari's sharpest edge.",
        "source": "Difford's Guide",
    },
],

"Rosita": [
    {
        "name": "Orange twist",
        "ingredient": "Oranges",
        "measure": "1 strip",
        "note": "Try trading the lemon garnish for a strip of orange peel instead. "
                "It leans into this tequila Negroni's bitter core and softens the "
                "Campari on your nose.",
        "source": PRACTICE,
    },
],

# ============================ Spirit-Forward Classics ======================

"Black Russian": [
    {
        "name": "Orange twist",
        "ingredient": "Oranges",
        "measure": "1 strip",
        "note": "Vodka keeps a low profile here, leaving coffee liqueur doing most "
                "of the talking. A twist of orange peel brings warm citrus aroma "
                "that pairs naturally with dark roast.",
        "source": PRACTICE,
    },
],

"French Connection": [
    {
        "name": "Orange twist",
        "ingredient": "Oranges",
        "measure": "1 strip",
        "note": "Cognac and amaretto are silky, nutty, and rich all the way down. "
                "Squeezing an orange peel over the ice brightens the glass with a "
                "lively citrus snap.",
        "source": PRACTICE,
    },
],

"Godfather": [
    {
        "name": "Orange twist",
        "ingredient": "Oranges",
        "measure": "1 strip",
        "note": "Smoky Scotch and sweet almond amaretto taste richer together when "
                "crowned with orange oil—it lifts the heavy sweetness without "
                "getting in the whisky's way.",
        "source": PRACTICE,
    },
],

"Harvard": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "Alongside or instead of the cherry, squeeze a strip of lemon peel "
                "across the top. Cognac runs rounder than rye, so a snap of "
                "lemon oil wakes everything up.",
        "source": PRACTICE,
    },
],

# ============================ Whiskey & Brandy Sours =======================

"Brandy Daisy": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "Because grenadine tips a Daisy sweeter than a plain sour, giving "
                "a lemon peel a quick twist over the top keeps the bright citrus "
                "aroma front and centre.",
        "source": PRACTICE,
    },
],

"Brandy Sour": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "Give a strip of lemon peel a squeeze over the finished foam. "
                "Brandy is softer than bourbon or rye, and that bright oil adds "
                "an extra crisp spark.",
        "source": PRACTICE,
    },
],

"Cameron's Kick": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "Two whiskies and creamy almond orgeat make a rich, nutty pour. A "
                "thin lemon twist over the top brings just enough crisp citrus "
                "sparkle without stealing the show.",
        "source": PRACTICE,
    },
],

"Gold Rush": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "Golden honey gives a Whiskey Sour plush warmth, and a quick twist "
                "of fresh lemon peel on top keeps that rich first sip feeling "
                "bright and crisp.",
        "source": PRACTICE,
    },
],

"Vodka Sour": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "Because vodka keeps completely quiet on aroma, squeezing a fresh "
                "lemon peel over the top wraps every sip in lively citrus oils.",
        "source": PRACTICE,
    },
],

"Ward Eight": [
    {
        "name": "Brandied cherry",
        "ingredient": "Maraschino cherries",
        "measure": "1",
        "note": "Drop a dark brandied cherry into the coupe alongside the orange "
                "twist. It echoes the ruby grenadine and leaves a sweet little "
                "finale at the bottom.",
        "source": PRACTICE,
    },
],

# ============================ Gin, Vodka & Agave Sours / Stirred ===========

"Algonquin": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "Give a lemon peel a quick squeeze over the foamy top before "
                "setting it down. It underlines the dry, savoury character of the "
                "rye and pineapple rather than tipping sweet.",
        "source": PRACTICE,
    },
],

"Bacardi Cocktail": [
    {
        "name": "Lime wedge",
        "ingredient": "Limes",
        "measure": "1 wedge",
        "note": "With ruby grenadine adding extra richness to the Daiquiri build, "
                "perching a fresh lime wedge on the rim lets you dial up the tart "
                "zip to taste.",
        "source": PRACTICE,
    },
],

"Bramble": [
    {
        "name": "Lemon slice and a blackberry",
        "ingredient": "Lemons",
        "measure": None,
        "note": "The classic London finish: nestle a fresh lemon slice and a "
                "ripe blackberry right on top of the crushed ice where the ruby "
                "liqueur trickles downward.",
        "source": "Difford's Guide; Dick Bradsell's original",
    },
],

"Clover Club": [
    {
        "name": "Raspberries on a stick",
        "ingredient": None,
        "measure": "2 or 3",
        "note": "Thread two or three fresh raspberries across the rim on a cocktail "
                "pick. They give the silky foam a lovely berry aroma and nod to "
                "the drink's classic raspberry roots.",
        "source": "Difford's Guide",
    },
],

"Corpse Reviver #2": [
    {
        "name": "Orange twist",
        "ingredient": "Oranges",
        "measure": "1 strip",
        "note": "Squeeze a wide orange peel gently across the rim before sipping. "
                "Those sunny oils join the Cointreau and make this bright morning "
                "reviver smell irresistible.",
        "source": "Difford's Guide; The Savoy Cocktail Book",
    },
],

"Cosmopolitan": [
    {
        "name": "Flamed orange twist",
        "ingredient": "Oranges",
        "measure": "1 strip",
        "note": "Pinch a wide strip of orange peel across a lit match over the "
                "glass so the mist flares into toasted citrus oil. It wakes up "
                "the glass and keeps cranberry from running the show.",
        "source": "Difford's Guide",
    },
],

"Daiquiri": [
    {
        "name": "Lime wheel",
        "ingredient": "Limes",
        "measure": "1 wheel",
        "note": "Perch a neat lime wheel on the rim rather than squeezing in extra "
                "juice. The drink is already balanced in the shaker, and the "
                "wheel gives you crisp lime aroma before every sip.",
        "source": "IBA official specification",
    },
],

"Hemingway Daiquiri": [
    {
        "name": "Lime wheel",
        "ingredient": "Limes",
        "measure": "1 wheel",
        "note": "This classic is already brisk and tart. Rest a thin lime wheel on "
                "the rim purely for fragrant citrus aroma—unless you deliberately "
                "crave an extra squeeze.",
        "source": "Difford's Guide",
    },
],

"Kamikaze": [
    {
        "name": "Lime wheel",
        "ingredient": "Limes",
        "measure": "1 wheel",
        "note": "With equal parts vodka, triple sec, and fresh lime, a tidy lime "
                "wheel on the rim brings fresh aroma without tilting the sharp "
                "balance already inside.",
        "source": PRACTICE,
    },
],

"Matador": [
    {
        "name": "Lime wedge",
        "ingredient": "Limes",
        "measure": "1 wedge",
        "note": "Canned pineapple juice leans much sweeter than fresh-pressed. Tuck "
                "a lime wedge on the rim so you can squeeze in an extra tart kick "
                "if needed.",
        "source": PRACTICE,
    },
],

"Pegu Club": [
    {
        "name": "Lime twist",
        "ingredient": "Limes",
        "measure": "1 strip",
        "note": "Lime juice and two bitters already handle the flavour inside the "
                "glass. Squeeze a fresh strip of lime peel over the top and drop "
                "it in for crisp aromatic lift.",
        "source": "Difford's Guide",
    },
],

"Pink Lady": [
    {
        "name": "Brandied cherry",
        "ingredient": "Maraschino cherries",
        "measure": "1",
        "note": "Gently rest a dark brandied cherry atop the pink foam so it "
                "stays afloat. Its deep fruit richness balances the silky cream "
                "far better than a bright neon cherry.",
        "source": PRACTICE,
    },
],

"Tequila Sour": [
    {
        "name": "Lime wheel",
        "ingredient": "Limes",
        "measure": "1 wheel",
        "note": "Even though this sour shakes with lemon juice, perching a thin "
                "lime wheel on the rim nods gently back toward the agave base.",
        "source": PRACTICE,
    },
],

"The Last Word": [
    {
        "name": "Brandied cherry",
        "ingredient": "Maraschino cherries",
        "measure": "1",
        "note": "Drop one dark brandied cherry into the pale green glass. It picks "
                "up the maraschino liqueur inside and offers a jewel-like sweet "
                "reward at the bottom.",
        "source": "Difford's Guide",
    },
],

"White Lady": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "Gin, Cointreau, and lemon pour silky and sharp, yet keep a quiet "
                "nose. One squeeze of fresh lemon peel across the top adds instant "
                "sunlit brightness.",
        "source": PRACTICE,
    },
],

# ============================ Champagne & Spritzes =========================

"Airmail": [
    {
        "name": "Lime twist",
        "ingredient": "Limes",
        "measure": "1 strip",
        "note": "Honey and bubbly Champagne soften a cocktail nicely, and a quick "
                "squeeze of lime peel over the flute adds sharp aromatic zing "
                "through the fizz.",
        "source": PRACTICE,
    },
],

"French 75": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 long strip",
        "note": "For the classic champagne-flute finish, drop a long spiral of "
                "lemon peel straight into the glass—every rising bubble carries "
                "bright citrus oil right to your nose.",
        "source": "IBA official specification",
    },
],

"Kir Royale": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "Blackcurrant crème de cassis brings lush berry sweetness—one crisp "
                "squeeze of lemon peel over the flute lifts the bubbles and keeps "
                "it light.",
        "source": PRACTICE,
    },
],

"Mimosa": [
    {
        "name": "Orange twist",
        "ingredient": "Oranges",
        "measure": "1 strip",
        "note": "Orange juice sheds much of its bright scent soon after pressing. "
                "Squeezing a fresh ribbon of peel over the flute brings back that "
                "just-picked orchard aroma.",
        "source": PRACTICE,
    },
],

"Morning Glory Fizz": [
    {
        "name": "Lemon twist",
        "ingredient": "Lemons",
        "measure": "1 strip",
        "note": "With smoky Scotch, absinthe, and a tall meringue cap of foam, "
                "resting a bright lemon twist right on top guarantees you smell "
                "fresh citrus before every sip.",
        "source": PRACTICE,
    },
],

"Ramos Gin Fizz": [
    {
        "name": "Orange flower water on the foam",
        "ingredient": None,
        "measure": "1 drop",
        "note": "The classic New Orleans finishing touch: dot a single drop of "
                "orange flower water onto that towering foam cap so every sip "
                "opens like orange blossoms.",
        "source": "Difford's Guide",
    },
],

# ============================ Highballs, Mules & Savory ====================

"Bloody Mary": [
    {
        "name": "Celery salt rim",
        "ingredient": "Salt",
        "measure": None,
        "note": "Rim the glass with celery salt before pouring. It seasons every "
                "mouthful evenly so the tomato juice sings right away without "
                "chasing it with extra hot sauce.",
        "source": "IBA official specification",
    },
    {
        "name": "Black pepper on top",
        "ingredient": "Pepper",
        "measure": "a good grind",
        "note": "Give it a generous fresh grind right over the ice at the end "
                "instead of burying it inside—that warm cracked-pepper aroma "
                "makes the whole glass taste savourier.",
        "source": "IBA official specification",
    },
],

"Gin And Tonic": [
    {
        "name": "Angostura, for a Pink Gin and Tonic",
        "ingredient": "Angostura bitters",
        "measure": "2 dashes",
        "note": "Shake two dashes of Angostura over the ice before pouring your "
                "tonic—it tints the glass rosy pink and folds warm baking spice "
                "right into the juniper.",
        "source": PRACTICE,
    },
],

"Greyhound": [
    {
        "name": "Grapefruit twist",
        "ingredient": None,
        "measure": "1 strip",
        "note": "Skip the salt rim—keep it a clean Greyhound and squeeze a rosy "
                "grapefruit peel over the top instead for extra tangy citrus "
                "perfume.",
        "source": PRACTICE,
    },
],

"Mexican Mule": [
    {
        "name": "Mint sprig",
        "ingredient": "Fresh mint",
        "measure": "1 sprig",
        "note": "Tuck a lively sprig of mint beside the lime wedge. Inside a "
                "chilled copper mug, fresh green mint and fiery ginger greet "
                "your nose before the first sip.",
        "source": PRACTICE,
    },
],

"Moscow Mule": [
    {
        "name": "Mint sprig and lime wedge",
        "ingredient": "Fresh mint",
        "measure": None,
        "note": "Pair a bright lime wedge with a fresh sprig of mint on top. A "
                "copper mug hides what's inside, so your garnish delivers the "
                "first impression.",
        "source": "IBA official specification",
    },
],

"Screwdriver": [
    {
        "name": "Orange slice",
        "ingredient": "Oranges",
        "measure": "1 slice",
        "note": "With just vodka and juice inside the glass, tucking a thick, "
                "fresh orange slice onto the rim makes it feel like a proper "
                "cocktail instead of breakfast in a hurry.",
        "source": "IBA official specification",
    },
],

"Sea breeze": [
    {
        "name": "Lime wedge",
        "ingredient": "Limes",
        "measure": "1 wedge",
        "note": "Cranberry and grapefruit both bring sweet-tart fruit, so a bright "
                "squeeze of lime on top cuts through and gives the whole tall "
                "glass an extra crisp snap.",
        "source": "IBA official specification",
    },
],

# ============================ Tiki, Tropical & Rum =========================

"Blue Hurricane": [
    {
        "name": "Orange slice and cherry",
        "ingredient": "Maraschino cherries",
        "measure": None,
        "note": "Since this neon-turquoise storm is built for beach-bar drama, "
                "clipping a bright orange slice and cherry to the rim completes "
                "the tropical mood.",
        "source": PRACTICE,
    },
],

"Jungle Bird": [
    {
        "name": "Pineapple wedge",
        "ingredient": None,
        "measure": "1 wedge",
        "note": "Perch a fresh pineapple wedge right on the rim rather than "
                "relying on canned rings—its sweet tropical scent sits nicely "
                "above the bittersweet Campari.",
        "source": "Difford's Guide",
    },
],

"Mai Tai": [
    {
        "name": "Squeezed lime shell and mint",
        "ingredient": "Fresh mint",
        "measure": None,
        "note": "Set half a squeezed lime dome-side up on the crushed ice and tuck "
                "a generous mint sprig right beside it—tradition says it mimics a "
                "tiny tropical island under palm fronds.",
        "source": "Trader Vic's original specification; IBA",
    },
],

"Mint Julep": [
    {
        "name": "Big mint sprig",
        "ingredient": None,
        "measure": "1 generous sprig",
        "note": "Give a lush mint bouquet a gentle clap between your palms and "
                "plant it right next to the straw—that leafy aroma greets you "
                "before every cool sip.",
        "source": "Difford's Guide",
    },
],

"Penicillin": [
    {
        "name": "Candied ginger",
        "ingredient": None,
        "measure": "1 piece",
        "note": "Thread a chunk of chewy candied ginger onto a pick across the "
                "rim. It previews the spicy kick underneath smoky Scotch and "
                "makes a sweet bite at the finish.",
        "source": "Sam Ross, Milk & Honey; Difford's Guide",
    },
],

"Planter's Punch": [
    {
        "name": "Grated nutmeg",
        "ingredient": None,
        "measure": "a light grating",
        "note": "Give the finished glass a light grating of fresh nutmeg. That "
                "warm island spice makes fruity rum punch taste wonderfully "
                "classic.",
        "source": "Difford's Guide",
    },
],

"Tequila Sunrise": [
    {
        "name": "Orange slice and cherry",
        "ingredient": "Maraschino cherries",
        "measure": None,
        "note": "Half the fun of a Sunrise is watching that ruby grenadine glow "
                "through orange juice, and a bright orange wheel plus cherry "
                "finishes the postcard look.",
        "source": "IBA official specification",
    },
],

"Zombie": [
    {
        "name": "Mint sprig",
        "ingredient": "Fresh mint",
        "measure": "1 sprig",
        "note": "Tuck a crisp mint sprig into the crushed ice right at the top. "
                "With three rums and high-proof 151 in the glass, cool green "
                "aroma offers a welcome breath of fresh air.",
        "source": "Difford's Guide",
    },
],

# ============================ Coffee & Dessert =============================

"Grasshopper": [
    {
        "name": "Grated chocolate or a mint leaf",
        "ingredient": "Fresh mint",
        "measure": None,
        "note": "Pick either dark chocolate shavings or a crisp green mint leaf—"
                "this creamy coupe is pure velvet, so the garnish brings all its "
                "fresh aroma and texture.",
        "source": PRACTICE,
    },
],

"Irish Coffee": [
    {
        "name": "Grated nutmeg",
        "ingredient": None,
        "measure": "a light grating",
        "note": "Try dusting a whisper of fresh nutmeg strictly across the cream "
                "cap (never stirred in). San Francisco's Buena Vista skips it, "
                "so pick whichever camp feels cosiest.",
        "source": "Difford's Guide (listed as an optional garnish)",
    },
],

"Oreo Mudslide": [
    {
        "name": "Crushed Oreo rim",
        "ingredient": None,
        "measure": None,
        "note": "Dip the chilled glass edge in chocolate syrup and press into "
                "crushed Oreo crumbs before pouring—if you're making a boozy "
                "milkshake, go all the way.",
        "source": PRACTICE,
    },
],

"Toasted Almond": [
    {
        "name": "Grated nutmeg",
        "ingredient": None,
        "measure": "a light grating",
        "note": "Amaretto, coffee liqueur, and cream are velvety and gentle all "
                "the way through—a fine grating of fresh nutmeg on top wakes up "
                "those toasted nutty notes.",
        "source": PRACTICE,
    },
],

}
