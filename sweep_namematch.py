#!/usr/bin/env python3
"""Read-only sweep: which name-matched bottle requirements can never match?

WHY THIS EXISTS

`matching._liqueur_satisfied` is a literal substring test. It builds candidate
keys from a row's `ingredient_name` and `notes` (the whole string, plus one
variant with NOISE_WORDS stripped) and asks whether any key of 4+ characters
appears inside the user's bottle name. It never splits the string into parts.

So a row whose notes read like a description rather than a product name can
never be satisfied by any bottle, no matter what the user owns:

    notes = 'Campari specifically'   -> key 'campari specifically'
    bottle = 'Campari'               -> 'campari specifically' not in 'campari'

The drink simply never appears. There is nothing on screen to explain it, which
is the same invisible-by-construction failure as the accent bug fixed on
2026-07-26 (see CLAUDE.md, The matcher). `check_specs.py` does not catch this:
its NAMEMATCH rules cover accents and brand-vs-category families, not "this
note is a sentence".

WHAT IT REPORTS

  BROKEN   Every key contains punctuation or a connective ('or', 'specifically',
           'e.g.', a comma, a bracket, a slash). No plausible bottle name can
           contain these. Zero judgement needed; these are certain.

  REVIEW   Keys are junk-free but carry a trailing generic descriptor, e.g.
           'Blue Curacao orange liqueur'. A bottle named exactly that would
           match, but nobody names a bottle that way. Needs an eyeball.

  IMPACT   Per user, how many currently-hidden recipes have a BROKEN/REVIEW row
           that a looser matcher WOULD have satisfied from a bottle they already
           own. This is a candidate count, not a promise. Confirm by eye before
           quoting it. (CLAUDE.md, 2026-07-25: simulating against an idealised
           bar overestimated by 5x.)

READ raw_name, NOT ingredient_name

`recipe_ingredients` carries both columns and they mean different things. On a
bottle_type row, `ingredient_name` is NULL and `raw_name` holds the product
name. matching.py reads `raw_name`. Reading the wrong one makes every row look
broken, because the clean single-product key vanishes and only the descriptive
`notes` string is left. See the comment on the query in main().

SAFETY

Read-only. Opens the database with mode=ro and issues no writes, so it is safe
to run on the live server without a backup. It still warns if a SQLite side
file is present, because a live journal means the rows being read may not be
the rows that survive.

USAGE

    python3 sweep_namematch.py                 # ./bomu.db, matcher from ./
    python3 sweep_namematch.py --bomu ~/bomu   # explicit project dir
    python3 sweep_namematch.py --json          # also write sweep_namematch.json
"""

import argparse
import json
import os
import re
import sqlite3
import sys

# Punctuation and connectives that cannot appear in a bottle's name. A key
# containing any of these is unsatisfiable by construction.
JUNK = re.compile(
    r"[(),/]"                       # brackets, comma, slash
    r"|\bor\b"                      # 'Cointreau or triple sec'
    r"|\bspecifically\b"
    r"|\be\.?g\.?\b"
    r"|\bstyle\b"                   # 'St-Germain style'
    r"|\bclassic choice\b"
    r"|\bat a push\b"
    r"|\bused as\b"                 # 'used as a rinse or a single dash'
    r"|\brebuilt after\b",          # placeholder text from the 2026-07-23 restore
    re.IGNORECASE,
)

# Words that describe a category rather than identify a product. A key ending
# in one of these is a description with a name buried in it.
#
# Deliberately excludes 'schnapps', 'bitters' and 'wine': those are part of the
# product name people put on a shelf ('Peach schnapps' is the bottle, 'Peach'
# is not), so stripping them would break the very rows that currently work.
TRAILING_DESCRIPTOR = re.compile(
    r"\b(liqueur|liquor|aperitif)\s*$", re.IGNORECASE
)

# Tokens too generic to prove a bottle is the right one on their own. 'white'
# must not let a bottle of White Rum satisfy White Creme de Cacao.
GENERIC_TOKENS = {
    "white", "green", "blue", "red", "dark", "light", "dry", "sweet", "aged",
    "old", "new", "the", "de", "di", "du", "no", "a", "an", "and", "or",
    "liqueur", "liquor", "brand", "classic", "choice", "specifically", "style",
    "push", "used", "rinse", "dash", "single", "specific", "rebuilt", "after",
    "db", "corruption",
}


def warn_side_files(db_path):
    """A journal/WAL/shm alongside the database means what we read may roll back."""
    found = [
        s for s in ("-journal", "-wal", "-shm") if os.path.exists(db_path + s)
    ]
    if found:
        print(
            "WARNING: SQLite side file(s) present: "
            + ", ".join(os.path.basename(db_path) + s for s in found)
            + "\n         Rows read here may not be the rows that survive. "
            "See CLAUDE.md, Gotchas.\n"
        )


def sub_phrases(text, fold):
    """Every contiguous run of words in `text`, longest first.

    Used only for the loose IMPACT test, to ask what a smarter matcher would
    have found. Never used to decide whether a row is well-formed.
    """
    tokens = [t for t in re.split(r"[^0-9a-z]+", fold(text)) if t]
    out = []
    for size in range(len(tokens), 0, -1):
        for i in range(len(tokens) - size + 1):
            gram = tokens[i : i + size]
            if all(t in GENERIC_TOKENS for t in gram):
                continue  # 'white', 'de', 'the' prove nothing
            phrase = " ".join(gram)
            if len(phrase) >= 4:
                out.append(phrase)
    return out


def classify(raw_name, notes, keys):
    """BROKEN, REVIEW or OK, plus the reason."""
    sources = [s for s in (raw_name, notes) if s]
    if not keys:
        return "BROKEN", "no keys at all; requirement is skipped silently"

    clean = [k for k in keys if not JUNK.search(k)]
    if not clean:
        return "BROKEN", "every key carries punctuation or a connective"

    # A key only helps if it is contiguous in one of its source strings. The
    # noise-stripped variant can splice words that were never adjacent:
    # 'Cointreau (orange liqueur)' -> 'cointreau orange', which appears in no
    # bottle name on earth.
    folded_sources = [s.lower() for s in sources]
    contiguous = [
        k for k in clean if any(k in _strip_accents(s) for s in folded_sources)
    ]
    if not contiguous:
        return "BROKEN", "only key is spliced from non-adjacent words"

    # Everything left is satisfiable by SOME bottle name. The remaining question
    # is whether it is satisfiable by a name a person would actually type.
    # 'Blue Curacao orange liqueur' survives every test above, because a bottle
    # named exactly that would match. Nobody names a bottle that.
    #
    # There is no clean way to tell 'White Creme de Cacao' (a real four-word
    # product) from 'Blue Curacao orange liqueur' (a two-word product wearing a
    # description) without knowing the products. So this deliberately over-flags:
    # any key needing more than two words gets an eyeball. A short REVIEW list
    # with some false positives beats a checker that quietly passes bad data.
    # (CLAUDE.md, 2026-07-26: a checker that cries wolf gets ignored, and one
    # that passes bad data is worse than none.)
    shortest = min(contiguous, key=lambda k: len(k.split()))
    if len(shortest.split()) > 2:
        stripped = TRAILING_DESCRIPTOR.sub("", shortest).strip()
        return "REVIEW", "shortest key is %d words ('%s'); is that a bottle name?" % (
            len(shortest.split()),
            stripped or shortest,
        )

    return "OK", ""


def _strip_accents(s):
    import unicodedata

    s = unicodedata.normalize("NFKD", s)
    return "".join(ch for ch in s if not unicodedata.combining(ch)).lower()


def suggest(raw_name, notes):
    """Cut a description down to the product name. A suggestion, not a fix."""
    source = notes or raw_name or ""
    cut = re.split(
        r"\s*[(,/]|\s+\bor\b|\s+\bspecifically\b|\s+\be\.?g\.?\b|\s+\bstyle\b",
        source,
        maxsplit=1,
    )[0]
    cut = TRAILING_DESCRIPTOR.sub("", cut).strip(" -,")
    return cut or source


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bomu", default=os.path.dirname(os.path.abspath(__file__)),
                    help="project dir holding bomu.db and matching.py")
    ap.add_argument("--db", default=None, help="override database path")
    ap.add_argument("--json", action="store_true", help="write sweep_namematch.json")
    args = ap.parse_args()

    bomu = os.path.expanduser(args.bomu)
    sys.path.insert(0, bomu)
    import matching  # noqa: E402  needs sys.path set first

    db_path = args.db or os.path.join(bomu, "bomu.db")
    if not os.path.exists(db_path):
        sys.exit("no database at %s" % db_path)
    warn_side_files(db_path)

    con = sqlite3.connect("file:%s?mode=ro" % db_path, uri=True)
    con.row_factory = sqlite3.Row

    # raw_name, NOT ingredient_name. `recipe_ingredients` has both, and they are
    # not interchangeable: `ingredient_name` points at the Mixers checklist and
    # is NULL on every bottle_type row, while `raw_name` holds the product name
    # the matcher actually uses. matching.py reads ing["raw_name"] in
    # _liqueur_satisfied, match_recipe and missing_ingredient_ids.
    #
    # The first version of this script read ingredient_name and so fed None as
    # the raw name, throwing away the clean key on every single row. It reported
    # 35 BROKEN and 8 REVIEW out of 84. Reading the right column, the same data
    # is 1 BROKEN and 6 REVIEW out of 87. A checker that reads the wrong column
    # does not under-report, it invents a catastrophe.
    rows = con.execute(
        "SELECT r.id recipe_id, r.name recipe, ri.id row_id, ri.raw_name n,"
        "       ri.notes nt, ri.bottle_type bt "
        "FROM recipe_ingredients ri JOIN recipes r ON r.id = ri.recipe_id "
        "WHERE ri.requirement_type = 'bottle_type' "
        "ORDER BY r.name"
    ).fetchall()

    name_matched, findings = [], []
    for r in rows:
        ing = {"bottle_type": r["bt"], "raw_name": r["n"]}
        if not matching._use_name_match(ing):
            continue
        name_matched.append(r)
        keys = matching._liqueur_keys(r["n"], r["nt"])
        verdict, reason = classify(r["n"], r["nt"], keys)
        if verdict != "OK":
            findings.append(
                {
                    "verdict": verdict,
                    "reason": reason,
                    "recipe_id": r["recipe_id"],
                    "recipe": r["recipe"],
                    "row_id": r["row_id"],
                    "name": r["n"],
                    "notes": r["nt"],
                    "keys": sorted(keys),
                    "suggest": suggest(r["n"], r["nt"]),
                }
            )

    total_recipes = con.execute("SELECT COUNT(*) FROM recipes").fetchone()[0]
    print("=" * 66)
    print("NAME-MATCH SWEEP")
    print("=" * 66)
    print("database          %s" % db_path)
    print("recipes           %d" % total_recipes)
    print("bottle_type rows  %d" % len(rows))
    print("name-matched      %d" % len(name_matched))
    broken = [f for f in findings if f["verdict"] == "BROKEN"]
    review = [f for f in findings if f["verdict"] == "REVIEW"]
    print("BROKEN            %d   (certain: can never match any bottle)" % len(broken))
    print("REVIEW            %d   (likely: needs an eyeball)" % len(review))
    print()

    for label, group in (("BROKEN", broken), ("REVIEW", review)):
        if not group:
            continue
        print("-" * 66)
        print("%s  (%d)" % (label, len(group)))
        print("-" * 66)
        for f in group:
            print("  %-24s row %s" % (f["recipe"], f["row_id"]))
            print("      notes    : %s" % f["notes"])
            print("      keys     : %s" % ", ".join(repr(k) for k in f["keys"]))
            print("      why      : %s" % f["reason"])
            print("      suggest  : %s" % f["suggest"])
        print()

    # ---- per-user impact -------------------------------------------------
    try:
        users = con.execute("SELECT id, username FROM users ORDER BY id").fetchall()
    except sqlite3.OperationalError:
        users = []
    if not users:
        print("No users table / no users. Skipping IMPACT.")
        print("(Expected on the stale local bomu.db. See CLAUDE.md, Gotchas.)")
    else:
        print("-" * 66)
        print("IMPACT  (candidates, confirm by eye before quoting)")
        print("-" * 66)
        print("  Counts recipes with a BROKEN/REVIEW row the user owns a bottle")
        print("  for. NOT the same as 'this many more drinks become makeable' --")
        print("  the recipe may still be blocked by something else. Fixing the")
        print("  rows and re-reading total_makeable is the only honest number.")
        print()
        suspect_by_recipe = {}
        for f in findings:
            suspect_by_recipe.setdefault(f["recipe_id"], []).append(f)

        for u in users:
            bottles = con.execute(
                "SELECT name, brand FROM bottles WHERE user_id = ?", (u["id"],)
            ).fetchall()
            shelf = [
                matching._fold(
                    "%s %s" % (b["name"] or "", b["brand"] or "")
                ).strip()
                for b in bottles
            ]
            hidden = []
            for recipe_id, group in suspect_by_recipe.items():
                for f in group:
                    strict = matching._liqueur_satisfied(
                        f["name"], f["notes"], shelf
                    )
                    if strict:
                        continue
                    loose = any(
                        p in bs
                        for p in sub_phrases(
                            f["notes"] or f["name"] or "", matching._fold
                        )
                        for bs in shelf
                    )
                    if loose:
                        hidden.append((f["recipe"], f["notes"]))
                        break
            print(
                "  %-12s %2d bottles   %2d recipe(s) with a bad row they could satisfy"
                % (u["username"], len(bottles), len(hidden))
            )
            for recipe, notes in sorted(hidden):
                print("       - %-22s (%s)" % (recipe, notes))
        print()

    if args.json:
        out = os.path.join(bomu, "sweep_namematch.json")
        with open(out, "w") as fh:
            json.dump(findings, fh, indent=2, ensure_ascii=False)
        print("wrote %s" % out)

    con.close()


if __name__ == "__main__":
    main()
