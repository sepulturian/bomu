#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Update `recipes.about`, `recipes.tip`, and standard optional garnishes (2026-11-20).

Usage:
    python migrate_copy_2026_11.py                 # dry run on bomu.db
    python migrate_copy_2026_11.py --commit        # write bomu.db
    python migrate_copy_2026_11.py --db copy.db    # dry run on copy
    python migrate_copy_2026_11.py --postgres      # dry run on Neon
    python migrate_copy_2026_11.py --postgres --commit

Updates:
1. `recipes.about` and `recipes.tip` from `about_text.py`
2. Standard classic garnishes moved out of `enhance_text.py` into `recipe_ingredients`
   with `requirement_type = 'optional'` and into the final step of `recipes.instructions`.

Expected effect on matcher counts: ZERO (`matching.py` ignores `optional` rows and
prose columns). Asserted before commit.
"""

import argparse
import os
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from about_text import ABOUT

DB_PATH = str(ROOT / "bomu.db")

# Standard classic garnishes moved into the recipe itself as optional rows +
# final step wording. Each entry is:
#   recipe_name: ([(raw_name, raw_measure, ingredient_name), ...], old_line, new_line)
GARNISH_MOVES = {
    "Negroni": (
        [("Orange twist", "1", "Oranges")],
        "4. Garnish and serve.",
        "4. Express an orange peel or slice over the glass and drop it in if you have one.",
    ),
    "Old Fashioned": (
        [("Orange twist", "1", "Oranges"), ("Maraschino cherry", "1", "Maraschino cherries")],
        "3. Stir briefly to integrate. Garnish with an orange twist and a cocktail cherry.",
        "3. Stir briefly to integrate. Garnish with an orange twist and a cherry if you like.",
    ),
    "Brandy Sour": (
        [("Lemon twist", "1", "Lemons")],
        "4. Dash Angostura over the foam once it settles.",
        "4. Dash Angostura over the foam once it settles, and finish with a lemon twist if you have one.",
    ),
    "Gold Rush": (
        [("Lemon twist", "1", "Lemons")],
        "3. Strain into an ice-filled old fashioned glass.",
        "3. Strain into an ice-filled old fashioned glass and garnish with a lemon twist if you have one.",
    ),
    "Bramble": (
        [("Lemon slice", "1", "Lemons"), ("Blackberry", "1", None)],
        "3. Slowly drizzle the Creme de Mure over the top in a circular motion. It sinks and bleeds through the ice in a way that earns its name.",
        "3. Slowly drizzle the Creme de Mure over the top so it bleeds through the ice, and top with a lemon slice and a blackberry if you have them.",
    ),
    "Clover Club": (
        [("Raspberries", "2 or 3", None)],
        "3. Double-strain into a chilled cocktail glass. The foam will settle into a clean, silky top.",
        "3. Double-strain into a chilled cocktail glass and garnish with a couple of fresh raspberries on a pick if you have them.",
    ),
    "Corpse Reviver #2": (
        [("Orange twist", "1", "Oranges")],
        "3. Shake hard until the tin is cold and frost is forming. Strain into the absinthe-kissed coupe.",
        "3. Shake hard until the tin is cold and frost is forming. Strain into the absinthe-kissed coupe and express an orange twist over the top if you have one.",
    ),
    "Daiquiri": (
        [("Lime wheel", "1", "Limes")],
        "3. Strain into a chilled cocktail glass.",
        "3. Strain into a chilled cocktail glass and rest a thin lime wheel on the rim if you have one.",
    ),
    "Hemingway Daiquiri": (
        [("Lime wheel", "1", "Limes")],
        "3. Double-strain into a chilled coupe. The extra strainer keeps any pulp or ice shards where they belong.",
        "3. Double-strain into a chilled coupe to catch any pulp or ice shards, and garnish with a lime wheel if you have one.",
    ),
    "Kamikaze": (
        [("Lime wheel", "1", "Limes")],
        "3. Strain into a chilled cocktail glass.",
        "3. Strain into a chilled cocktail glass and garnish with a lime wheel or wedge if you like.",
    ),
    "Matador": (
        [("Lime wedge", "1", "Limes")],
        "4. Strain into the chilled coupe and serve immediately.",
        "4. Strain into the chilled coupe and rest a lime wedge on the rim if you have one.",
    ),
    "Pegu Club": (
        [("Lime twist", "1", "Limes")],
        "4. Strain into a chilled cocktail glass.",
        "4. Strain into a chilled cocktail glass and express a strip of lime peel over the top if you have one.",
    ),
    "Pink Lady": (
        [("Maraschino cherry", "1", "Maraschino cherries")],
        "3. Double-strain into a chilled cocktail glass and let the foam settle into that pale pink crown.",
        "3. Double-strain into a chilled cocktail glass, let the foam settle, and drop in a cherry if you like.",
    ),
    "Tequila Sour": (
        [("Lime wheel", "1", "Limes")],
        "4. Let the foam settle, then dash bitters across the top.",
        "4. Let the foam settle, dash bitters across the top, and perch a lime wheel on the rim if you have one.",
    ),
    "The Last Word": (
        [("Maraschino cherry", "1", "Maraschino cherries")],
        "3. Double-strain into a chilled cocktail glass.",
        "3. Double-strain into a chilled cocktail glass and drop a brandied cherry in the bottom if you like.",
    ),
    "White Lady": (
        [("Lemon twist", "1", "Lemons")],
        "4. Strain into a chilled cocktail glass and serve up.",
        "4. Strain into a chilled cocktail glass and squeeze a lemon twist over the top if you have one.",
    ),
    "Kir Royale": (
        [("Lemon twist", "1", "Lemons")],
        "3. Do not stir. Let the two find each other.",
        "3. Do not stir. Express a lemon twist over the flute if you like and let the bubbles mix it.",
    ),
    "Mimosa": (
        [("Orange twist", "1", "Oranges")],
        "3. That is it. Some drinks do not need a paragraph.",
        "3. Garnish with a strip of orange twist if you feel like dressing it up.",
    ),
    "Morning Glory Fizz": (
        [("Lemon twist", "1", "Lemons")],
        "5. Serve immediately, before the head collapses.",
        "5. Express a lemon twist over the foam if you have one and serve immediately.",
    ),
    "Greyhound": (
        [("Grapefruit twist", "1", None)],
        "3. Give it a gentle stir to bring everything together. Tart, clean, and honest.",
        "3. Give it a gentle stir and garnish with a grapefruit peel or wedge if you have one.",
    ),
    "Moscow Mule": (
        [("Lime wedge", "1", "Limes"), ("Mint sprig", "1 sprig", "Fresh mint")],
        "3. Top with the 8 oz of ginger beer and give it one slow stir to bring everything together without killing the carbonation.",
        "3. Top with the 8 oz of ginger beer, give it one slow stir, and garnish with a lime wedge and a sprig of mint if you have them.",
    ),
    "Screwdriver": (
        [("Orange slice", "1", "Oranges")],
        "4. Give it one gentle stir to bring it together.",
        "4. Give it one gentle stir and perch an orange slice on the rim if you have one.",
    ),
    "Sea breeze": (
        [("Lime wedge", "1", "Limes")],
        "3. Float 1 oz grapefruit juice over the top. It'll drift down on its own, giving you a nice gradient before you hand it over.",
        "3. Float 1 oz grapefruit juice over the top and finish with a lime wedge on the rim if you have one.",
    ),
    "Blue Hurricane": (
        [("Orange slice", "1", "Oranges"), ("Maraschino cherry", "1", "Maraschino cherries")],
        "3. Blend until smooth and slushy. Pour into a highball glass and drink through the widest straw you own.",
        "3. Blend until smooth and slushy, pour into a highball glass, and garnish with an orange slice and cherry if you like.",
    ),
    "Jungle Bird": (
        [("Pineapple wedge", "1", None)],
        "3. Strain over fresh ice into an old fashioned glass.",
        "3. Strain over fresh ice into an old fashioned glass and garnish with a pineapple wedge if you have one.",
    ),
    "Mai Tai": (
        [("Mint sprig", "1 sprig", "Fresh mint")],
        "4. Garnish with a cherry and hand it to someone who deserves a vacation.",
        "4. Garnish with a mint sprig or cherry if you have them and hand it to someone who deserves a vacation.",
    ),
    "Mint Julep": (
        [("Mint sprig", "1 generous sprig", "Fresh mint")],
        "3. Stir until the outside of the glass frosts over. Top with more crushed ice to crown it.",
        "3. Stir until the outside of the glass frosts over, mound more crushed ice on top, and tuck a big mint sprig right next to the straw.",
    ),
    "Penicillin": (
        [("Candied ginger", "1 piece", None)],
        "3. Float 1/4 oz Islay single malt over the back of a spoon. That smoky layer is the whole point, so don't skip it.",
        "3. Float 1/4 oz Islay single malt over the back of a spoon, and rest a piece of candied ginger on the rim if you have it.",
    ),
    "Tequila Sunrise": (
        [("Orange slice", "1", "Oranges"), ("Maraschino cherry", "1", "Maraschino cherries")],
        "3. Leave it alone. The whole point is the sunrise, so resist the urge to stir.",
        "3. Leave it unstirred so the sunrise gradient holds, and garnish with an orange slice and cherry if you like.",
    ),
    "Zombie": (
        [("Mint sprig", "1 sprig", "Fresh mint")],
        "3. Pour the 151 slowly over the back of a spoon to float it on top. It stays there for a reason. Respect it.",
        "3. Float the 151 slowly over the back of a spoon, and tuck a fresh mint sprig into the ice if you have one.",
    ),
}


def guard_side_files(db_path):
    """Refuse to run if SQLite left a journal, WAL, or shared-memory file behind."""
    stragglers = [
        p for p in (db_path + "-journal", db_path + "-wal", db_path + "-shm")
        if os.path.exists(p)
    ]
    if stragglers:
        print("REFUSING TO RUN. SQLite side files present:")
        for p in stragglers:
            print("   ", p)
        sys.exit(1)


def user_counts(conn):
    """Snapshot per-user (id, username, makeable, one_away) via matching.py."""
    import matching

    users = conn.execute("SELECT id, username FROM users ORDER BY id").fetchall()
    out = []
    for u in users:
        r = matching.get_recommendations(u["id"], max_makeable=200, max_one_away=200)
        out.append((u["id"], u["username"], r["total_makeable"], r["total_one_away"]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--commit", action="store_true", help="actually write")
    ap.add_argument("--db", default=DB_PATH, help="SQLite database path")
    ap.add_argument(
        "--postgres",
        action="store_true",
        help="Write to DATABASE_URL (Neon Postgres) configured in .env.",
    )
    args = ap.parse_args()

    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
    import database

    if args.postgres:
        if not database._is_postgres():
            print("REFUSING TO RUN. --postgres given but DATABASE_URL does not "
                  "resolve to Postgres (unset, or FORCE_SQLITE is on).")
            sys.exit(1)
        conn = database.get_db()
        target_label = "Postgres (DATABASE_URL)"
    else:
        os.environ["FORCE_SQLITE"] = "1"
        guard_side_files(args.db)
        database.DB_PATH = os.path.abspath(args.db)
        conn = sqlite3.connect(args.db)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        target_label = args.db

    print(f"Target database: {target_label}")
    print(f"Backend check:   {'postgres' if database._is_postgres() else 'sqlite'}\n")

    rows = conn.execute(
        "SELECT id, name, about, tip, instructions FROM recipes ORDER BY name"
    ).fetchall()
    db_names = {r["name"] for r in rows}
    by_name = {r["name"]: r for r in rows}
    valid_ings = {
        r["name"]
        for r in conn.execute("SELECT name FROM ingredients").fetchall()
    }

    problems = []
    missing_copy = sorted(db_names - set(ABOUT.keys()))
    if missing_copy:
        problems.append(f"Missing about_text.ABOUT entries for: {missing_copy}")
    extra_copy = sorted(set(ABOUT.keys()) - db_names)
    if extra_copy:
        problems.append(f"about_text.ABOUT keys not in DB: {extra_copy}")
    missing_garnish = sorted(set(GARNISH_MOVES.keys()) - db_names)
    if missing_garnish:
        problems.append(f"GARNISH_MOVES keys not in DB: {missing_garnish}")

    updates = []
    for r in rows:
        entry = ABOUT.get(r["name"])
        if not entry:
            continue
        new_about = (entry.get("about") or "").strip() or None
        new_tip = (entry.get("tip") or "").strip() or None
        cur_about = (r["about"] or "").strip() or None
        cur_tip = (r["tip"] or "").strip() or None
        if cur_about != new_about or cur_tip != new_tip:
            updates.append((r["id"], r["name"], new_about, new_tip))

    garnish_inserts = []
    step_updates = []
    for rname, (opt_rows, old_line, new_line) in sorted(GARNISH_MOVES.items()):
        r = by_name.get(rname)
        if not r:
            continue
        rid = r["id"]
        existing_ings = conn.execute(
            "SELECT raw_name, requirement_type, sort_order FROM recipe_ingredients "
            "WHERE recipe_id = ? ORDER BY sort_order",
            (rid,),
        ).fetchall()
        existing_raw = {i["raw_name"].strip().lower() for i in existing_ings}
        next_sort = (max((i["sort_order"] for i in existing_ings), default=-1) + 1)

        for raw_name, raw_measure, ing_name in opt_rows:
            if ing_name and ing_name not in valid_ings:
                problems.append(f"{rname}: garnish ingredient {ing_name!r} not in ingredients table")
                continue
            if raw_name.strip().lower() not in existing_raw:
                garnish_inserts.append(
                    (rid, rname, raw_name, raw_measure, ing_name, next_sort)
                )
                next_sort += 1

        instr = r["instructions"] or ""
        if new_line in instr:
            pass
        elif old_line in instr:
            step_updates.append((rid, rname, instr.replace(old_line, new_line, 1)))
        else:
            problems.append(f"{rname}: expected step line not found: {old_line!r}")

    if problems:
        print("PROBLEMS FOUND. Nothing will be written:")
        for p in problems:
            print("  -", p)
        conn.rollback()
        conn.close()
        sys.exit(1)

    with_tip = sum(1 for r in rows if (ABOUT[r["name"]].get("tip") or "").strip())
    print(f"Catalog:          {len(rows)} recipes ({len(rows)} abouts, {with_tip} tips)")
    print(f"About/tip edits:  {len(updates)} recipe(s)")
    print(f"Optional rows:    {len(garnish_inserts)} new optional garnish row(s)")
    print(f"Instruction steps:{len(step_updates)} final-step garnish update(s)")
    for _rid, rname, na, _nt in updates[:5]:
        print(f"  ~ {rname:<24} about={(na or '')[:60]}...")
    if len(updates) > 5:
        print(f"  ... and {len(updates) - 5} more about/tip updates.")
    for _rid, rname, raw_name, raw_measure, ing_name, _so in garnish_inserts[:5]:
        print(f"  + {rname:<24} optional: {raw_name} ({raw_measure}) -> {ing_name}")
    if len(garnish_inserts) > 5:
        print(f"  ... and {len(garnish_inserts) - 5} more optional garnish rows.")

    before_counts = user_counts(conn)

    if not args.commit:
        conn.rollback()
        conn.close()
        print("\nDRY RUN. Nothing written. Re-run with --commit.")
        return

    try:
        for rid, _rname, na, nt in updates:
            conn.execute(
                "UPDATE recipes SET about = ?, tip = ? WHERE id = ?",
                (na, nt, rid),
            )
        for rid, _rname, raw_name, raw_measure, ing_name, sort_order in garnish_inserts:
            conn.execute(
                "INSERT INTO recipe_ingredients "
                "(recipe_id, raw_name, raw_measure, requirement_type, bottle_type, "
                "ingredient_name, notes, sort_order) "
                "VALUES (?, ?, ?, 'optional', NULL, ?, NULL, ?)",
                (rid, raw_name, raw_measure, ing_name, sort_order),
            )
        for rid, _rname, new_instr in step_updates:
            conn.execute(
                "UPDATE recipes SET instructions = ? WHERE id = ?",
                (new_instr, rid),
            )
        after_counts = user_counts(conn)
        if before_counts != after_counts:
            raise RuntimeError(
                f"Matcher counts moved unexpectedly: {before_counts} -> {after_counts}"
            )
        conn.commit()
    except Exception as exc:
        conn.rollback()
        conn.close()
        print(f"\nFAILED, rolled back: {exc}")
        sys.exit(1)

    conn.close()
    print(
        f"\nCOMMITTED {len(updates)} about/tip updates, "
        f"{len(garnish_inserts)} optional garnish rows, "
        f"{len(step_updates)} step updates. Matcher counts verified unchanged:"
    )
    for b in before_counts:
        print(f"  {b[0]:2d} {b[1]:<12} {b[2]:2d}/{b[3]:2d}")


if __name__ == "__main__":
    main()
