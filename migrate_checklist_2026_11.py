#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mixers checklist overhaul & Moscow Mule spec fix (2026-11-20, backlog #8).

Usage:
    python migrate_checklist_2026_11.py                 # dry run on bomu.db
    python migrate_checklist_2026_11.py --commit        # write bomu.db
    python migrate_checklist_2026_11.py --db copy.db    # dry run on copy
    python migrate_checklist_2026_11.py --postgres      # dry run on Neon
    python migrate_checklist_2026_11.py --postgres --commit

Fixes:
  1. Remove unused `Water` (0 required recipes) from ingredients + user_stock.
     (`Maraschino cherries` stays so the 8 recipe_enhancements tags keep working.)
  2. Merge `Light Cream` -> `Heavy cream` (transfer user_stock ticks cleanly,
     update recipe_ingredients & recipe_enhancements, delete `Light Cream`).
  3. Normalize 12 checklist labels (`Coconut cream` -> `Cream of coconut` plus
     consistent sentence casing for Title Case auto-added items).
  4. Clarify Piña Colada's coconut note to match `Cream of coconut`.
  5. Fix misplaced `ingredients.category` buckets (`Grapefruit soda` -> mixer,
     `Mole bitters` -> bitter, `Coffee`/`Heavy cream`/`Vanilla extract`/
     `Vanilla ice cream`/`Whipped cream` -> pantry, `Cream of coconut`/
     `Passion fruit syrup`/`White wine` -> auto).
  6. Fix Moscow Mule: require `Ginger beer` instead of `Ginger ale` and update
     step 3 instructions to match.
"""

import argparse
import os
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

DB_PATH = str(ROOT / "bomu.db")

RENAMES = [
    ("Coconut cream", "Cream of coconut"),
    ("Agave Syrup", "Agave syrup"),
    ("Ginger Syrup", "Ginger syrup"),
    ("Mole Bitters", "Mole bitters"),
    ("Orgeat Syrup", "Orgeat syrup"),
    ("Passion Fruit Syrup", "Passion fruit syrup"),
    ("Red Wine", "Red wine"),
    ("Sweet And Sour Mix", "Sweet and sour mix"),
    ("Vanilla Extract", "Vanilla extract"),
    ("Vanilla Ice Cream", "Vanilla ice cream"),
    ("Whipped Cream", "Whipped cream"),
    ("White Wine", "White wine"),
]

CATEGORY_FIXES = [
    ("Grapefruit soda", ("grapefruit soda",), "mixer"),
    ("Mole bitters", ("mole bitters",), "bitter"),
    ("Coffee", ("coffee",), "pantry"),
    ("Heavy cream", ("heavy cream",), "pantry"),
    ("Vanilla extract", ("vanilla extract",), "pantry"),
    ("Vanilla ice cream", ("vanilla ice cream",), "pantry"),
    ("Whipped cream", ("whipped cream",), "pantry"),
    ("Cream of coconut", ("cream of coconut", "coconut cream"), "auto"),
    ("Passion fruit syrup", ("passion fruit syrup",), "auto"),
    ("White wine", ("white wine",), "auto"),
]

PINA_COLADA_NOTE = (
    "Sweetened cream of coconut (e.g. Coco López), not unsweetened coconut milk"
)


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

    problems = []
    actions = []

    # 1. Remove Water (0 required recipes)
    water_req = conn.execute(
        "SELECT COUNT(*) AS c FROM recipe_ingredients "
        "WHERE requirement_type = 'ingredient' AND lower(ingredient_name) = 'water'"
    ).fetchone()["c"]
    if water_req > 0:
        problems.append(f"Found {water_req} required recipe_ingredients row(s) referencing 'Water'.")
    else:
        ri_water = conn.execute(
            "SELECT COUNT(*) AS c FROM recipe_ingredients WHERE lower(ingredient_name) = 'water'"
        ).fetchone()["c"]
        if ri_water > 0:
            actions.append((
                f"Clear ingredient_name='Water' on {ri_water} non-required recipe_ingredients row(s)",
                "UPDATE recipe_ingredients SET ingredient_name = NULL WHERE lower(ingredient_name) = 'water'",
                (),
            ))
        re_water = conn.execute(
            "SELECT COUNT(*) AS c FROM recipe_enhancements WHERE lower(ingredient_name) = 'water'"
        ).fetchone()["c"]
        if re_water > 0:
            actions.append((
                f"Clear ingredient_name='Water' on {re_water} recipe_enhancements row(s)",
                "UPDATE recipe_enhancements SET ingredient_name = NULL WHERE lower(ingredient_name) = 'water'",
                (),
            ))

        water_row = conn.execute(
            "SELECT id, name FROM ingredients WHERE lower(name) = 'water'"
        ).fetchone()
        if not water_row:
            print("  [ok]   'Water' already removed from ingredients.")
        else:
            water_ticks = conn.execute(
                "SELECT COUNT(*) AS c FROM user_stock WHERE ingredient_id = ?",
                (water_row["id"],),
            ).fetchone()["c"]
            if water_ticks > 0:
                actions.append((
                    f"Delete {water_ticks} user_stock tick(s) for 'Water' (id={water_row['id']})",
                    "DELETE FROM user_stock WHERE ingredient_id = ?",
                    (water_row["id"],),
                ))
            actions.append((
                f"Delete 'Water' (id={water_row['id']}) from ingredients",
                "DELETE FROM ingredients WHERE id = ?",
                (water_row["id"],),
            ))

    # 2. Merge Light Cream -> Heavy cream
    heavy_row = conn.execute(
        "SELECT id, name FROM ingredients WHERE name = ?", ("Heavy cream",)
    ).fetchone()
    light_row = conn.execute(
        "SELECT id, name FROM ingredients WHERE lower(name) = 'light cream'"
    ).fetchone()
    if not heavy_row:
        problems.append("Target ingredient 'Heavy cream' not found.")
    else:
        ri_light = conn.execute(
            "SELECT COUNT(*) AS c FROM recipe_ingredients WHERE lower(ingredient_name) = 'light cream'"
        ).fetchone()["c"]
        re_light = conn.execute(
            "SELECT COUNT(*) AS c FROM recipe_enhancements WHERE lower(ingredient_name) = 'light cream'"
        ).fetchone()["c"]
        if light_row:
            light_ticks = conn.execute(
                "SELECT COUNT(*) AS c FROM user_stock WHERE ingredient_id = ?",
                (light_row["id"],),
            ).fetchone()["c"]
            if light_ticks > 0:
                actions.append((
                    f"Transfer {light_ticks} user_stock tick(s) from {light_row['name']!r} to 'Heavy cream'",
                    "INSERT INTO user_stock (user_id, ingredient_id) "
                    "SELECT us.user_id, ? FROM user_stock us "
                    "WHERE us.ingredient_id = ? "
                    "AND NOT EXISTS ("
                    "SELECT 1 FROM user_stock e WHERE e.user_id = us.user_id AND e.ingredient_id = ?)",
                    (heavy_row["id"], light_row["id"], heavy_row["id"]),
                ))
                actions.append((
                    f"Delete user_stock rows for {light_row['name']!r} (id={light_row['id']})",
                    "DELETE FROM user_stock WHERE ingredient_id = ?",
                    (light_row["id"],),
                ))
            if ri_light > 0:
                actions.append((
                    f"Repoint {ri_light} recipe_ingredients row(s) from 'Light Cream' -> 'Heavy cream'",
                    "UPDATE recipe_ingredients SET ingredient_name = ? WHERE lower(ingredient_name) = 'light cream'",
                    ("Heavy cream",),
                ))
            if re_light > 0:
                actions.append((
                    f"Repoint {re_light} recipe_enhancements row(s) from 'Light Cream' -> 'Heavy cream'",
                    "UPDATE recipe_enhancements SET ingredient_name = ? WHERE lower(ingredient_name) = 'light cream'",
                    ("Heavy cream",),
                ))
            actions.append((
                f"Delete {light_row['name']!r} (id={light_row['id']}) from ingredients",
                "DELETE FROM ingredients WHERE id = ?",
                (light_row["id"],),
            ))
        else:
            if ri_light > 0:
                actions.append((
                    f"Repoint {ri_light} recipe_ingredients row(s) from 'Light Cream' -> 'Heavy cream'",
                    "UPDATE recipe_ingredients SET ingredient_name = ? WHERE lower(ingredient_name) = 'light cream'",
                    ("Heavy cream",),
                ))
            if re_light > 0:
                actions.append((
                    f"Repoint {re_light} recipe_enhancements row(s) from 'Light Cream' -> 'Heavy cream'",
                    "UPDATE recipe_enhancements SET ingredient_name = ? WHERE lower(ingredient_name) = 'light cream'",
                    ("Heavy cream",),
                ))
            if ri_light == 0 and re_light == 0:
                print("  [ok]   'Light Cream' already merged into 'Heavy cream'.")

    # 3. Rename 12 checklist labels (exact case-sensitive updates)
    renamed_ok = 0
    for old, new in RENAMES:
        old_ing = conn.execute(
            "SELECT id FROM ingredients WHERE name = ?", (old,)
        ).fetchone()
        new_ing = conn.execute(
            "SELECT id FROM ingredients WHERE name = ?", (new,)
        ).fetchone()
        if old_ing and new_ing:
            problems.append(f"Both {old!r} and {new!r} exist in ingredients; refusing to rename.")
            continue
        if not old_ing and not new_ing:
            problems.append(f"Neither {old!r} nor {new!r} found in ingredients.")
            continue

        did_something = False
        if old_ing:
            actions.append((
                f"Rename ingredient id={old_ing['id']}: {old!r} -> {new!r}",
                "UPDATE ingredients SET name = ? WHERE id = ?",
                (new, old_ing["id"]),
            ))
            did_something = True

        ri_old = conn.execute(
            "SELECT COUNT(*) AS c FROM recipe_ingredients WHERE ingredient_name = ?",
            (old,),
        ).fetchone()["c"]
        if ri_old > 0:
            actions.append((
                f"Update {ri_old} recipe_ingredients row(s): {old!r} -> {new!r}",
                "UPDATE recipe_ingredients SET ingredient_name = ? WHERE ingredient_name = ?",
                (new, old),
            ))
            did_something = True

        re_old = conn.execute(
            "SELECT COUNT(*) AS c FROM recipe_enhancements WHERE ingredient_name = ?",
            (old,),
        ).fetchone()["c"]
        if re_old > 0:
            actions.append((
                f"Update {re_old} recipe_enhancements row(s): {old!r} -> {new!r}",
                "UPDATE recipe_enhancements SET ingredient_name = ? WHERE ingredient_name = ?",
                (new, old),
            ))
            did_something = True

        if not did_something:
            renamed_ok += 1

    if renamed_ok == len(RENAMES):
        print(f"  [ok]   All {len(RENAMES)} checklist labels already normalized.")

    # 4. Clarify Piña Colada's coconut note
    pina = conn.execute(
        "SELECT id FROM recipes WHERE name = ?", ("Pina Colada",)
    ).fetchone()
    if not pina:
        problems.append("Recipe 'Pina Colada' not found.")
    else:
        coco_row = conn.execute(
            "SELECT id, ingredient_name, notes FROM recipe_ingredients "
            "WHERE recipe_id = ? AND ingredient_name IN (?, ?)",
            (pina["id"], "Coconut cream", "Cream of coconut"),
        ).fetchone()
        if not coco_row:
            problems.append("Pina Colada coconut row not found.")
        elif coco_row["notes"] == PINA_COLADA_NOTE:
            print("  [ok]   Pina Colada coconut note already updated.")
        else:
            actions.append((
                f"Pina Colada row {coco_row['id']}: clarify coconut note",
                "UPDATE recipe_ingredients SET notes = ? WHERE id = ?",
                (PINA_COLADA_NOTE, coco_row["id"]),
            ))

    # 5. Fix ingredients.category placements
    cat_ok = 0
    for label, lower_names, target_cat in CATEGORY_FIXES:
        placeholders = ", ".join("?" * len(lower_names))
        row = conn.execute(
            f"SELECT id, name, category FROM ingredients WHERE lower(name) IN ({placeholders})",
            lower_names,
        ).fetchone()
        if not row:
            problems.append(f"Ingredient for category fix {label!r} not found.")
        elif row["category"] == target_cat:
            cat_ok += 1
        else:
            actions.append((
                f"Category fix {label!r} (id={row['id']}): {row['category']!r} -> {target_cat!r}",
                "UPDATE ingredients SET category = ? WHERE id = ?",
                (target_cat, row["id"]),
            ))
    if cat_ok == len(CATEGORY_FIXES):
        print(f"  [ok]   All {len(CATEGORY_FIXES)} ingredient categories already placed.")

    # 6. Fix Moscow Mule: Ginger ale -> Ginger beer
    gb_ing = conn.execute(
        "SELECT id FROM ingredients WHERE name = ?", ("Ginger beer",)
    ).fetchone()
    if not gb_ing:
        problems.append("Target ingredient 'Ginger beer' not found.")
    mm = conn.execute(
        "SELECT id, instructions FROM recipes WHERE name = ?", ("Moscow Mule",)
    ).fetchone()
    if not mm:
        problems.append("Recipe 'Moscow Mule' not found.")
    else:
        mm_row = conn.execute(
            "SELECT id, raw_name, ingredient_name FROM recipe_ingredients "
            "WHERE recipe_id = ? AND requirement_type = 'ingredient' "
            "AND lower(ingredient_name) IN ('ginger ale', 'ginger beer')",
            (mm["id"],),
        ).fetchone()
        if not mm_row:
            problems.append("Moscow Mule ginger row not found.")
        elif mm_row["raw_name"] == "Ginger beer" and mm_row["ingredient_name"] == "Ginger beer":
            print("  [ok]   Moscow Mule ingredient row already Ginger beer.")
        elif (mm_row["ingredient_name"] or "").lower() == "ginger ale":
            actions.append((
                f"Moscow Mule row {mm_row['id']}: Ginger ale -> Ginger beer",
                "UPDATE recipe_ingredients SET raw_name = ?, ingredient_name = ? WHERE id = ?",
                ("Ginger beer", "Ginger beer", mm_row["id"]),
            ))
        else:
            problems.append(f"Unexpected Moscow Mule row state: {dict(mm_row)}")

        old_mm = "8 oz of ginger ale"
        new_mm = "8 oz of ginger beer"
        mm_instr = mm["instructions"] or ""
        if new_mm in mm_instr:
            print("  [ok]   Moscow Mule instructions already specify ginger beer.")
        elif old_mm in mm_instr:
            actions.append((
                "Moscow Mule instructions: 8 oz of ginger ale -> 8 oz of ginger beer",
                "UPDATE recipes SET instructions = ? WHERE id = ?",
                (mm_instr.replace(old_mm, new_mm, 1), mm["id"]),
            ))
        else:
            problems.append("Moscow Mule instructions missing expected '8 oz of ginger ale' text.")

    if problems:
        print("\nPROBLEMS FOUND. Nothing will be written:")
        for p in problems:
            print("  -", p)
        conn.rollback()
        conn.close()
        sys.exit(1)

    print(f"\nPlanned actions ({len(actions)}):")
    for desc, _sql, _params in actions:
        print("  +", desc)

    before_counts = user_counts(conn)

    if not args.commit:
        conn.rollback()
        conn.close()
        print("\nDRY RUN. Nothing written. Re-run with --commit.")
        return

    try:
        for _desc, sql, params in actions:
            conn.execute(sql, params)
        conn.commit()
    except Exception as exc:
        conn.rollback()
        conn.close()
        print(f"\nFAILED, rolled back: {exc}")
        sys.exit(1)

    after_counts = user_counts(conn)
    conn.close()

    print("\nCOMMITTED.")
    print("User matcher counts (before -> after):")
    for b, a in zip(before_counts, after_counts):
        delta = "" if b == a else f"  (delta: {a[2]-b[2]:+d}/{a[3]-b[3]:+d})"
        print(f"  {b[0]:2d} {b[1]:<12} {b[2]:2d}/{b[3]:2d} -> {a[2]:2d}/{a[3]:2d}{delta}")


if __name__ == "__main__":
    main()
