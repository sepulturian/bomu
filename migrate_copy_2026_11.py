#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Update `recipes.about` and `recipes.tip` from `about_text.py` (2026-11-20).

Usage:
    python migrate_copy_2026_11.py                 # dry run on bomu.db
    python migrate_copy_2026_11.py --commit        # write bomu.db
    python migrate_copy_2026_11.py --db copy.db    # dry run on copy
    python migrate_copy_2026_11.py --postgres      # dry run on Neon
    python migrate_copy_2026_11.py --postgres --commit

Updates ONLY `recipes.about` and `recipes.tip` without touching `instructions`,
`recipe_ingredients`, or `ingredients`. Expected effect on matcher counts: ZERO.
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
        "SELECT id, name, about, tip FROM recipes ORDER BY name"
    ).fetchall()
    db_names = {r["name"] for r in rows}

    problems = []
    missing_copy = sorted(db_names - set(ABOUT.keys()))
    if missing_copy:
        problems.append(f"Missing about_text.ABOUT entries for: {missing_copy}")
    extra_copy = sorted(set(ABOUT.keys()) - db_names)
    if extra_copy:
        problems.append(f"about_text.ABOUT keys not in DB: {extra_copy}")

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

    if problems:
        print("PROBLEMS FOUND. Nothing will be written:")
        for p in problems:
            print("  -", p)
        conn.rollback()
        conn.close()
        sys.exit(1)

    with_tip = sum(1 for r in rows if (ABOUT[r["name"]].get("tip") or "").strip())
    print(f"Catalog:         {len(rows)} recipes ({len(rows)} abouts, {with_tip} tips)")
    print(f"Planned updates: {len(updates)} recipe(s)")
    for _rid, rname, na, nt in updates[:5]:
        print(f"  ~ {rname:<24} about={(na or '')[:60]}...")
    if len(updates) > 5:
        print(f"  ... and {len(updates) - 5} more.")

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
    print(f"\nCOMMITTED {len(updates)} updates. Matcher counts verified unchanged:")
    for b in before_counts:
        print(f"  {b[0]:2d} {b[1]:<12} {b[2]:2d}/{b[3]:2d}")


if __name__ == "__main__":
    main()
