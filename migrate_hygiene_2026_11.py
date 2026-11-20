#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hygiene & DB parity migration (2026-11-19).

Usage:
    python migrate_hygiene_2026_11.py                 # dry run on bomu.db
    python migrate_hygiene_2026_11.py --commit        # write bomu.db
    python migrate_hygiene_2026_11.py --db copy.db    # dry run on copy
    python migrate_hygiene_2026_11.py --postgres      # dry run on Neon
    python migrate_hygiene_2026_11.py --postgres --commit

Fixes:
  1. Hugo Spritz row (#15): raw_name='Elderflower Liqueur', notes='St-Germain'
  2. Paloma instructions: 'grape soda.' -> 'grapefruit soda.'
  3. Ti' Punch instructions: 'Add 2 oz rum and stir.' -> 'Add 2 oz rhum agricole (or white rum) and stir.'
  4. Caesar instructions: 'and a squeeze of lime.' -> 'and 1/2 oz fresh lime juice.'
  5. Postgres only: verify no duplicate (recipe_id, name) or NULL source in
     recipe_enhancements, then ensure UNIQUE (recipe_id, name), NOT NULL /
     DEFAULT 0 parity, and idx_recipe_enhancements_recipe exist.

Expected effect on matching.get_recommendations() for all 5 existing users: 0
(no user owns an elderflower bottle, and instruction edits don't affect matching).
"""

import argparse
import os
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

DB_PATH = str(ROOT / "bomu.db")

INSTRUCTION_PATCHES = [
    (
        "Paloma",
        "then the grape soda.",
        "then the grapefruit soda.",
    ),
    (
        "Ti' Punch",
        "Add 2 oz rum and stir.",
        "Add 2 oz rhum agricole (or white rum) and stir.",
    ),
    (
        "Caesar",
        "and a squeeze of lime.",
        "and 1/2 oz fresh lime juice.",
    ),
]


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
        r = matching.get_recommendations(u["id"])
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

    # 1. Hugo Spritz row (#15)
    hugo = conn.execute("SELECT id FROM recipes WHERE name = ?", ("Hugo Spritz",)).fetchone()
    if not hugo:
        problems.append("Recipe 'Hugo Spritz' not found.")
    else:
        rows = conn.execute(
            "SELECT id, raw_name, notes FROM recipe_ingredients "
            "WHERE recipe_id = ? AND bottle_type = 'liqueur'",
            (hugo["id"],),
        ).fetchall()
        if len(rows) != 1:
            problems.append(f"Expected 1 liqueur row on Hugo Spritz, found {len(rows)}.")
        else:
            row = rows[0]
            if row["raw_name"] == "Elderflower Liqueur" and row["notes"] == "St-Germain":
                print("  [ok]   Hugo Spritz already migrated.")
            elif row["raw_name"] == "Elderflower Liqueur (St-Germain)":
                actions.append((
                    f"Hugo Spritz row {row['id']}: raw_name -> 'Elderflower Liqueur', notes -> 'St-Germain'",
                    "UPDATE recipe_ingredients SET raw_name = ?, notes = ? WHERE id = ?",
                    ("Elderflower Liqueur", "St-Germain", row["id"]),
                ))
            else:
                problems.append(
                    f"Unexpected Hugo Spritz liqueur row {row['id']}: "
                    f"raw_name={row['raw_name']!r}, notes={row['notes']!r}"
                )

    # 2-4. Paloma, Ti' Punch, Caesar instruction fixes
    for recipe_name, old_sub, new_sub in INSTRUCTION_PATCHES:
        rec = conn.execute(
            "SELECT id, instructions FROM recipes WHERE name = ?", (recipe_name,)
        ).fetchone()
        if not rec:
            problems.append(f"Recipe {recipe_name!r} not found.")
            continue
        instr = rec["instructions"] or ""
        if new_sub in instr:
            print(f"  [ok]   {recipe_name} instructions already migrated.")
        elif old_sub in instr:
            updated = instr.replace(old_sub, new_sub, 1)
            actions.append((
                f"{recipe_name}: {old_sub!r} -> {new_sub!r}",
                "UPDATE recipes SET instructions = ? WHERE id = ?",
                (updated, rec["id"]),
            ))
        else:
            problems.append(
                f"{recipe_name} instructions missing expected substring {old_sub!r}."
            )

    # 5. Postgres constraint / index parity on recipe_enhancements
    if args.postgres:
        dups = conn.execute(
            "SELECT recipe_id, name, COUNT(*) AS n FROM recipe_enhancements "
            "GROUP BY recipe_id, name HAVING COUNT(*) > 1"
        ).fetchall()
        if dups:
            problems.append(f"Duplicate (recipe_id, name) rows in recipe_enhancements: {len(dups)}")

        null_sources = conn.execute(
            "SELECT COUNT(*) FROM recipe_enhancements WHERE source IS NULL"
        ).fetchone()[0]
        if null_sources:
            problems.append(f"Found {null_sources} recipe_enhancements rows with NULL source.")

        if not problems:
            has_unique = conn.execute(
                """SELECT 1 FROM pg_constraint
                   WHERE conrelid = 'recipe_enhancements'::regclass
                     AND contype = 'u'
                     AND strpos(pg_get_constraintdef(oid), '(recipe_id, name)') > 0"""
            ).fetchone()
            if has_unique:
                print("  [ok]   Postgres UNIQUE (recipe_id, name) already exists.")
            else:
                actions.append((
                    "Postgres: add UNIQUE (recipe_id, name) on recipe_enhancements",
                    "ALTER TABLE recipe_enhancements "
                    "ADD CONSTRAINT recipe_enhancements_recipe_id_name_key UNIQUE (recipe_id, name)",
                    None,
                ))

            cols = {
                r["column_name"]: r
                for r in conn.execute(
                    """SELECT column_name, is_nullable, column_default
                       FROM information_schema.columns
                       WHERE table_schema = 'public' AND table_name = 'recipe_enhancements'"""
                ).fetchall()
            }
            if cols.get("source", {}).get("is_nullable") == "YES":
                actions.append((
                    "Postgres: SET NOT NULL on recipe_enhancements.source",
                    "ALTER TABLE recipe_enhancements ALTER COLUMN source SET NOT NULL",
                    None,
                ))
            if cols.get("sort_order", {}).get("is_nullable") == "YES":
                actions.append((
                    "Postgres: SET NOT NULL + DEFAULT 0 on recipe_enhancements.sort_order",
                    "ALTER TABLE recipe_enhancements "
                    "ALTER COLUMN sort_order SET DEFAULT 0, "
                    "ALTER COLUMN sort_order SET NOT NULL",
                    None,
                ))

            has_idx = conn.execute(
                """SELECT 1 FROM pg_indexes
                   WHERE schemaname = 'public'
                     AND tablename = 'recipe_enhancements'
                     AND indexname = 'idx_recipe_enhancements_recipe'"""
            ).fetchone()
            if has_idx:
                print("  [ok]   Postgres index idx_recipe_enhancements_recipe already exists.")
            else:
                actions.append((
                    "Postgres: create idx_recipe_enhancements_recipe",
                    "CREATE INDEX IF NOT EXISTS idx_recipe_enhancements_recipe "
                    "ON recipe_enhancements (recipe_id)",
                    None,
                ))

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
            if params is None:
                conn.execute(sql)
            else:
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
    changed = False
    for b, a in zip(before_counts, after_counts):
        delta = "" if b == a else "  <-- CHANGED"
        if b != a:
            changed = True
        print(f"  {b[0]:2d} {b[1]:<12} {b[2]:2d}/{b[3]:2d} -> {a[2]:2d}/{a[3]:2d}{delta}")
    if changed:
        print("WARNING: User counts moved unexpectedly!")
        sys.exit(1)


if __name__ == "__main__":
    main()
