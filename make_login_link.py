#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Print a single-use sign-in link for a Bomu user. Laptop only: never on the web.

Usage (from the main checkout, Windows PowerShell):
    venv\\Scripts\\python.exe make_login_link.py Avishka
    venv\\Scripts\\python.exe make_login_link.py Avishka --db scratch.db --base-url http://127.0.0.1:5055

With the main checkout's .env this writes to LIVE NEON; the first line it
prints says which database it reached. --db points it at a SQLite file
instead (a scratch copy for testing).

The link opens a "Sign in as <name>" page; the button on it signs the friend
in and takes them to /account/password to choose a new password. It works
once and lasts 7 days, and making a new link for someone switches off their
earlier unused ones. Send it privately: whoever holds it can get into that
account until it's used or expires.

Prints the backend, the user, the expiry and the link. Nothing else secret:
only the token's SHA-256 is stored, and the token itself exists only in the
printed link. Needs the login_links table (migrate_login_links_2026_11.py).
"""

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

DEFAULT_BASE_URL = "https://www.bomu.lol"


def main():
    ap = argparse.ArgumentParser(description="Print a single-use sign-in link.")
    ap.add_argument("username", help="the user's username (any case)")
    ap.add_argument("--db", help="use this SQLite file instead of DATABASE_URL")
    ap.add_argument("--base-url", default=DEFAULT_BASE_URL,
                    help=f"site the link points at (default {DEFAULT_BASE_URL})")
    args = ap.parse_args()

    # Only this folder's .env: a parent folder's (a worktree's main checkout)
    # must not silently send the write to Neon.
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
    import database
    import login_links

    if args.db:
        os.environ["FORCE_SQLITE"] = "1"
        database.DB_PATH = os.path.abspath(args.db)

    if database._is_postgres():
        print("Backend: postgres (DATABASE_URL). This is the LIVE database.")
    else:
        path = database.DB_PATH
        print(f"Backend: SQLITE {path}")
        if not os.path.exists(path):
            print("REFUSING TO RUN. That file does not exist.")
            sys.exit(1)
        stragglers = [p for p in (path + "-journal", path + "-wal", path + "-shm")
                      if os.path.exists(p)]
        if stragglers:
            print("REFUSING TO RUN. SQLite side files present: " + ", ".join(stragglers))
            sys.exit(1)

    conn = database.get_db()
    try:
        ready = login_links.table_exists(conn)
    finally:
        conn.close()
    if not ready:
        flag = " --postgres" if database._is_postgres() else ""
        print("No login_links table yet. Run migrate_login_links_2026_11.py"
              f"{flag} (dry run), then again with --commit.")
        sys.exit(1)

    user = database.get_user_by_username(args.username.strip())
    if user is None:
        conn = database.get_db()
        names = [r["username"] for r in conn.execute(
            "SELECT username FROM users ORDER BY id").fetchall()]
        conn.close()
        print(f"No user named {args.username!r}. Users: {', '.join(names)}")
        sys.exit(1)

    token, expires_at, revoked = login_links.create_link(user["id"])
    days = login_links.LINK_LIFETIME.days

    print(f"User:    {user['username']} (id {user['id']})")
    print(f"Expires: {expires_at:%Y-%m-%d %H:%M} UTC ({days} days). Works once.")
    if revoked:
        print(f"Switched off {revoked} earlier unused link(s) for this user.")
    print()
    print(f"{args.base_url.rstrip('/')}/signin/{token}")


if __name__ == "__main__":
    main()
