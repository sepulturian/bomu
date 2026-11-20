#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Recipe spec & catalog QA fixes (2026-11-19).

Usage:
    python migrate_qa_specs_2026_11.py                 # dry run on bomu.db
    python migrate_qa_specs_2026_11.py --commit        # write bomu.db
    python migrate_qa_specs_2026_11.py --db copy.db    # dry run on copy
    python migrate_qa_specs_2026_11.py --postgres      # dry run on Neon
    python migrate_qa_specs_2026_11.py --postgres --commit

Fixes:
  1. Americano: add missing Soda water / club soda requirement (2 oz) and
     update step 3 instructions so it differs from Milano-Torino.
  2. White Russian: require Heavy cream (1 oz, Light cream / half-and-half)
     instead of tagging cream optional (was identical to Black Russian).
  3. Vodka Martini: downgrade Olive garnish from required ingredient to optional.
  4. Woo Woo: downgrade Lime wedge garnish from required ingredient to optional.
  5. Sazerac & Mint Julep: downgrade Water from required ingredient to optional.
  6. Dry Rob Roy: promote Angostura bitters from optional to required ingredient.
  7. Rename 'Martinez 2' -> 'Martinez'.

Unlike hygiene-only migrations, these fixes intentionally adjust matcher counts
toward honest specs; prints before -> after counts per user without failing on
expected deltas.
"""

import argparse
import os
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

DB_PATH = str(ROOT / "bomu.db")


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

    # 1. Americano: add Soda water / club soda + update instructions
    americano = conn.execute(
        "SELECT id, instructions FROM recipes WHERE name = ?", ("Americano",)
    ).fetchone()
    if not americano:
        problems.append("Recipe 'Americano' not found.")
    else:
        has_soda = conn.execute(
            "SELECT id FROM recipe_ingredients WHERE recipe_id = ? AND ingredient_name = ?",
            (americano["id"], "Soda water / club soda"),
        ).fetchone()
        if has_soda:
            print("  [ok]   Americano soda water row already present.")
        else:
            opt_rows = conn.execute(
                "SELECT id, sort_order FROM recipe_ingredients "
                "WHERE recipe_id = ? AND requirement_type = 'optional' "
                "ORDER BY sort_order DESC",
                (americano["id"],),
            ).fetchall()
            for r in opt_rows:
                actions.append((
                    f"Americano optional row {r['id']}: sort_order {r['sort_order']} -> {r['sort_order'] + 1}",
                    "UPDATE recipe_ingredients SET sort_order = ? WHERE id = ?",
                    (r["sort_order"] + 1, r["id"]),
                ))
            actions.append((
                "Americano: insert required Soda water / club soda (2 oz)",
                "INSERT INTO recipe_ingredients "
                "(recipe_id, raw_name, raw_measure, requirement_type, bottle_type, ingredient_name, notes, sort_order) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (americano["id"], "Soda water", "2 oz", "ingredient", None,
                 "Soda water / club soda", "Top to taste", 2),
            ))

        old_step = "3. Give it a brief stir to marry the two."
        new_step = "3. Top with 2 oz soda water and give it one gentle stir to marry without killing the fizz."
        instr = americano["instructions"] or ""
        if new_step in instr:
            print("  [ok]   Americano instructions already updated.")
        elif old_step in instr:
            actions.append((
                "Americano instructions: include 2 oz soda water in step 3",
                "UPDATE recipes SET instructions = ? WHERE id = ?",
                (instr.replace(old_step, new_step, 1), americano["id"]),
            ))
        else:
            problems.append("Americano instructions missing expected step 3 text.")

    # 2. White Russian: require Heavy cream (1 oz) + update instructions
    wr = conn.execute(
        "SELECT id, instructions FROM recipes WHERE name = ?", ("White Russian",)
    ).fetchone()
    if not wr:
        problems.append("Recipe 'White Russian' not found.")
    else:
        cream_row = conn.execute(
            "SELECT id, raw_name, raw_measure, requirement_type, ingredient_name, notes "
            "FROM recipe_ingredients WHERE recipe_id = ? AND raw_name = ?",
            (wr["id"], "Light cream"),
        ).fetchone()
        if not cream_row:
            problems.append("White Russian 'Light cream' row not found.")
        elif (
            cream_row["requirement_type"] == "ingredient"
            and cream_row["ingredient_name"] == "Heavy cream"
            and cream_row["raw_measure"] == "1 oz"
        ):
            print("  [ok]   White Russian cream row already required.")
        else:
            actions.append((
                f"White Russian row {cream_row['id']}: optional -> ingredient ('Heavy cream', 1 oz)",
                "UPDATE recipe_ingredients SET requirement_type = ?, ingredient_name = ?, "
                "raw_measure = ?, notes = ? WHERE id = ?",
                ("ingredient", "Heavy cream", "1 oz",
                 "Heavy cream or half-and-half, floated over the back of a spoon",
                 cream_row["id"]),
            ))

        old_wr = "3. Float light cream over the back of a spoon to taste."
        new_wr = "3. Float 1 oz light or heavy cream over the back of a spoon."
        wr_instr = wr["instructions"] or ""
        if new_wr in wr_instr:
            print("  [ok]   White Russian instructions already updated.")
        elif old_wr in wr_instr:
            actions.append((
                "White Russian instructions: include 1 oz cream measure in step 3",
                "UPDATE recipes SET instructions = ? WHERE id = ?",
                (wr_instr.replace(old_wr, new_wr, 1), wr["id"]),
            ))
        else:
            problems.append("White Russian instructions missing expected step 3 text.")

    # 3. Vodka Martini: Olive -> optional
    vm = conn.execute("SELECT id FROM recipes WHERE name = ?", ("Vodka Martini",)).fetchone()
    if not vm:
        problems.append("Recipe 'Vodka Martini' not found.")
    else:
        olive_row = conn.execute(
            "SELECT id, requirement_type FROM recipe_ingredients "
            "WHERE recipe_id = ? AND raw_name = ?",
            (vm["id"], "Olive"),
        ).fetchone()
        if not olive_row:
            problems.append("Vodka Martini 'Olive' row not found.")
        elif olive_row["requirement_type"] == "optional":
            print("  [ok]   Vodka Martini Olive already optional.")
        else:
            actions.append((
                f"Vodka Martini row {olive_row['id']}: Olive ingredient -> optional",
                "UPDATE recipe_ingredients SET requirement_type = ? WHERE id = ?",
                ("optional", olive_row["id"]),
            ))

    # 4. Woo Woo: Lime wedge -> optional
    ww = conn.execute("SELECT id FROM recipes WHERE name = ?", ("Woo Woo",)).fetchone()
    if not ww:
        problems.append("Recipe 'Woo Woo' not found.")
    else:
        lime_row = conn.execute(
            "SELECT id, requirement_type FROM recipe_ingredients "
            "WHERE recipe_id = ? AND raw_name = ?",
            (ww["id"], "Lime wedge"),
        ).fetchone()
        if not lime_row:
            problems.append("Woo Woo 'Lime wedge' row not found.")
        elif lime_row["requirement_type"] == "optional":
            print("  [ok]   Woo Woo Lime wedge already optional.")
        else:
            actions.append((
                f"Woo Woo row {lime_row['id']}: Lime wedge ingredient -> optional",
                "UPDATE recipe_ingredients SET requirement_type = ?, notes = ? WHERE id = ?",
                ("optional", "Garnish", lime_row["id"]),
            ))

    # 5. Sazerac & Mint Julep: Water -> optional (ingredient_name=NULL)
    for rname in ("Sazerac", "Mint Julep"):
        rec = conn.execute("SELECT id FROM recipes WHERE name = ?", (rname,)).fetchone()
        if not rec:
            problems.append(f"Recipe {rname!r} not found.")
            continue
        wrow = conn.execute(
            "SELECT id, requirement_type, ingredient_name FROM recipe_ingredients "
            "WHERE recipe_id = ? AND raw_name = ?",
            (rec["id"], "Water"),
        ).fetchone()
        if not wrow:
            problems.append(f"{rname} 'Water' row not found.")
        elif wrow["requirement_type"] == "optional" and wrow["ingredient_name"] is None:
            print(f"  [ok]   {rname} Water already optional.")
        else:
            actions.append((
                f"{rname} row {wrow['id']}: Water -> optional (ingredient_name=NULL)",
                "UPDATE recipe_ingredients SET requirement_type = ?, ingredient_name = ? WHERE id = ?",
                ("optional", None, wrow["id"]),
            ))

    # 6. Dry Rob Roy: Angostura bitters optional -> ingredient
    drr = conn.execute("SELECT id FROM recipes WHERE name = ?", ("Dry Rob Roy",)).fetchone()
    if not drr:
        problems.append("Recipe 'Dry Rob Roy' not found.")
    else:
        ang_row = conn.execute(
            "SELECT id, requirement_type FROM recipe_ingredients "
            "WHERE recipe_id = ? AND raw_name = ?",
            (drr["id"], "Angostura bitters"),
        ).fetchone()
        if not ang_row:
            problems.append("Dry Rob Roy 'Angostura bitters' row not found.")
        elif ang_row["requirement_type"] == "ingredient":
            print("  [ok]   Dry Rob Roy Angostura bitters already required.")
        else:
            actions.append((
                f"Dry Rob Roy row {ang_row['id']}: Angostura bitters optional -> ingredient",
                "UPDATE recipe_ingredients SET requirement_type = ? WHERE id = ?",
                ("ingredient", ang_row["id"]),
            ))

    # 7. Martinez 2 -> Martinez
    m2 = conn.execute("SELECT id FROM recipes WHERE name = ?", ("Martinez 2",)).fetchone()
    m_new = conn.execute("SELECT id FROM recipes WHERE name = ?", ("Martinez",)).fetchone()
    if m_new and not m2:
        print("  [ok]   Recipe already named 'Martinez'.")
    elif m2 and m_new:
        problems.append("Both 'Martinez' and 'Martinez 2' exist; refusing to rename.")
    elif m2:
        actions.append((
            f"Rename recipe id {m2['id']}: 'Martinez 2' -> 'Martinez'",
            "UPDATE recipes SET name = ? WHERE id = ?",
            ("Martinez", m2["id"]),
        ))
    else:
        problems.append("Neither 'Martinez 2' nor 'Martinez' found.")

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
