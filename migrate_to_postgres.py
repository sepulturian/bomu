"""Migrate bomu_live.db (SQLite) into Neon Postgres configured in .env."""

import os
import sqlite3
import sys
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

load_dotenv(ROOT / ".env")

import database  # noqa: E402
import matching  # noqa: E402

TABLES_IN_ORDER = [
    (
        "users",
        ["id", "username", "password_hash", "created_at"],
        "(id)",
    ),
    (
        "ingredients",
        ["id", "name", "category", "in_stock"],
        "(id)",
    ),
    (
        "recipes",
        ["id", "name", "glass", "instructions", "image_url", "cocktaildb_id", "source", "added_date", "about", "tip"],
        "(id)",
    ),
    (
        "recipe_ingredients",
        ["id", "recipe_id", "raw_name", "raw_measure", "requirement_type", "bottle_type", "ingredient_name", "notes", "sort_order"],
        "(id)",
    ),
    (
        "recipe_enhancements",
        ["id", "recipe_id", "name", "ingredient_name", "measure", "note", "source", "sort_order"],
        "(id)",
    ),
    (
        "bottles",
        ["id", "user_id", "name", "type", "brand", "added_date"],
        "(id)",
    ),
    (
        "user_stock",
        ["user_id", "ingredient_id"],
        "(user_id, ingredient_id)",
    ),
    (
        "ratings",
        ["user_id", "recipe_id", "thumb", "rated_at"],
        "(user_id, recipe_id)",
    ),
    (
        "scan_log",
        ["id", "user_id", "scanned_at"],
        "(id)",
    ),
]

SERIAL_TABLES = [
    "users",
    "ingredients",
    "recipes",
    "recipe_ingredients",
    "recipe_enhancements",
    "bottles",
    "scan_log",
]


def main():
    pg_url = os.environ.get("DATABASE_URL") or os.environ.get("POSTGRES_URL")
    if not pg_url:
        sys.exit("ERROR: DATABASE_URL or POSTGRES_URL must be set in .env before running.")

    source_path = ROOT / "bomu_live.db"
    if not source_path.exists():
        sys.exit(f"ERROR: Missing source SQLite database: {source_path}")

    database.DB_PATH = database.DEFAULT_DB_PATH
    database.init_db(force=True, seed=False)

    src = sqlite3.connect(source_path)
    src.row_factory = sqlite3.Row
    dst = database.get_db()

    try:
        for table, cols, conflict_cols in TABLES_IN_ORDER:
            rows = src.execute(f"SELECT {', '.join(cols)} FROM {table}").fetchall()
            if rows:
                placeholders = ", ".join(["?"] * len(cols))
                col_list = ", ".join(cols)
                sql = (
                    f"INSERT INTO {table} ({col_list}) VALUES ({placeholders}) "
                    f"ON CONFLICT {conflict_cols} DO NOTHING"
                )
                dst.executemany(sql, [tuple(r[c] for c in cols) for r in rows])
            print(f"Copied {len(rows):>3} source rows -> {table}")

        for table in SERIAL_TABLES:
            dst.execute(
                f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), "
                f"COALESCE((SELECT MAX(id) FROM {table}), 1))"
            )

        dst.commit()

        print("\nVerified Neon Postgres row counts:")
        for table, _cols, _conflict in TABLES_IN_ORDER:
            pg_count = dst.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            sq_count = src.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            status = "OK" if pg_count == sq_count else "DIFF"
            print(f"  {table:<20} pg={pg_count:<4} sqlite={sq_count:<4} [{status}]")
    finally:
        src.close()
        dst.close()

    recs = matching.get_recommendations(1)
    print(
        f"\nMatcher check for user_id=1 on Neon Postgres: "
        f"{recs['total_makeable']} makeable, {recs['total_one_away']} one-away"
    )


if __name__ == "__main__":
    main()
