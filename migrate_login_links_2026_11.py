#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Create the login_links table for single-use sign-in links (2026-11-21).

Usage (from the main checkout, Windows PowerShell):
    venv\\Scripts\\python.exe migrate_login_links_2026_11.py                 # dry run on bomu.db
    venv\\Scripts\\python.exe migrate_login_links_2026_11.py --commit        # write bomu.db
    venv\\Scripts\\python.exe migrate_login_links_2026_11.py --db copy.db    # dry run on a copy
    venv\\Scripts\\python.exe migrate_login_links_2026_11.py --postgres      # dry run on Neon
    venv\\Scripts\\python.exe migrate_login_links_2026_11.py --postgres --commit

Creates (DDL shared with database.init_db(), so the two can't drift):
  1. login_links (token_hash PK, user_id -> users ON DELETE CASCADE,
     created_at, expires_at, used_at). Stores SHA-256 hashes only.
  2. idx_login_links_user on login_links (user_id).

Idempotent: an existing table with the expected columns is reported [ok] and
left alone, so a re-run is a no-op. An existing table with other columns is a
problem and nothing is written.

The app can deploy before this runs: /signin/<token> shows its "this link has
expired" page while the table is missing, and every other page ignores it.
On SQLite, init_db() also creates the table whenever the app starts.

Expected effect on matching.get_recommendations() for all users: 0 (the
matcher never reads this table). The script checks it.
"""

import argparse
import os
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

DB_PATH = str(ROOT / "bomu.db")

EXPECTED_COLUMNS = {"token_hash", "user_id", "created_at", "expires_at", "used_at"}


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


def existing_columns(conn, postgres):
    """Column names of login_links, or None if the table doesn't exist."""
    if postgres:
        rows = conn.execute(
            """SELECT column_name FROM information_schema.columns
               WHERE table_schema = 'public' AND table_name = 'login_links'"""
        ).fetchall()
        return {r["column_name"] for r in rows} or None
    rows = conn.execute("PRAGMA table_info(login_links)").fetchall()
    return {r["name"] for r in rows} or None


def index_exists(conn, postgres):
    if postgres:
        row = conn.execute(
            """SELECT 1 FROM pg_indexes
               WHERE schemaname = 'public' AND tablename = 'login_links'
                 AND indexname = 'idx_login_links_user'"""
        ).fetchone()
    else:
        row = conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'index' AND name = 'idx_login_links_user'"
        ).fetchone()
    return row is not None


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
        table_ddl = database.LOGIN_LINKS_DDL_POSTGRES
    else:
        os.environ["FORCE_SQLITE"] = "1"
        if not os.path.exists(args.db):
            print(f"REFUSING TO RUN. {args.db} does not exist.")
            sys.exit(1)
        guard_side_files(args.db)
        database.DB_PATH = os.path.abspath(args.db)
        conn = sqlite3.connect(args.db)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        target_label = args.db
        table_ddl = database.LOGIN_LINKS_DDL_SQLITE

    print(f"Target database: {target_label}")
    print(f"Backend check:   {'postgres' if database._is_postgres() else 'sqlite'}\n")

    problems = []
    actions = []

    cols = existing_columns(conn, args.postgres)
    if cols is None:
        actions.append(("create table login_links", table_ddl))
    elif cols == EXPECTED_COLUMNS:
        print("  [ok]   login_links already exists with the expected columns.")
    else:
        problems.append(
            f"login_links exists with unexpected columns: {sorted(cols)} "
            f"(expected {sorted(EXPECTED_COLUMNS)})."
        )

    if cols is None or not index_exists(conn, args.postgres):
        actions.append(("create index idx_login_links_user", database.LOGIN_LINKS_INDEX_DDL))
    else:
        print("  [ok]   idx_login_links_user already exists.")

    if problems:
        print("\nPROBLEMS FOUND. Nothing will be written:")
        for p in problems:
            print("  -", p)
        conn.rollback()
        conn.close()
        sys.exit(1)

    print(f"\nPlanned actions ({len(actions)}):")
    for desc, _sql in actions:
        print("  +", desc)

    before_counts = user_counts(conn)

    if not args.commit:
        conn.rollback()
        conn.close()
        print("\nDRY RUN. Nothing written. Re-run with --commit.")
        return

    try:
        for _desc, sql in actions:
            conn.execute(sql)
        conn.commit()
    except Exception as exc:
        conn.rollback()
        conn.close()
        print(f"\nFAILED, rolled back: {exc}")
        sys.exit(1)

    cols_after = existing_columns(conn, args.postgres)
    after_counts = user_counts(conn)
    conn.close()

    print("\nCOMMITTED.")
    if cols_after != EXPECTED_COLUMNS:
        print(f"WARNING: login_links columns after commit: {sorted(cols_after or [])}")
        sys.exit(1)
    print("login_links columns: " + ", ".join(sorted(cols_after)))
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
