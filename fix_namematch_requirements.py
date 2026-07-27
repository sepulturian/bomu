# -*- coding: utf-8 -*-
"""Fix name-matched requirements that can never be satisfied.

WHY
---
Found by the spec audit, not by any user report, because the failure is silent:
the drink simply never appears and nobody knows to complain.

matching.py satisfies a `liqueur` / `amaro` / `other` requirement by checking
whether the row's keyword is a literal substring of one of the user's bottle
names (`_liqueur_satisfied`). It lowercases both sides. It does **not** strip
accents, and it has no notion of two products being the same thing under
different names. So two separate classes of permanent miss:

  ACCENTS
    Vieux Carre's row is "Bénédictine". A user who typed their bottle in as
    "Benedictine", which is how the label reads and how anyone types it, never
    matches. Bobby Burns wants "Benedictine" and matches fine. Same bottle,
    same shelf, one drink shows and one does not.

    Same shape: El Diablo's "Crème de Cassis" vs Bourbon Renewal's
    "Creme de Cassis". El Presidente's "Orange Curaçao" vs Pegu Club's
    "Orange Curacao".

  FAMILY SPLITS
    Sazerac asks for "Ricard" and Zombie asks for "Pernod". Both are brands of
    pastis, and every other anise drink in the catalog (Corpse Reviver #2,
    Death in the Afternoon, Morning Glory Fizz, Remember the Maine) asks for
    "Absinthe". A user with a bottle labelled Absinthe can make four of those
    six. Requiring a specific brand name is not a real requirement, it is a
    typo with consequences.

    Same shape: Singapore Sling's "Cherry brandy" vs Blood and Sand's and
    Remember the Maine's "Cherry Heering".

Also cleaned up here: four `optional` rows pointing at ingredient names that do
not exist in the `ingredients` table (Nutmeg, Pineapple Slice, Cucumber Slice,
Strawberry). Optional rows never block makeability so these were harmless, but
they are dead references and they make the data lie about what is on the
checklist.

THE REAL FIX IS IN matching.py, NOT HERE
----------------------------------------
This script repairs the data. It does not stop the next accented liqueur from
being added, or the next brand name from being used where a category belongs.
Per the lesson recorded in CLAUDE.md on 2026-07-25: fixing the source that
produced a bad value does not fix the shape of the hole it went through. The
durable fix is to accent-normalise inside `_liqueur_keys` so the comparison
stops being accent-sensitive at all. That is a code change and belongs in the
same commit as this script.

EXPECTED IMPACT
---------------
This one WILL move makeable and one-away counts, unlike migrate_recipe_about.py
which must not. Record the counts before and after for at least user 1 and
user 4, because those are the two with real shelves.

USAGE
-----
    python3 fix_namematch_requirements.py            # dry run, prints the plan
    python3 fix_namematch_requirements.py --commit   # writes

Idempotent. Every change is matched on the current value, so a second run finds
nothing to do.
"""

import os
import sqlite3
import sys

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bomu.db")


# (recipe name, current raw_name, new raw_name, new notes)
#
# The notes field matters as much as the name: _liqueur_keys() builds match
# candidates from BOTH raw_name and notes, so a good notes value is a second
# chance to match. Each note below names the product plainly and keeps the
# brand as an example rather than as the requirement.
REQUIREMENT_FIXES = [
    (
        "Vieux Carré", "Bénédictine", "Benedictine",
        "Benedictine DOM herbal liqueur",
    ),
    (
        "El Diablo", "Crème de Cassis", "Creme de Cassis",
        "Creme de Cassis blackcurrant liqueur",
    ),
    (
        "El Presidente", "Orange Curaçao", "Orange Curacao",
        "Orange Curacao, or triple sec at a push",
    ),
    (
        "Sazerac", "Ricard", "Absinthe",
        "Absinthe, pastis or Herbsaint, used as a rinse",
    ),
    (
        "Zombie", "Pernod", "Absinthe",
        "Absinthe or pastis, Pernod is the usual bottle",
    ),
    (
        "Singapore Sling", "Cherry brandy", "Cherry Heering",
        "Cherry liqueur, Cherry Heering is the classic choice",
    ),
]


# (recipe name, raw_name) -> clear the dangling ingredient_name.
# These are optional garnishes pointing at checklist rows that do not exist.
# Setting the reference to NULL is honest; inventing four new checklist rows
# for garnishes would start every existing user off with four fresh unticked
# boxes, which is a real cost for no gain. See CLAUDE.md, Adding recipes.
DANGLING_OPTIONAL = [
    ("Painkiller", "Freshly Grated Nutmeg"),
    ("Painkiller", "Pineapple Slice"),
    ("Pimm's Cup", "Cucumber slice"),
    ("Pimm's Cup", "Strawberry"),
]


# Repointing the requirement row leaves the instructions naming the old brand,
# so the step would say "rinse it with the Ricard" while the ingredient list
# above it says Absinthe. A user reading both would reasonably conclude the app
# is broken. (recipe, find, replace) -- applied only if `find` is present, so
# this stays idempotent and stays safe whichever order the two migrations run.
INSTRUCTION_WORDING = [
    ("Sazerac", "rinse it with the Ricard", "rinse it with the absinthe"),
    ("Zombie", "gold rum, Pernod, grenadine", "gold rum, absinthe, grenadine"),
]


def guard_side_files():
    """A stray SQLite journal rolled the live database back on 2026-07-23."""
    for suffix in ("-journal", "-wal", "-shm"):
        side = DB_PATH + suffix
        if os.path.exists(side):
            print(f"REFUSING TO RUN: {os.path.basename(side)} is present.")
            print("Close anything using the database and re-run. See CLAUDE.md, Gotchas.")
            sys.exit(1)


def main():
    commit = "--commit" in sys.argv
    guard_side_files()

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    try:
        planned = []
        already = []
        notfound = []

        for recipe, old_raw, new_raw, new_notes in REQUIREMENT_FIXES:
            row = conn.execute(
                "SELECT ri.id, ri.raw_name, ri.notes, ri.bottle_type "
                "FROM recipe_ingredients ri JOIN recipes r ON r.id = ri.recipe_id "
                "WHERE r.name = ? AND ri.raw_name = ?",
                (recipe, old_raw),
            ).fetchone()
            if row is None:
                done = conn.execute(
                    "SELECT 1 FROM recipe_ingredients ri JOIN recipes r ON r.id = ri.recipe_id "
                    "WHERE r.name = ? AND ri.raw_name = ?",
                    (recipe, new_raw),
                ).fetchone()
                (already if done else notfound).append(f"{recipe}: {old_raw}")
                continue
            planned.append(("req", row["id"], recipe, old_raw, new_raw, new_notes))

        for recipe, raw in DANGLING_OPTIONAL:
            row = conn.execute(
                "SELECT ri.id, ri.ingredient_name FROM recipe_ingredients ri "
                "JOIN recipes r ON r.id = ri.recipe_id "
                "WHERE r.name = ? AND ri.raw_name = ? AND ri.ingredient_name IS NOT NULL",
                (recipe, raw),
            ).fetchone()
            if row is None:
                already.append(f"{recipe}: {raw} (already cleared)")
                continue
            planned.append(("opt", row["id"], recipe, raw, None, row["ingredient_name"]))

        for recipe, find, repl in INSTRUCTION_WORDING:
            row = conn.execute(
                "SELECT id, instructions FROM recipes WHERE name = ?", (recipe,)
            ).fetchone()
            if row is None or find not in (row["instructions"] or ""):
                already.append(f"{recipe}: instructions wording (nothing to change)")
                continue
            planned.append(("instr", row["id"], recipe, find, repl,
                            (row["instructions"] or "").replace(find, repl)))

        print("PLAN\n" + "=" * 60)
        for kind, _rid, recipe, old_raw, new_raw, extra in planned:
            if kind == "req":
                print(f"  {recipe:<20} '{old_raw}' -> '{new_raw}'")
                print(f"  {'':<20} notes -> {extra!r}")
            elif kind == "instr":
                print(f"  {recipe:<20} instructions: {old_raw!r} -> {new_raw!r}")
            else:
                print(f"  {recipe:<20} optional '{old_raw}': clear dangling ingredient_name {extra!r}")
        if already:
            print("\nAlready done (no action):")
            for a in already:
                print(f"  {a}")
        if notfound:
            print("\nNOT FOUND, check these by hand before committing:")
            for a in notfound:
                print(f"  {a}")

        if not planned:
            print("\nNothing to do.")
            conn.close()
            return

        if not commit:
            print(f"\nDRY RUN. {len(planned)} changes staged, nothing written.")
            print("Re-run with --commit to apply.")
            print("\nRecord the counts BEFORE committing, this script is expected to move them:")
            print('  python3 -c "import matching; '
                  "print([ (u, matching.get_recommendations(u)['total_makeable'], "
                  "matching.get_recommendations(u)['total_one_away']) for u in (1,4,5) ])\"")
            conn.close()
            return

        for kind, rid, _recipe, _old, new_raw, extra in planned:
            if kind == "req":
                conn.execute(
                    "UPDATE recipe_ingredients SET raw_name = ?, notes = ? WHERE id = ?",
                    (new_raw, extra, rid),
                )
            elif kind == "instr":
                conn.execute(
                    "UPDATE recipes SET instructions = ? WHERE id = ?", (extra, rid))
            else:
                conn.execute(
                    "UPDATE recipe_ingredients SET ingredient_name = NULL WHERE id = ?",
                    (rid,),
                )

        conn.commit()
        print(f"\nDone. {len(planned)} rows updated.")
        print("Now re-check the counts and expect them to have gone UP:")
        print('  python3 -c "import matching; '
              "print([ (u, matching.get_recommendations(u)['total_makeable'], "
              "matching.get_recommendations(u)['total_one_away']) for u in (1,4,5) ])\"")

    except Exception as exc:
        conn.rollback()
        print(f"FAILED, rolled back: {exc}")
        conn.close()
        sys.exit(1)

    conn.close()


if __name__ == "__main__":
    main()
