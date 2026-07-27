# -*- coding: utf-8 -*-
"""Add an "About this drink" section and a "Worth knowing" tip to every recipe.

WHY
---
Two things were wrong and they turn out to be the same thing.

First, recipe pages had no context. You could see what went in a Bee's Knees and
how to build it, but nothing about what it is or why it is called that, which is
most of what makes a cocktail list fun to browse rather than just accurate.

Second, and this is the part nobody noticed: the flavour line at the top of
`instructions` was being rendered as step 1. `instruction_steps()` in app.py
splits on line breaks and does not care whether a line is prose or a step, so
every recipe page has been telling people that the first instruction in a Bee's
Knees is "A Sour with a little more dignity." The same thing happens at the
bottom: 31 of the recipes added on 2026-07-24 and 07-25 end with a trailing note
("Demerara syrup instead of simple is the upgrade here"), which renders as a
final numbered step.

So the fix for the missing context and the fix for the phantom steps are one
change: pull the prose out of `instructions` into fields of its own.

WHAT IT DOES
------------
1. Adds `about` and `tip` columns to `recipes`. Both nullable, so a recipe
   without them renders exactly as it does today.
2. Rewrites `instructions` to contain numbered steps and nothing else.
3. Populates `about` for all 171 recipes and `tip` for the 125 that have a
   technique note worth reading before you start.
4. Normalises the 16 recipes whose instructions were one prose blob with no
   numbered steps at all, so every recipe now renders as an ordered list.

WHAT IT DELIBERATELY DOES NOT DO
--------------------------------
It does not touch `recipe_ingredients`, `ingredients` or `user_stock`. Nothing
here can change what anyone can make. **Makeable and one-away counts must be
identical before and after.** If they move, something is wrong, and that is the
whole verification for this script. The separate name-matching fixes found in
the same audit live in `fix_namematch_requirements.py` precisely so that their
effect on the counts can be read on its own.

USAGE
-----
    python3 migrate_recipe_about.py            # dry run, prints the plan
    python3 migrate_recipe_about.py --commit   # writes

Idempotent. Recipes are matched on name and the column adds are guarded, so
re-running after a successful commit is a no-op.
"""

import os
import re
import sqlite3
import sys

from about_text import ABOUT

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bomu.db")

MARKER = "[BOMU_REWRITTEN_v1]"


# ---------------------------------------------------------------------------
# Recipes whose instructions were a single prose paragraph with no numbered
# steps, so there was nothing for the template's ordered list to render and
# nothing to cleanly separate the blurb from the method. Rewritten here into
# steps. The wording is preserved as closely as the restructure allows; the
# blurb sentences that were mixed into these paragraphs have moved to `about`.
# ---------------------------------------------------------------------------
INSTRUCTION_REWRITES = {
    "Aperol Spritz": [
        "Fill a large wine glass with ice.",
        "Pour in 150 ml of prosecco first.",
        "Add 100 ml of Aperol.",
        "Top with a splash of soda water.",
        "Stir once, gently, and leave it alone. Garnish with an orange slice.",
    ],
    "Aviation": [
        "Add the gin, lemon juice and maraschino liqueur to a shaker with plenty of ice.",
        "Shake hard for about 15 seconds until the tin is properly cold.",
        "Double-strain into a chilled cocktail glass. This one deserves a clear pour, not a cloudy one.",
        "Garnish with a cherry or a lemon twist.",
    ],
    "Bee's Knees": [
        "Add 2 oz gin, 3/4 oz honey syrup and 3/4 oz fresh lemon juice to a shaker with ice.",
        "Shake hard until the tin is properly cold, about 12 seconds.",
        "Strain into a chilled coupe.",
        "Twist a lemon peel over the surface to express the oils, then rest it on the rim.",
    ],
    "Champagne Cocktail": [
        "Place the sugar cube in a champagne flute and saturate it with 2 dashes of bitters.",
        "Add 1 dash of cognac directly onto the cube.",
        "Slowly pour chilled champagne over the back of a spoon to preserve the bubbles.",
        "Twist a lemon peel over the glass to express the oils, then drop it in.",
    ],
    "Chatham Artillery Punch": [
        "Add 1/2 oz cognac, 1/2 oz rye or bourbon and 1/2 oz aged rum to a shaker.",
        "Add 3/4 oz lemon juice and 1/2 oz simple syrup.",
        "Shake with ice and strain into an ice-filled punch cup or wine glass.",
        "Top with about 2 oz chilled champagne or sparkling wine.",
        "Grate nutmeg over the top and garnish with a lemon wheel.",
    ],
    "Cuba Libre": [
        "Fill a highball glass with ice.",
        "Pour in 2 oz of light rum.",
        "Squeeze in the juice of half a lime directly over the rum, then drop the shell in.",
        "Top with Coca-Cola to taste.",
        "Give it one gentle stir, enough to marry it without killing the carbonation.",
    ],
    "Dark and Stormy": [
        "Fill a highball glass to the brim with ice.",
        "Pour in the ginger beer first, leaving room at the top.",
        "Float the dark rum slowly over the top so it clouds downward through the glass.",
        "Serve with a lime wedge and do not stir it. The layering is the drink.",
    ],
    "Espresso Martini": [
        "Pull a fresh shot of espresso. It needs to be hot and fresh or the foam will not form.",
        "Add the vodka, Kahlua, a dash of simple syrup and the espresso to a shaker with plenty of ice.",
        "Shake hard, longer than feels necessary, at least 15 seconds.",
        "Strain into a chilled cocktail glass and let the crema settle on top.",
        "Garnish with three coffee beans.",
    ],
    "Fish House Punch": [
        "Add 1 1/2 oz Jamaican or aged rum, 3/4 oz cognac and 1/4 oz peach brandy to a shaker.",
        "Add 3/4 oz lemon juice and 1/2 oz simple syrup.",
        "Shake with ice and strain into an ice-filled punch cup.",
        "Grate nutmeg over the top.",
        "Garnish with a lemon wheel.",
    ],
    "Irish Coffee": [
        "Warm the glass with hot water, then tip it out. A cold glass ruins it.",
        "Pour in 1 1/2 oz Irish whiskey and add 1 tsp sugar.",
        "Fill with about 8 oz hot brewed coffee and stir until the sugar dissolves.",
        "Float 1 tbsp lightly whipped cream over the back of a spoon so it sits on top.",
        "Drink through the cream, not around it.",
    ],
    "Kir Royale": [
        "Pour the creme de cassis into a champagne flute first.",
        "Slowly pour the champagne over the back of a spoon to layer it gently on top.",
        "Do not stir. Let the two find each other.",
    ],
    # Steps name the ingredients exactly as the recipe_ingredients rows do
    # (triple sec, sweet and sour), not by generic category. A step calling it
    # "orange liqueur" while the list above says "Triple sec" reads as two
    # different drinks on one page.
    "Mai Tai": [
        "Add 1 oz light rum, 1/2 oz orgeat syrup, 1/2 oz triple sec and 1 1/2 oz sweet and sour to a shaker with ice.",
        "Shake hard until the tin is properly cold.",
        "Strain into a Collins glass over fresh ice.",
        "Garnish with a cherry and hand it to someone who deserves a vacation.",
    ],
    "Mimosa": [
        "Pour 2 oz of chilled orange juice into a chilled champagne flute.",
        "Top slowly with chilled champagne, pouring down the side of the glass.",
        "That is it. Some drinks do not need a paragraph.",
    ],
    "Mojito": [
        "Press 2 to 4 mint leaves with 2 tsp sugar and the juice of 1 lime in a highball glass until fragrant.",
        "Fill the glass with cracked ice.",
        "Pour in 2 to 3 oz of light rum and stir to lift the mint off the bottom.",
        "Top with soda water to taste.",
        "Give it one gentle stir and garnish with a mint sprig.",
    ],
    "Oreo Mudslide": [
        "Blend 1 oz vodka, 1 oz Kahlua and 1 oz Baileys with both scoops of vanilla ice cream until completely smooth. No chunks.",
        "Pour into a Collins glass.",
        "Crush an Oreo and scatter it over the top.",
    ],
    "Pina Colada": [
        "Add the light rum, coconut cream and pineapple juice to a blender.",
        "Add a generous scoop of crushed ice.",
        "Blend until completely smooth, not chunky.",
        "Pour into a Collins or hurricane glass and garnish with a pineapple wedge.",
    ],
    "Screwdriver": [
        "Fill a highball glass with ice.",
        "Pour 2 oz vodka directly over the ice.",
        "Top with orange juice to taste.",
        "Give it one gentle stir to bring it together.",
    ],
    "Singapore Sling": [
        "Add 1 oz gin, 1/2 oz cherry brandy, 1/2 oz grenadine and 2 oz sweet and sour to a shaker with ice.",
        "Shake hard until the tin is cold and frosty.",
        "Strain into a hurricane glass over fresh ice.",
        "Top with carbonated water to taste and stir once to integrate.",
        "Garnish with a cherry.",
    ],
}


def guard_side_files():
    """A stray SQLite journal rolled the live database back on 2026-07-23.
    Refuse to touch the file while one is present, because committing on top of
    an uncommitted journal is how that data was lost."""
    for suffix in ("-journal", "-wal", "-shm"):
        side = DB_PATH + suffix
        if os.path.exists(side):
            print(f"REFUSING TO RUN: {os.path.basename(side)} is present.")
            print("Close anything using the database and re-run. See CLAUDE.md, Gotchas.")
            sys.exit(1)


def strip_marker(text):
    return (text or "").replace(MARKER, "").strip()


def steps_only(text):
    """Return just the numbered steps from an instructions blob, renumbered
    from 1. Prose before the first numbered line and after the last is dropped,
    because that prose is exactly what is moving into `about` and `tip`."""
    lines = [l.strip() for l in strip_marker(text).splitlines() if l.strip()]
    numbered = [l for l in lines if re.match(r"^\d+\.", l)]
    out = []
    for i, line in enumerate(numbered, start=1):
        out.append(f"{i}. " + re.sub(r"^\d+\.\s*", "", line))
    return out


def build_instructions(name, current):
    """The instructions this recipe should end up with: numbered steps only."""
    if name in INSTRUCTION_REWRITES:
        steps = [f"{i}. {s}" for i, s in enumerate(INSTRUCTION_REWRITES[name], start=1)]
    else:
        steps = steps_only(current)
    if not steps:
        return None
    return "\n".join(steps) + "\n" + MARKER


def ensure_columns(conn, commit):
    """Add the two columns if they are not already there. Guarded so a re-run
    after a successful commit does not blow up on a duplicate column."""
    have = {r[1] for r in conn.execute("PRAGMA table_info(recipes)")}
    added = []
    for col in ("about", "tip"):
        if col not in have:
            added.append(col)
            if commit:
                conn.execute(f"ALTER TABLE recipes ADD COLUMN {col} TEXT")
    return added


def main():
    commit = "--commit" in sys.argv
    guard_side_files()

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    try:
        added = ensure_columns(conn, commit)
        if added:
            print(f"Columns to add: {', '.join(added)}")
        else:
            print("Columns already present.")

        rows = conn.execute("SELECT id, name, instructions FROM recipes ORDER BY name").fetchall()
        print(f"{len(rows)} recipes in the database.\n")

        missing_copy = []
        no_steps = []
        planned = []

        for r in rows:
            entry = ABOUT.get(r["name"])
            if entry is None:
                missing_copy.append(r["name"])
                continue

            new_instr = build_instructions(r["name"], r["instructions"])
            if new_instr is None:
                no_steps.append(r["name"])
                continue

            planned.append((r["id"], r["name"], entry["about"], entry.get("tip"),
                            new_instr, r["instructions"]))

        if missing_copy:
            print("NO ABOUT COPY WRITTEN FOR THESE, they would be left blank:")
            for n in missing_copy:
                print(f"   {n}")
            print("Refusing to run a partial pass. Add copy to about_text.py first.")
            conn.close()
            sys.exit(1)

        if no_steps:
            print("COULD NOT BUILD NUMBERED STEPS FOR THESE:")
            for n in no_steps:
                print(f"   {n}")
            print("Add them to INSTRUCTION_REWRITES. Refusing to run a partial pass.")
            conn.close()
            sys.exit(1)

        changed_instructions = [p for p in planned if strip_marker(p[4]) != strip_marker(p[5])]
        with_tips = [p for p in planned if p[3]]

        print(f"Plan: write `about` on {len(planned)} recipes, `tip` on {len(with_tips)}.")
        print(f"      rewrite `instructions` on {len(changed_instructions)} "
              f"(the rest already contained only numbered steps).\n")

        print("Sample of what changes, first 3 rewritten:")
        for _id, name, about, tip, new_i, old_i in changed_instructions[:3]:
            print(f"\n  --- {name}")
            print(f"      about: {about[:90]}...")
            print(f"      tip:   {(tip or '(none)')[:90]}")
            print(f"      steps before: {len([l for l in strip_marker(old_i).splitlines() if l.strip()])} lines "
                  f"-> after: {len([l for l in strip_marker(new_i).splitlines() if l.strip()])} lines")

        if not commit:
            print("\nDRY RUN. Nothing written. Re-run with --commit to apply.")
            conn.close()
            return

        for _id, name, about, tip, new_i, _old in planned:
            conn.execute(
                "UPDATE recipes SET about = ?, tip = ?, instructions = ? WHERE id = ?",
                (about, tip, new_i, _id),
            )

        conn.commit()

    except Exception as exc:
        conn.rollback()
        print(f"FAILED, rolled back: {exc}")
        conn.close()
        sys.exit(1)

    n_about = conn.execute("SELECT COUNT(*) FROM recipes WHERE about IS NOT NULL AND about != ''").fetchone()[0]
    n_tip = conn.execute("SELECT COUNT(*) FROM recipes WHERE tip IS NOT NULL AND tip != ''").fetchone()[0]
    print(f"\nDone. {n_about} recipes have an about, {n_tip} have a tip.")
    print("Now verify the counts did NOT move:")
    print('  python3 -c "import matching; r=matching.get_recommendations(1); '
          "print(r['total_makeable'], r['total_one_away'])\"")
    conn.close()


if __name__ == "__main__":
    main()
