"""
Retag ready-to-drink (RTD) products that the photo scanner recorded as base spirits.

THE PROBLEM
-----------
The vision prompt asked for a `type` from a fixed list and gave no guidance on
what counts as, say, vodka. So a can of Vodka Cruiser Pineapple (about 4% alcohol,
premixed, sweet) came back as type='vodka'.

That matters because matching.py treats vodka as a FUNGIBLE type: any bottle of
type 'vodka' satisfies any recipe asking for vodka. So an alcopop was quietly
telling a user they could make a Vodka Martini, a Screwdriver and a Moscow Mule.
Those are false positives, and false positives are worse than missing drinks
because they make the whole recommendation list untrustworthy.

THE FIX
-------
Retag matching bottles to type='other'. 'other' is in NAME_MATCH_TYPES, meaning
it is matched by name substring rather than by category, so the bottle stays
visible in the user's bar and can still satisfy a recipe that names it directly,
but it no longer stands in for a real bottle of spirit.

The scanner prompt in app.py has been updated separately so new scans get this
right at entry.

SAFETY
------
  * Dry run by default. Pass --commit to write.
  * Only touches bottles whose name matches a known RTD pattern AND whose
    current type is a base spirit.
  * Prints every proposed change for review before it happens.
  * Refuses to run if SQLite side files are present.

USAGE
-----
    python3 fix_rtd_bottles.py              # show what would change
    python3 fix_rtd_bottles.py --commit     # apply
"""

import argparse
import os
import re
import sqlite3
import sys

DEFAULT_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bomu.db")

# Types where a wrong tag actively creates false positives, because
# matching.py matches these by category rather than by name.
FUNGIBLE_SPIRIT_TYPES = {
    "gin", "vodka", "rum", "tequila", "mezcal", "whiskey",
    "bourbon", "scotch", "brandy", "cognac",
}

# Name patterns that indicate a premixed or low-alcohol product rather than a
# bottle of spirit. Word-boundary anchored so "cruiser" does not match
# something like "Cruiser Reserve Rum".
RTD_PATTERNS = [
    r"\bcruiser\b",           # Vodka Cruiser
    r"\bsmirnoff ice\b",
    r"\bhard seltzer\b",
    r"\bseltzer\b",
    r"\bcooler\b",
    r"\balcopop\b",
    r"\bpremix(ed)?\b",
    r"\bready[- ]to[- ]drink\b",
    r"\brtd\b",
    r"\bcanned cocktail\b",
    # "Jack Daniel's & Cola", "Bourbon and Coke". Note: no \b before the
    # separator, because & and + are not word characters and \b would never
    # match against a preceding space.
    r"(?:\band\b|&|\+)\s*(?:cola|coke|soda|tonic|ginger ale|lemonade)\b",
    r"\bmule in a can\b",
    r"\bvodka soda\b",
    r"\bgin(\s|-)?soda\b",
]

COMPILED = [re.compile(p, re.IGNORECASE) for p in RTD_PATTERNS]


def looks_like_rtd(name, brand):
    blob = f"{name or ''} {brand or ''}"
    return any(p.search(blob) for p in COMPILED)


def guard_against_journal_files(db_path):
    bad = [db_path + s for s in ("-journal", "-wal", "-shm")
           if os.path.exists(db_path + s)]
    if bad:
        print("REFUSING TO RUN. Found SQLite side files next to the database:")
        for p in bad:
            print("   ", p)
        print("\nThese can silently roll back committed data (see 2026-07-23).")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commit", action="store_true", help="Actually write.")
    parser.add_argument("--db", default=DEFAULT_DB, help="Path to bomu.db")
    args = parser.parse_args()

    guard_against_journal_files(args.db)

    if not os.path.exists(args.db):
        print(f"No database at {args.db}")
        sys.exit(1)

    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row

    cols = {r["name"] for r in conn.execute("PRAGMA table_info(bottles)")}
    has_user_id = "user_id" in cols

    select = "SELECT id, name, type, brand" + (", user_id" if has_user_id else "") + " FROM bottles"
    rows = conn.execute(select).fetchall()

    print(f"Database: {args.db}")
    print(f"Bottles scanned: {len(rows)}")
    print()

    candidates = []
    for r in rows:
        if r["type"] in FUNGIBLE_SPIRIT_TYPES and looks_like_rtd(r["name"], r["brand"]):
            candidates.append(r)

    if not candidates:
        print("No mis-tagged ready-to-drink products found. Nothing to do.")
        conn.close()
        return

    print(f"Found {len(candidates)} bottle(s) tagged as a base spirit that look")
    print("like ready-to-drink products:")
    print()
    for r in candidates:
        owner = f"  user_id={r['user_id']}" if has_user_id else ""
        print(f"    id={r['id']:<4} {r['name']}")
        print(f"           type: {r['type']}  ->  other{owner}")
    print()

    if not args.commit:
        print("DRY RUN. Nothing was written.")
        print("Review the list above, then re-run with --commit to apply.")
        conn.close()
        return

    try:
        conn.executemany(
            "UPDATE bottles SET type = 'other' WHERE id = ?",
            [(r["id"],) for r in candidates],
        )
        conn.commit()
    except Exception as exc:
        conn.rollback()
        print(f"FAILED, rolled back: {exc}")
        conn.close()
        sys.exit(1)

    print(f"Retagged {len(candidates)} bottle(s) to type='other'.")
    conn.close()


if __name__ == "__main__":
    main()
