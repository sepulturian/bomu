"""
Split whiskey and vermouth into sub-types, on both bottles and recipe rows.

THE PROBLEM
-----------
matching.py grouped every whiskey into one fungible family and treated vermouth
as a single undifferentiated type. Two consequences, both live until now:

1. A recipe asking for rye accepted a bottle of Islay Scotch. Brooklyn and Ward
   Eight would cheerfully suggest themselves to someone holding only Laphroaig.

2. Sweet and dry vermouth were the same thing to the matcher, AND identical
   requirement types get deduplicated, so a recipe calling for both was
   satisfied by a single bottle. The Affinity showed as makeable for a user
   holding three sweet vermouths and no dry vermouth at all.

THE FIX
-------
Four new types: rye, irish, vermouth_sweet, vermouth_dry. The generic parents
('whiskey', 'vermouth') still accept every sub-type, so nothing that used to
match stops matching on the recipe side.

This script retags existing rows:

  bottles              by product name, e.g. "Cinzano Vermouth Rosso" -> sweet
  recipe_ingredients   by raw_name/notes, e.g. "Dry Vermouth" -> vermouth_dry

Anything genuinely ambiguous is LEFT ALONE on the generic type. matching.py
treats a generic bottle as permissive (it accepts 'whiskey' for a rye slot, and
'vermouth' for either sweet or dry), so an unresolved bottle keeps behaving
exactly as it does today rather than silently losing the user a drink.

WHY NAME MATCHING IS SAFE HERE
------------------------------
Vermouth labelling is unusually reliable: rosso/rossa/rojo/red/sweet all mean
sweet, and dry/extra dry/blanc-labelled-dry mean dry. Whiskey is similar: a
bottle saying "rye" is rye, one saying "Irish" is Irish. Where a label says
neither, we do nothing. The patterns below are conservative by design.

SAFETY
------
  * Dry run by default. Pass --commit to write.
  * Prints every proposed change, plus everything it is deliberately skipping.
  * Single transaction, rolls back on error.
  * Refuses to run if SQLite journal/WAL side files are present.
  * Idempotent: rows already on a sub-type are ignored.

USAGE
-----
    python3 migrate_spirit_subtypes.py
    python3 migrate_spirit_subtypes.py --commit
"""

import argparse
import os
import re
import sqlite3
import sys

DEFAULT_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bomu.db")


# --- vermouth -------------------------------------------------------------
# Order matters: dry is checked first because "Dry Vermouth Rosso" does not
# exist, but "extra dry" appearing alongside other words does.
VERMOUTH_RULES = [
    ("vermouth_dry", [
        r"\bdry\b",
        r"\bextra[- ]dry\b",
        r"\bsecco\b",          # Italian dry
        r"\bblanc de blancs\b",
    ]),
    ("vermouth_sweet", [
        r"\brosso\b", r"\brossa\b",   # Italian red
        r"\brojo\b",                   # Spanish red
        r"\brouge\b",                  # French red
        r"\bred\b",
        r"\bsweet\b",
        r"\bdolce\b",
        r"\bcarpano antica\b",         # famously sweet, label says neither
        r"\bpunt e mes\b",
    ]),
]

# --- whiskey --------------------------------------------------------------
WHISKEY_RULES = [
    ("rye", [
        r"\brye\b",
        r"\brittenhouse\b",
        r"\bsazerac\b",
        r"\bwhistlepig\b",
        r"\bold overholt\b",
        r"\bmichter's rye\b",
        r"\bknob creek rye\b",
    ]),
    ("irish", [
        r"\birish\b",
        r"\bjameson\b",
        r"\bredbreast\b",
        r"\btullamore\b",
        r"\bbushmills\b",
        r"\bpowers\b",
        r"\bgreen spot\b",
        r"\byellow spot\b",
    ]),
]


def _match(rules, text):
    """Return the first sub-type whose patterns hit, or None."""
    low = (text or "").lower()
    for subtype, patterns in rules:
        for p in patterns:
            if p and re.search(p, low):
                return subtype
    return None


def classify_vermouth(text):
    return _match(VERMOUTH_RULES, text)


def classify_whiskey(text):
    return _match(WHISKEY_RULES, text)


def guard_against_journal_files(db_path):
    bad = [db_path + s for s in ("-journal", "-wal", "-shm")
           if os.path.exists(db_path + s)]
    if bad:
        print("REFUSING TO RUN. Found SQLite side files next to the database:")
        for p in bad:
            print("   ", p)
        print("\nThese can silently roll back committed data (see 2026-07-23).")
        sys.exit(1)


def plan_bottles(conn):
    """Work out bottle retags. Returns (changes, skipped)."""
    changes, skipped = [], []
    # Older copies of the database predate multi-user and have no user_id.
    cols = {c["name"] for c in conn.execute("PRAGMA table_info(bottles)")}
    uid = "user_id" if "user_id" in cols else "NULL AS user_id"
    rows = conn.execute(
        f"SELECT id, {uid}, name, type, brand FROM bottles "
        "WHERE type IN ('vermouth', 'whiskey')"
    ).fetchall()

    for r in rows:
        blob = f"{r['name'] or ''} {r['brand'] or ''}"
        if r["type"] == "vermouth":
            new = classify_vermouth(blob)
        else:
            new = classify_whiskey(blob)

        if new:
            changes.append((r["id"], r["name"], r["type"], new, r["user_id"]))
        else:
            skipped.append((r["id"], r["name"], r["type"], r["user_id"]))
    return changes, skipped


def plan_recipe_ingredients(conn):
    """Work out recipe row retags. Returns (changes, skipped)."""
    changes, skipped = [], []
    rows = conn.execute(
        "SELECT ri.id, ri.raw_name, ri.notes, ri.bottle_type, r.name AS recipe "
        "FROM recipe_ingredients ri JOIN recipes r ON r.id = ri.recipe_id "
        "WHERE ri.requirement_type = 'bottle_type' "
        "AND ri.bottle_type IN ('vermouth', 'whiskey')"
    ).fetchall()

    for r in rows:
        blob = f"{r['raw_name'] or ''} {r['notes'] or ''}"

        # "Rye or bourbon" is deliberately flexible; leaving it generic keeps
        # both acceptable, which is what the recipe intends.
        if re.search(r"\bor bourbon\b", blob, re.IGNORECASE):
            skipped.append((r["id"], r["recipe"], r["raw_name"], r["bottle_type"]))
            continue

        if r["bottle_type"] == "vermouth":
            new = classify_vermouth(blob)
        else:
            new = classify_whiskey(blob)

        if new:
            changes.append((r["id"], r["recipe"], r["raw_name"], r["bottle_type"], new))
        else:
            skipped.append((r["id"], r["recipe"], r["raw_name"], r["bottle_type"]))
    return changes, skipped


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commit", action="store_true", help="Actually write.")
    parser.add_argument("--db", default=DEFAULT_DB)
    args = parser.parse_args()

    guard_against_journal_files(args.db)
    if not os.path.exists(args.db):
        print(f"No database at {args.db}")
        sys.exit(1)

    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row
    print(f"Database: {args.db}\n")

    b_changes, b_skipped = plan_bottles(conn)
    r_changes, r_skipped = plan_recipe_ingredients(conn)

    print(f"=== BOTTLES: {len(b_changes)} to retag, {len(b_skipped)} left generic ===")
    for _id, name, old, new, uid in b_changes:
        print(f"    id={_id:<4} user={uid}  {name}")
        print(f"           {old} -> {new}")
    if b_skipped:
        print("\n  Left on the generic type (label does not say which):")
        for _id, name, typ, uid in b_skipped:
            print(f"    id={_id:<4} user={uid}  {name}  [{typ}]")

    print(f"\n=== RECIPE ROWS: {len(r_changes)} to retag, {len(r_skipped)} left generic ===")
    for _id, recipe, raw, old, new in r_changes:
        print(f"    {recipe:<26} {raw:<18} {old} -> {new}")
    if r_skipped:
        print("\n  Left on the generic type:")
        for _id, recipe, raw, typ in r_skipped:
            print(f"    {recipe:<26} {raw:<18} [{typ}]")

    if not b_changes and not r_changes:
        print("\nNothing to do.")
        conn.close()
        return

    if not args.commit:
        print("\nDRY RUN. Nothing was written.")
        print("Re-run with --commit to apply.")
        conn.close()
        return

    try:
        conn.executemany("UPDATE bottles SET type = ? WHERE id = ?",
                         [(new, _id) for _id, _n, _o, new, _u in b_changes])
        conn.executemany("UPDATE recipe_ingredients SET bottle_type = ? WHERE id = ?",
                         [(new, _id) for _id, _r, _raw, _o, new in r_changes])
        conn.commit()
    except Exception as exc:
        conn.rollback()
        print(f"FAILED, rolled back: {exc}")
        conn.close()
        sys.exit(1)

    print(f"\nDone. {len(b_changes)} bottles and {len(r_changes)} recipe rows retagged.")
    conn.close()


if __name__ == "__main__":
    main()
