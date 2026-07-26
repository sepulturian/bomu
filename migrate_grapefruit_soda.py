"""Rename the "Grape Soda" checklist ingredient to "Grapefruit soda".

WHY
---
The row has never actually meant purple grape soda. Its only consumer is the
Paloma, whose recipe row already carries the note "Grapefruit soda (e.g.
Jarritos, Squirt)". So the data has been right and the label has been wrong.

That was harmless while the label was just a line on a long checklist. It stopped
being harmless on 2026-07-25, when build_mixer_gap() started ranking checklist
ingredients and telling users, by name, what to go buy. A wrong label in that
banner is the app confidently sending someone to the store for the wrong bottle.

WHAT IT DOES
------------
1. Renames the ingredient row to "Grapefruit soda".
2. Clears every user_stock tick on it. Anyone who ticked "Grape Soda" ticked it
   meaning purple grape soda, so carrying the tick forward would silently claim
   they can make a Paloma. Losing a tick is recoverable in one tap; a drink the
   app promises and the user can't make is the failure mode this whole rename
   exists to prevent.
3. Repoints the Paloma's recipe_ingredients row (raw_name + ingredient_name) and
   rewrites its note, which no longer needs to explain away a wrong name.

The checklist tile photo is handled separately: static/ingredients/grape_soda.jpg
is a picture of purple grape soda and has to be replaced with a grapefruit-soda
photo named grapefruit_soda.jpg, or the tile will show the wrong drink under the
right name. app.py matches photos to ingredients by slug, so the filename is the
whole of that wiring.

USAGE
-----
    python3 migrate_grapefruit_soda.py            # dry run, prints the plan
    python3 migrate_grapefruit_soda.py --commit   # writes

Idempotent: re-running after a successful commit is a no-op.
"""

import os
import sqlite3
import sys

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bomu.db")

OLD_NAME = "Grape Soda"
NEW_NAME = "Grapefruit soda"

# The Paloma's row. Matched on the recipe name so this can't hit anything else.
PALOMA_RECIPE = "Paloma"
NEW_RAW_NAME = "Grapefruit soda"
NEW_NOTE = "Jarritos, Squirt, Ting or any grapefruit soda"


def guard_side_files():
    """A stray SQLite journal rolled the live database back on 2026-07-23.
    Refuse to touch the file while one is present -- committing on top of an
    uncommitted journal is how that data was lost."""
    for suffix in ("-journal", "-wal", "-shm"):
        side = DB_PATH + suffix
        if os.path.exists(side):
            sys.exit(
                f"ABORT: found {os.path.basename(side)}.\n"
                "Another process has the database open, or a previous write did "
                "not finish cleanly. Resolve that before running this script."
            )


def main():
    commit = "--commit" in sys.argv
    guard_side_files()

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    try:
        # --- Read the current state -------------------------------------
        ing = conn.execute(
            "SELECT id, name FROM ingredients WHERE name = ?", (OLD_NAME,)
        ).fetchone()

        if ing is None:
            already = conn.execute(
                "SELECT id FROM ingredients WHERE name = ?", (NEW_NAME,)
            ).fetchone()
            if already:
                print(f"Nothing to do: '{NEW_NAME}' already exists (id {already['id']}).")
                return
            sys.exit(
                f"ABORT: no ingredient named '{OLD_NAME}' and none named "
                f"'{NEW_NAME}'. Refusing to guess."
            )

        ing_id = ing["id"]

        clash = conn.execute(
            "SELECT id FROM ingredients WHERE name = ? AND id != ?",
            (NEW_NAME, ing_id),
        ).fetchone()
        if clash:
            sys.exit(
                f"ABORT: an ingredient named '{NEW_NAME}' already exists "
                f"(id {clash['id']}). Renaming would create a duplicate row and "
                "split ticks across both. Merge them by hand."
            )

        ticks = conn.execute(
            """SELECT us.user_id, u.username
                 FROM user_stock us
                 LEFT JOIN users u ON u.id = us.user_id
                WHERE us.ingredient_id = ?""",
            (ing_id,),
        ).fetchall()

        recipe_rows = conn.execute(
            """SELECT ri.id, ri.raw_name, ri.ingredient_name, ri.notes, r.name AS recipe
                 FROM recipe_ingredients ri
                 JOIN recipes r ON r.id = ri.recipe_id
                WHERE ri.ingredient_name = ?""",
            (OLD_NAME,),
        ).fetchall()

        # --- Report -----------------------------------------------------
        print(f"Ingredient id {ing_id}: '{OLD_NAME}' -> '{NEW_NAME}'")
        print()

        if ticks:
            who = ", ".join(t["username"] or f"user {t['user_id']}" for t in ticks)
            print(f"Ticks to clear ({len(ticks)}): {who}")
            print("  These users ticked a row labelled 'Grape Soda'. Keeping the")
            print("  tick would tell them they can make a Paloma with the wrong soda.")
        else:
            print("Ticks to clear: none")
        print()

        if recipe_rows:
            print(f"Recipe rows to repoint ({len(recipe_rows)}):")
            for row in recipe_rows:
                print(f"  {row['recipe']}: raw_name '{row['raw_name']}' -> '{NEW_RAW_NAME}'")
                print(f"    note: {row['notes']!r}")
                print(f"       -> {NEW_NOTE!r}")
        else:
            print("Recipe rows to repoint: none")
            print("  Unexpected -- the Paloma was the only consumer. Check the data.")
        print()

        # Any OTHER recipe row still pointing at the old name by raw_name only
        strays = conn.execute(
            """SELECT r.name, ri.raw_name, ri.requirement_type
                 FROM recipe_ingredients ri
                 JOIN recipes r ON r.id = ri.recipe_id
                WHERE LOWER(ri.raw_name) LIKE '%grape soda%'
                  AND (ri.ingredient_name IS NULL OR ri.ingredient_name != ?)""",
            (OLD_NAME,),
        ).fetchall()
        if strays:
            print("Heads up -- rows mentioning grape soda that this script will NOT touch:")
            for s in strays:
                print(f"  {s['name']}: {s['raw_name']} ({s['requirement_type']})")
            print()

        if not commit:
            print("DRY RUN. Nothing written. Re-run with --commit to apply.")
            return

        # --- Write ------------------------------------------------------
        conn.execute("BEGIN")
        conn.execute("UPDATE ingredients SET name = ? WHERE id = ?", (NEW_NAME, ing_id))
        conn.execute("DELETE FROM user_stock WHERE ingredient_id = ?", (ing_id,))
        conn.execute(
            """UPDATE recipe_ingredients
                  SET raw_name = ?, ingredient_name = ?, notes = ?
                WHERE ingredient_name = ?""",
            (NEW_RAW_NAME, NEW_NAME, NEW_NOTE, OLD_NAME),
        )
        conn.commit()

        # --- Verify -----------------------------------------------------
        check_name = conn.execute(
            "SELECT name FROM ingredients WHERE id = ?", (ing_id,)
        ).fetchone()["name"]
        check_ticks = conn.execute(
            "SELECT COUNT(*) FROM user_stock WHERE ingredient_id = ?", (ing_id,)
        ).fetchone()[0]
        check_rows = conn.execute(
            "SELECT COUNT(*) FROM recipe_ingredients WHERE ingredient_name = ?",
            (NEW_NAME,),
        ).fetchone()[0]

        assert check_name == NEW_NAME, check_name
        assert check_ticks == 0, check_ticks

        print("COMMITTED.")
        print(f"  ingredient {ing_id} is now '{check_name}'")
        print(f"  {len(ticks)} tick(s) cleared, {check_ticks} remaining")
        print(f"  {check_rows} recipe row(s) now point at '{NEW_NAME}'")
        print()
        print("Still to do by hand:")
        print("  Put the new grapefruit_soda.jpg in static/ingredients/ and delete")
        print("  grape_soda.jpg, or the checklist tile will keep showing purple")
        print("  grape soda under the new name.")

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
