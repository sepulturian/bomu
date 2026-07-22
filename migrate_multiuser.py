"""One-time migration: single-user Bomu -> multi-user Bomu.

What it does, in order:
  1. Creates the users and user_stock tables (if missing).
  2. Adds a user_id column to bottles (if missing).
  3. Rebuilds ratings with a (user_id, recipe_id) primary key (if needed).
  4. Prompts for a username + password (typed by you, never stored in code),
     creates the first account, and assigns ALL existing bottles, ratings,
     and ticked checklist ingredients to it.

Safe to re-run: each step checks whether it's already done and skips.
Run it with the app STOPPED, and back up bomu.db first:
    cp bomu.db bomu.db.pre-multiuser
    python migrate_multiuser.py
"""

import getpass
import sqlite3
import sys

from werkzeug.security import generate_password_hash

from database import DB_PATH, init_db


def column_exists(conn, table, column):
    cols = [r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()]
    return column in cols


def main():
    # Step 1: init_db now creates users + user_stock (and nothing destructive).
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    # Step 2: bottles.user_id
    if not column_exists(conn, "bottles", "user_id"):
        print("Adding user_id column to bottles...")
        conn.execute("ALTER TABLE bottles ADD COLUMN user_id INTEGER")
        conn.commit()
    else:
        print("bottles.user_id already exists, skipping.")

    # Step 3: ratings rebuild (old schema had recipe_id as the primary key).
    if not column_exists(conn, "ratings", "user_id"):
        print("Rebuilding ratings table with (user_id, recipe_id) key...")
        conn.execute("ALTER TABLE ratings RENAME TO ratings_old")
        conn.execute("""
            CREATE TABLE ratings (
                user_id INTEGER NOT NULL,
                recipe_id INTEGER NOT NULL,
                thumb INTEGER NOT NULL,
                rated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, recipe_id),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
            )
        """)
        # Old rows are copied with user_id = 0 for now; claimed below.
        conn.execute("""
            INSERT INTO ratings (user_id, recipe_id, thumb, rated_at)
            SELECT 0, recipe_id, thumb, rated_at FROM ratings_old
        """)
        conn.execute("DROP TABLE ratings_old")
        conn.commit()
    else:
        print("ratings.user_id already exists, skipping.")

    # Step 4: create the first account and claim orphaned data.
    orphan_bottles = conn.execute(
        "SELECT COUNT(*) FROM bottles WHERE user_id IS NULL OR user_id = 0"
    ).fetchone()[0]
    orphan_ratings = conn.execute(
        "SELECT COUNT(*) FROM ratings WHERE user_id = 0"
    ).fetchone()[0]
    legacy_stock = conn.execute(
        "SELECT COUNT(*) FROM ingredients WHERE in_stock = 1"
    ).fetchone()[0]

    if orphan_bottles == 0 and orphan_ratings == 0:
        print("No unclaimed data found -- migration already complete. Done.")
        conn.close()
        return

    print(f"\nFound {orphan_bottles} bottles, {orphan_ratings} ratings and "
          f"{legacy_stock} ticked ingredients to claim.")
    print("Create YOUR account (this becomes the owner of all existing data):")
    username = input("  Username: ").strip()
    if not username:
        print("No username given, aborting. Nothing was claimed.")
        sys.exit(1)
    password = getpass.getpass("  Password (8+ chars, typing is hidden): ")
    if len(password) < 8:
        print("Password too short, aborting. Nothing was claimed.")
        sys.exit(1)
    confirm = getpass.getpass("  Same again: ")
    if password != confirm:
        print("Passwords don't match, aborting. Nothing was claimed.")
        sys.exit(1)

    existing = conn.execute(
        "SELECT id FROM users WHERE username = ?", (username,)
    ).fetchone()
    if existing:
        user_id = existing["id"]
        print(f"User '{username}' already exists (id {user_id}); claiming data for them.")
    else:
        cur = conn.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, generate_password_hash(password)),
        )
        user_id = cur.lastrowid
        print(f"Created user '{username}' (id {user_id}).")

    conn.execute(
        "UPDATE bottles SET user_id = ? WHERE user_id IS NULL OR user_id = 0",
        (user_id,),
    )
    conn.execute("UPDATE ratings SET user_id = ? WHERE user_id = 0", (user_id,))
    # Copy legacy global checklist ticks into this user's personal stock.
    conn.execute(
        """INSERT OR IGNORE INTO user_stock (user_id, ingredient_id)
           SELECT ?, id FROM ingredients WHERE in_stock = 1""",
        (user_id,),
    )
    conn.commit()

    b = conn.execute("SELECT COUNT(*) FROM bottles WHERE user_id = ?", (user_id,)).fetchone()[0]
    r = conn.execute("SELECT COUNT(*) FROM ratings WHERE user_id = ?", (user_id,)).fetchone()[0]
    s = conn.execute("SELECT COUNT(*) FROM user_stock WHERE user_id = ?", (user_id,)).fetchone()[0]
    print(f"\nDone. {username} now owns {b} bottles, {r} ratings, {s} stocked ingredients.")
    print("Restart/reload the app and log in with this account.")
    conn.close()


if __name__ == "__main__":
    main()
