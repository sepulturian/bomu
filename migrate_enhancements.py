#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create the `recipe_enhancements` table and populate it from enhance_text.py.

    python3 migrate_enhancements.py            # dry run, prints the plan
    python3 migrate_enhancements.py --commit   # writes

EXPECTED EFFECT ON THE MATCHER: NONE.

That is the verification, not a side note. matching.py never reads this table,
so makeable and one-away counts must be byte-identical before and after. If they
move, something is wrong and the transaction should not have been committed.
This is the same trick migrate_recipe_about.py used: a migration whose expected
effect is "zero" is a migration you can actually check.

WHAT IT REFUSES TO DO
---------------------
- Run if a SQLite journal/WAL side file is present. On 2026-07-23 a stray
  .db-journal rolled the live database back and ate committed data.
- Insert an enhancement naming a checklist ingredient that does not exist in
  the `ingredients` table. A dangling name shows the user a "not on your list
  yet" line pointing at nothing they can ever tick.
- Insert an enhancement for something the recipe already requires. If the spec
  already calls for orange bitters, suggesting orange bitters is noise, and the
  local bomu.db is a stale 100-recipe copy so the list in enhance_text.py
  cannot be trusted about this. Checked here against whatever database is
  actually being written to.
- Insert an enhancement with no source. Rule 1 of enhance_text.py.
- Insert for a recipe name that is not in the catalog. Reported loudly rather
  than skipped quietly: a name that does not match is a typo, and a typo that
  fails silently is how you end up with copy nobody ever sees.

Re-running is a no-op: rows are keyed on (recipe_id, name) and existing rows
are updated in place rather than duplicated.
"""

import argparse
import os
import sqlite3
import sys

from enhance_text import ENHANCEMENTS

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bomu.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS recipe_enhancements (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id       INTEGER NOT NULL,
    name            TEXT    NOT NULL,
    ingredient_name TEXT,
    measure         TEXT,
    note            TEXT,
    source          TEXT    NOT NULL,
    sort_order      INTEGER NOT NULL DEFAULT 0,
    UNIQUE (recipe_id, name),
    FOREIGN KEY (recipe_id) REFERENCES recipes (id) ON DELETE CASCADE
);
"""

INDEX = """
CREATE INDEX IF NOT EXISTS idx_recipe_enhancements_recipe
    ON recipe_enhancements (recipe_id);
"""


def guard_side_files(db_path):
    """Refuse to run if SQLite left a journal, WAL or shared-memory file behind.
    Committing on top of one of those is how the 2026-07-23 data loss happened."""
    stragglers = [
        p for p in (db_path + "-journal", db_path + "-wal", db_path + "-shm")
        if os.path.exists(p)
    ]
    if stragglers:
        print("REFUSING TO RUN. SQLite side files present:")
        for p in stragglers:
            print("   ", p)
        print("\nThe database may be mid-write or mid-rollback. Close every "
              "connection, confirm the file is clean, then try again.")
        sys.exit(1)


def build_plan(conn, allow_missing_recipes=False):
    """Resolve enhance_text.py against the database.
    Returns (rows, problems, warnings)."""
    recipe_ids = {
        r["name"]: r["id"]
        for r in conn.execute("SELECT id, name FROM recipes")
    }
    known_ingredients = {
        r["name"].lower(): r["name"]
        for r in conn.execute("SELECT name FROM ingredients")
    }

    rows, problems, warnings = [], [], []

    for recipe_name, entries in sorted(ENHANCEMENTS.items()):
        if recipe_name not in recipe_ids:
            msg = (f"NO SUCH RECIPE: {recipe_name!r} is not in the catalog. "
                   f"Check the spelling against the recipes table.")
            (warnings if allow_missing_recipes else problems).append(msg)
            continue
        rid = recipe_ids[recipe_name]

        # Everything this recipe ALREADY puts on the page, so a suggestion
        # cannot duplicate something the reader can already see.
        #
        # Deliberately includes requirement_type = 'optional'. Those rows are
        # already rendered with a grey "optional" pill in the Ingredients card,
        # and the local copy shows nine optional Angostura rows and four
        # optional orange bitters rows still sitting there. Listing the same
        # thing twice on one page under two different headings is worse than
        # listing it nowhere -- it reads as two different instructions.
        #
        # Both columns, because raw_name is the product name and
        # ingredient_name is the checklist key and either could collide.
        already_shown = set()
        for r in conn.execute(
            "SELECT raw_name, ingredient_name FROM recipe_ingredients "
            "WHERE recipe_id = ?",
            (rid,),
        ):
            for v in (r["raw_name"], r["ingredient_name"]):
                if v:
                    already_shown.add(v.strip().lower())

        for order, e in enumerate(entries):
            name = (e.get("name") or "").strip()
            source = (e.get("source") or "").strip()
            ing = e.get("ingredient")
            ing = ing.strip() if ing else None

            if not name:
                problems.append(f"{recipe_name}: entry {order} has no name.")
                continue
            if not source:
                problems.append(f"{recipe_name} / {name}: no source. Rule 1.")
                continue
            if ing and ing.lower() not in known_ingredients:
                problems.append(
                    f"{recipe_name} / {name}: ingredient {ing!r} is not in the "
                    f"ingredients checklist. Use an existing row or set it to "
                    f"None -- do NOT add a checklist row for a suggestion, it "
                    f"starts unticked for every existing user."
                )
                continue
            if ing and ing.lower() in already_shown:
                # A WARNING, not an error, and this distinction matters.
                #
                # Whether a collision exists is a property of the database, not
                # of enhance_text.py: the local copy is a stale 100-recipe
                # snapshot and the live server has had rows added and removed
                # since. The Negroni is the worked example -- the local copy
                # still carries an optional orange bitters row, the live server
                # does not, because it was one of seven removed on 2026-07-26.
                # The same entry is therefore correct on one database and a
                # duplicate on the other, and only the database can say which.
                #
                # Aborting the whole run over one collision would also mean a
                # single already-present garnish blocks 160 unrelated rows from
                # landing. Skip the row, say so loudly, keep going.
                warnings.append(
                    f"SKIPPED {recipe_name} / {name}: {ing!r} is already on "
                    f"this recipe's ingredient list, so it would render twice. "
                    f"Nothing to fix unless you expected it to appear."
                )
                continue

            rows.append({
                "recipe_id": rid,
                "recipe_name": recipe_name,
                "name": name,
                # Store the canonical casing from the ingredients table, so the
                # "in your stock" lookup can't miss on a casing difference.
                "ingredient_name": known_ingredients[ing.lower()] if ing else None,
                "measure": (e.get("measure") or None),
                "note": (e.get("note") or None),
                "source": source,
                "sort_order": order,
            })

    return rows, problems, warnings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--commit", action="store_true", help="actually write")
    ap.add_argument("--db", default=DB_PATH, help="database to migrate")
    ap.add_argument(
        "--allow-missing-recipes", action="store_true",
        help="Downgrade 'recipe not in catalog' from an error to a warning. "
             "This exists ONLY for testing against the stale local bomu.db, "
             "which is a 100-recipe pre-multi-user snapshot and is missing "
             "roughly 70 recipes that exist on the server. NEVER pass this on "
             "the live database: there, a name that does not match is a typo, "
             "and a typo that fails silently is copy nobody ever sees.",
    )
    args = ap.parse_args()

    guard_side_files(args.db)

    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    # The table has to exist before build_plan can be verified against it, but
    # CREATE TABLE IF NOT EXISTS inside the same transaction is safe to roll
    # back, so this stays honest on a dry run.
    conn.execute(SCHEMA)
    conn.execute(INDEX)

    rows, problems, warnings = build_plan(conn, args.allow_missing_recipes)

    if warnings:
        skips = [w for w in warnings if w.startswith("SKIPPED")]
        missing = [w for w in warnings if not w.startswith("SKIPPED")]
        if missing:
            print(f"{len(missing)} recipe(s) in enhance_text.py are not in this "
                  f"catalog. --allow-missing-recipes is on, so these were "
                  f"skipped instead of failing. Never pass that flag on the "
                  f"server, where a name that does not match is a typo.\n")
            for w in missing:
                print("  -", w)
            print()
        if skips:
            print(f"{len(skips)} entr(ies) skipped as already-shown:\n")
            for w in skips:
                print("  -", w)
            print()

    if problems:
        print(f"{len(problems)} PROBLEM(S). Nothing will be written.\n")
        for p in problems:
            print("  -", p)
        conn.rollback()
        conn.close()
        sys.exit(1)

    existing = {
        (r["recipe_id"], r["name"])
        for r in conn.execute("SELECT recipe_id, name FROM recipe_enhancements")
    }
    inserts = [r for r in rows if (r["recipe_id"], r["name"]) not in existing]
    updates = [r for r in rows if (r["recipe_id"], r["name"]) in existing]

    recipes_touched = len({r["recipe_name"] for r in rows})
    total_recipes = conn.execute("SELECT COUNT(*) FROM recipes").fetchone()[0]

    print(f"Database:  {args.db}")
    print(f"Catalog:   {total_recipes} recipes")
    print(f"Planned:   {len(rows)} enhancement rows across {recipes_touched} "
          f"recipes ({total_recipes - recipes_touched} get nothing)")
    print(f"           {len(inserts)} new, {len(updates)} already present "
          f"(will be updated in place)\n")

    current = None
    for r in rows:
        if r["recipe_name"] != current:
            current = r["recipe_name"]
            print(f"  {current}")
        have = f" [checklist: {r['ingredient_name']}]" if r["ingredient_name"] else ""
        print(f"      - {r['name']}{have}")

    if not args.commit:
        conn.rollback()
        conn.close()
        print("\nDRY RUN. Nothing written. Re-run with --commit.")
        return

    try:
        for r in rows:
            conn.execute(
                """
                INSERT INTO recipe_enhancements
                    (recipe_id, name, ingredient_name, measure, note, source, sort_order)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (recipe_id, name) DO UPDATE SET
                    ingredient_name = excluded.ingredient_name,
                    measure         = excluded.measure,
                    note            = excluded.note,
                    source          = excluded.source,
                    sort_order      = excluded.sort_order
                """,
                (r["recipe_id"], r["name"], r["ingredient_name"], r["measure"],
                 r["note"], r["source"], r["sort_order"]),
            )
        conn.commit()
    except Exception as exc:
        conn.rollback()
        conn.close()
        print(f"\nFAILED, rolled back: {exc}")
        sys.exit(1)

    n = conn.execute("SELECT COUNT(*) FROM recipe_enhancements").fetchone()[0]
    conn.close()
    print(f"\nCOMMITTED. recipe_enhancements now holds {n} rows.")
    print("Now verify the matcher did NOT move:")
    print('  python3 -c "import matching; r=matching.get_recommendations(1); '
          "print(r['total_makeable'], r['total_one_away'])\"")


if __name__ == "__main__":
    main()
