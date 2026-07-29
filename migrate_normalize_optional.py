#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Normalise the `optional` rows in recipe_ingredients.

    python3 migrate_normalize_optional.py            # dry run
    python3 migrate_normalize_optional.py --commit   # writes

THE PROBLEM
-----------
Optional rows are garnishes and they were never audited, so the same garnish
appears under several spellings. On the stale local copy alone:

    Orange Peel / Orange peel / Orange twist / Orange Twist /
    Orange slice / Orange slices / Orange Slice / Orange     -- eight rows
    Maraschino cherry / Maraschino Cherry / Cherry           -- three rows
    Lemon peel / Lemon twist / Lemon Twist / Lemon / lemon   -- five rows

plus rows for `Ice` and `Water`, which are not garnishes and are not optional
in any meaningful sense -- every shaken drink uses ice, and listing it as an
optional ingredient is the app saying something it does not mean.

EXPECTED EFFECT ON THE MATCHER: NONE.

`optional` rows are skipped outright by both match_recipe() and
missing_ingredient_ids(), so nothing here can change makeability. Same
verification as migrate_enhancements.py: the counts must not move, and if they
do, roll it back and find out why.

WHY IT WON'T SILENTLY REWRITE THINGS IT DOESN'T RECOGNISE
---------------------------------------------------------
The live database has 171 recipes; the local copy is a stale 100-recipe
pre-multi-user snapshot, so this script was written against an incomplete view
of the data on purpose-built distrust. Anything not explicitly listed in
CANONICAL or DROP is REPORTED AND LEFT ALONE. Read the "unmapped" section of
the dry run, add what belongs, run it again. A migration that guesses at rows
it has never seen is exactly how the Grape Soda tile ended up showing purple
grape soda under a grapefruit label.
"""

import argparse
import os
import sqlite3
import sys
from collections import defaultdict

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bomu.db")

# variant (lowercased, stripped) -> canonical display name.
#
# Chosen so the name says what you do with it. "Orange peel" and "Orange twist"
# are collapsed to "Orange twist" because a twist is the action; "Orange slice"
# stays separate because a slice really is a different garnish that goes in the
# drink rather than over it. Bare "Orange" is ambiguous and resolves to the
# twist, which is the far commoner intent in this catalog.
CANONICAL = {
    # --- orange ---
    "orange": "Orange twist",
    "orange peel": "Orange twist",
    "orange twist": "Orange twist",
    "orange zest": "Orange twist",
    "orange zest twist": "Orange twist",
    "orange slice": "Orange slice",
    "orange slices": "Orange slice",
    "orange wheel": "Orange slice",
    "orange wedge": "Orange wedge",

    # --- lemon ---
    "lemon": "Lemon twist",
    "lemon peel": "Lemon twist",
    "lemon twist": "Lemon twist",
    "lemon zest": "Lemon twist",
    "lemon slice": "Lemon slice",
    "lemon wheel": "Lemon slice",
    "lemon wedge": "Lemon wedge",

    # --- lime ---
    "lime": "Lime wedge",
    "lime wedge": "Lime wedge",
    "lime wheel": "Lime wheel",
    "lime slice": "Lime wheel",
    "lime peel": "Lime twist",
    "lime twist": "Lime twist",

    # --- cherry ---
    "cherry": "Maraschino cherry",
    "maraschino cherry": "Maraschino cherry",
    "cocktail cherry": "Maraschino cherry",
    "brandied cherry": "Brandied cherry",

    # --- mint ---
    "mint": "Mint sprig",
    "mint sprig": "Mint sprig",
    "fresh mint": "Mint sprig",
    "fresh mint sprig": "Mint sprig",
    "mint leaves": "Mint sprig",

    # --- pineapple ---
    "pineapple": "Pineapple wedge",
    "pineapple wedge": "Pineapple wedge",
    "pineapple slice": "Pineapple wedge",
    "pineapple chunk": "Pineapple wedge",

    # --- spice and seasoning ---
    "nutmeg": "Grated nutmeg",
    "freshly grated nutmeg": "Grated nutmeg",
    "grated nutmeg": "Grated nutmeg",
    "ground nutmeg": "Grated nutmeg",
    "cinnamon": "Cinnamon",
    "cinnamon stick": "Cinnamon stick",
    "cloves": "Cloves",
    "salt": "Salt",
    "celery salt": "Celery salt",
    "pepper": "Black pepper",
    "black pepper": "Black pepper",

    # --- other produce ---
    "cucumber slice": "Cucumber slice",
    "strawberry": "Strawberry",
    "berries": "Berries",
    "olive": "Olive",
    "olives": "Olive",
    "cocktail onion": "Cocktail onion",
    "cocktail onions": "Cocktail onion",

    # --- dairy / misc that are genuinely optional additions ---
    "light cream": "Light cream",
    "whipped cream": "Whipped cream",
    "oreo cookie": "Oreo cookie",
}

# Rows deleted outright. These are not garnishes and not optional additions --
# they are either implied by the method or already a required ingredient, and
# showing them under an "optional" pill tells the user something false.
DROP = {
    "ice",           # every shaken or built drink uses it; the method says so
    "water",         # only ever appears as dilution, which is not an ingredient
    "ice cubes",
    "crushed ice",
    "garnish",       # a placeholder that names nothing
    "",
}


def guard_side_files(db_path):
    """Refuse to run if SQLite left a journal, WAL or -shm file behind."""
    stragglers = [
        p for p in (db_path + "-journal", db_path + "-wal", db_path + "-shm")
        if os.path.exists(p)
    ]
    if stragglers:
        print("REFUSING TO RUN. SQLite side files present:")
        for p in stragglers:
            print("   ", p)
        sys.exit(1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--commit", action="store_true")
    ap.add_argument("--db", default=DB_PATH)
    args = ap.parse_args()

    guard_side_files(args.db)

    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        "SELECT ri.id, ri.raw_name, r.name AS recipe "
        "FROM recipe_ingredients ri JOIN recipes r ON r.id = ri.recipe_id "
        "WHERE ri.requirement_type = 'optional' "
        "ORDER BY r.name"
    ).fetchall()

    renames, drops, unmapped = [], [], defaultdict(list)

    for row in rows:
        raw = (row["raw_name"] or "").strip()
        key = raw.lower()
        if key in DROP:
            drops.append(row)
        elif key in CANONICAL:
            target = CANONICAL[key]
            if target != raw:
                renames.append((row, target))
        else:
            unmapped[raw].append(row["recipe"])

    before = {}
    for r in conn.execute(
        "SELECT raw_name, COUNT(*) c FROM recipe_ingredients "
        "WHERE requirement_type = 'optional' GROUP BY raw_name"
    ):
        before[r["raw_name"]] = r["c"]

    print(f"Database: {args.db}")
    print(f"{len(rows)} optional rows, {len(before)} distinct names\n")

    print(f"RENAME  {len(renames)} rows")
    grouped = defaultdict(list)
    for row, target in renames:
        grouped[(row["raw_name"], target)].append(row["recipe"])
    for (src, target), recipes in sorted(grouped.items()):
        print(f"    {src!r} -> {target!r}  ({len(recipes)} rows)")

    print(f"\nDELETE  {len(drops)} rows")
    for row in drops:
        print(f"    {row['raw_name']!r} on {row['recipe']}")

    print(f"\nUNMAPPED  {len(unmapped)} distinct names, LEFT ALONE")
    if unmapped:
        print("    Read these. If any belong in CANONICAL or DROP, add them")
        print("    and re-run. Nothing below is being touched.")
        print()
        print("    Expect optional BITTERS rows to show up here. They are not")
        print("    garnishes and this script has no opinion on them. They are")
        print("    the survivors of the 2026-07-26 audit that kept six bitters")
        print("    rows and removed seven. Leave them where they are: they are")
        print("    part of the drink, which is why they were kept, and")
        print("    migrate_enhancements.py already refuses to suggest anything")
        print("    that duplicates a row on this list.")
        for name, recipes in sorted(unmapped.items()):
            shown = ", ".join(recipes[:3])
            more = f" +{len(recipes) - 3} more" if len(recipes) > 3 else ""
            print(f"    {name!r}  ({len(recipes)}): {shown}{more}")

    if not renames and not drops:
        conn.close()
        print("\nNothing to do. Already normalised.")
        return

    if not args.commit:
        conn.close()
        print("\nDRY RUN. Nothing written. Re-run with --commit.")
        return

    try:
        for row, target in renames:
            conn.execute(
                "UPDATE recipe_ingredients SET raw_name = ? WHERE id = ?",
                (target, row["id"]),
            )
        for row in drops:
            conn.execute("DELETE FROM recipe_ingredients WHERE id = ?", (row["id"],))
        conn.commit()
    except Exception as exc:
        conn.rollback()
        conn.close()
        print(f"\nFAILED, rolled back: {exc}")
        sys.exit(1)

    after = conn.execute(
        "SELECT COUNT(DISTINCT raw_name) FROM recipe_ingredients "
        "WHERE requirement_type = 'optional'"
    ).fetchone()[0]
    total = conn.execute(
        "SELECT COUNT(*) FROM recipe_ingredients WHERE requirement_type = 'optional'"
    ).fetchone()[0]
    conn.close()

    print(f"\nCOMMITTED. {total} optional rows, {len(before)} distinct names "
          f"-> {after} distinct names.")
    print("Now confirm the matcher did NOT move:")
    print('  python3 -c "import matching; r=matching.get_recommendations(1); '
          "print(r['total_makeable'], r['total_one_away'])\"")


if __name__ == "__main__":
    main()
