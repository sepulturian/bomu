# -*- coding: utf-8 -*-
"""Two spec corrections found by the audit: the Sazerac's base spirit, and the
orphaned bitters rows left behind by an old bitters audit.

1. THE SAZERAC IS SPECCED WITH BOURBON
--------------------------------------
The drink is rye or cognac. The IBA spec is cognac; rye is the modern standard;
bourbon is listed by most sources as a substitution rather than the recipe. The
row was `bourbon`, and the recipe's own opening line admitted it: "Some use rye;
this version calls for bourbon."

That was tolerable while the page said nothing else. It stopped being tolerable
once the About copy went in, because that copy explains the drink is named after
a cognac brand "before rye took over". The page would have asserted one thing in
prose and required another in the ingredient list.

    THIS CHANGES WHO CAN MAKE IT, AND NOT ONLY UPWARD.

    FUNGIBLE_TYPES: `rye` accepts {rye, whiskey}, `bourbon` accepts {bourbon}.
    So switching the row from bourbon to rye:
      GAINS  anyone with a rye bottle, and anyone with a legacy bottle still
             sitting on the generic `whiskey` type
      LOSES  anyone whose only whiskey is typed `bourbon`

    That trade is deliberate but it is a judgement call, not an obvious fix.
    CLAUDE.md's own principle is that a false negative is worse than mild
    permissiveness, which argues the other way. The tiebreaker is that this is
    not a matcher question, it is a question of whether the app is telling the
    truth about what the drink is. A bourbon Sazerac under the name Sazerac is
    the app being confidently wrong, which is the same failure as the Vodka
    Cruiser and the Grape Soda.

    To revert: set SAZERAC_BASE_TYPE to "bourbon" and re-run. Everything else
    in this script is independent of it.

2. TWELVE ORPHANED BITTERS ROWS
-------------------------------
A past pass (the rows literally carry the note "added by bitters audit", which
clean_notes strips before display) added an optional bitters row to twelve
recipes without touching their instructions. So the ingredient list shows a
dash of Angostura and the method never mentions it. They are `optional`, so
none of them ever blocked anything, which is exactly why nobody noticed.

The fix is not uniform, because the rows are not uniformly right. Test applied
to each: is a dash of bitters here a published spec or an established bartender
convention for THIS drink?

  KEEP, and name it in the method (6). Bitters genuinely belong and the step
  was simply incomplete. A Rob Roy without Angostura is not a Rob Roy, and the
  Pisco Sour's dash goes on the foam at the end, which is a technique note the
  method was silently omitting.

  REMOVE (6). Plausible-sounding but not part of the drink. Trader Vic's Mai
  Tai has no bitters, the Negroni has three bitter or aromatic components
  already, and nothing in the Sidecar, Daiquiri, Americano or Boulevardier
  canon calls for them. An optional row the app cannot justify is noise on the
  ingredient list, and since build_mixer_gap() now reads checklist labels out
  loud as shopping instructions, noise is not free.

  UNTOUCHED. The Tequila Sour's Angostura row is not part of this set: its note
  reads "Dashed over the foam", so it was added deliberately and documented.

USAGE
-----
    python3 fix_recipe_specs.py            # dry run, prints the plan
    python3 fix_recipe_specs.py --commit   # writes

Idempotent, and order-independent with respect to the other two migrations.
The instruction edits are targeted substring replacements applied only if the
target text is present, so migrate_recipe_about.py's renumbering cannot break
them and re-running finds nothing to do.
"""

import os
import sqlite3
import sys

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bomu.db")

# Flip to "bourbon" to revert change 1. See the module docstring.
SAZERAC_BASE_TYPE = "rye"
SAZERAC_BASE_NAME = "Rye whiskey"
SAZERAC_BASE_NOTE = "Rye traditionally, cognac historically. Bourbon works at a push."


# Bitters rows to keep, each paired with the instruction edit that makes the
# method mention them. (recipe, find, replace)
BITTERS_KEEP = [
    (
        "Dry Rob Roy",
        "Fill a mixing glass with ice and add the 2 1/2 oz Scotch.",
        "Fill a mixing glass with ice, then add the 2 1/2 oz Scotch and a dash of Angostura.",
    ),
    (
        "Bobby Burns Cocktail",
        "Add the Scotch, sweet vermouth, and Benedictine to a mixing glass",
        "Add the Scotch, sweet vermouth, Benedictine and a dash of Angostura to a mixing glass",
    ),
    (
        "Hot Toddy",
        "Add the honey and whiskey, then top with hot water.",
        "Add the honey, whiskey and a dash of Angostura, then top with hot water.",
    ),
    (
        "Whiskey Sour",
        "Pour in the 2 oz blended whiskey, add ice,",
        "Pour in the 2 oz blended whiskey and a dash of Angostura, add ice,",
    ),
    (
        "Vodka Martini",
        "Add the vodka and dry vermouth to a mixing glass",
        "Add the vodka, dry vermouth and a dash of orange bitters to a mixing glass",
    ),
    (
        "Pisco Sour",
        "The foam should settle into a clean, dense layer on top.",
        "The foam should settle into a clean, dense layer on top. Dash the Angostura "
        "over the foam at the very end, not into the shaker.",
    ),
]

# Bitters rows to delete outright. (recipe, raw_name)
BITTERS_REMOVE = [
    ("Americano", "Angostura bitters"),
    ("Boulevardier", "Angostura bitters"),
    ("Daiquiri", "Angostura bitters"),
    ("Mai Tai", "Angostura bitters"),
    ("Negroni", "Orange bitters"),
    ("Mezcal Negroni", "Orange bitters"),
    ("Sidecar", "Orange bitters"),
]
# Mezcal Negroni was NOT in the audit's flagged list and had to be found by
# hand. The coverage check treats a row as mentioned if any distinctive word
# from its name appears in the method, and "Orange bitters" matched the method's
# "Express the orange peel". A garnish covering for an unrelated ingredient is
# exactly the kind of false negative that makes an audit tool worth less than
# it looks. check_specs.py now special-cases bitters rows.

# The audit note is a dev tag. clean_notes() already hides it, but leaving it on
# the rows that survive means the data still says "added by bitters audit" about
# a row that is now a deliberate part of the recipe.
AUDIT_NOTE = "added by bitters audit"
KEPT_NOTES = {
    "Dry Rob Roy": "Canonical in a Rob Roy, not optional in spirit",
    "Bobby Burns Cocktail": "A dash rounds out the Benedictine",
    "Hot Toddy": "Standard addition, adds spice against the honey",
    "Whiskey Sour": "A dash on top is standard modern practice",
    "Vodka Martini": "Orange bitters is a recognised classic variation",
    "Pisco Sour": "Dashed over the foam at the end, not shaken in",
}


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
    planned = []
    already = []

    try:
        # --- 1. Sazerac base spirit -------------------------------------
        row = conn.execute(
            "SELECT ri.id, ri.raw_name, ri.bottle_type FROM recipe_ingredients ri "
            "JOIN recipes r ON r.id = ri.recipe_id "
            "WHERE r.name = 'Sazerac' AND ri.requirement_type = 'bottle_type' "
            "AND ri.bottle_type IN ('bourbon', 'rye', 'whiskey')"
        ).fetchone()
        if row is None:
            already.append("Sazerac: base spirit row not found, check by hand")
        elif row["bottle_type"] == SAZERAC_BASE_TYPE:
            already.append(f"Sazerac: base already {SAZERAC_BASE_TYPE}")
        else:
            planned.append(("sazerac", row["id"], "Sazerac",
                            f"{row['raw_name']} ({row['bottle_type']})",
                            f"{SAZERAC_BASE_NAME} ({SAZERAC_BASE_TYPE})", None))

        for find, repl in [
            ("dissolve the superfine sugar in 1 tsp water, then add 2 dashes Peychaud bitters and the bourbon",
             "dissolve the superfine sugar in 1 tsp water, then add 2 dashes Peychaud bitters and the rye"),
        ]:
            r = conn.execute("SELECT id, instructions FROM recipes WHERE name = 'Sazerac'").fetchone()
            if r and find in (r["instructions"] or ""):
                planned.append(("instr", r["id"], "Sazerac", find, repl,
                                r["instructions"].replace(find, repl)))
            else:
                already.append("Sazerac: instructions already name the rye")

        # --- 2a. Bitters rows to keep, with a method edit ----------------
        for recipe, find, repl in BITTERS_KEEP:
            r = conn.execute("SELECT id, instructions FROM recipes WHERE name = ?",
                             (recipe,)).fetchone()
            if r is None:
                already.append(f"{recipe}: recipe not found")
            elif find not in (r["instructions"] or ""):
                already.append(f"{recipe}: method already mentions the bitters")
            else:
                planned.append(("instr", r["id"], recipe, find, repl,
                                r["instructions"].replace(find, repl)))

            note_row = conn.execute(
                "SELECT ri.id, ri.notes FROM recipe_ingredients ri "
                "JOIN recipes r ON r.id = ri.recipe_id "
                "WHERE r.name = ? AND ri.notes = ?", (recipe, AUDIT_NOTE)).fetchone()
            if note_row is not None:
                planned.append(("note", note_row["id"], recipe, AUDIT_NOTE,
                                KEPT_NOTES[recipe], None))

        # --- 2b. Bitters rows to delete ----------------------------------
        for recipe, raw in BITTERS_REMOVE:
            r = conn.execute(
                "SELECT ri.id FROM recipe_ingredients ri JOIN recipes r ON r.id = ri.recipe_id "
                "WHERE r.name = ? AND ri.raw_name = ? AND ri.requirement_type = 'optional'",
                (recipe, raw)).fetchone()
            if r is None:
                already.append(f"{recipe}: {raw} already removed")
            else:
                planned.append(("delrow", r["id"], recipe, raw, None, None))

        # --- report -------------------------------------------------------
        print("PLAN\n" + "=" * 68)
        for kind, _rid, recipe, a, b, _extra in planned:
            if kind == "sazerac":
                print(f"  {recipe:<22} base spirit  {a}  ->  {b}")
            elif kind == "instr":
                print(f"  {recipe:<22} method text edited")
                print(f"  {'':<22}   - {a[:72]}")
                print(f"  {'':<22}   + {b[:72]}")
            elif kind == "note":
                print(f"  {recipe:<22} bitters note {a!r} -> {b!r}")
            elif kind == "delrow":
                print(f"  {recipe:<22} REMOVE optional row '{a}'")
        if already:
            print("\nNothing to do for:")
            for a in already:
                print(f"  {a}")

        if not planned:
            print("\nAlready applied. Nothing written.")
            conn.close()
            return

        if not commit:
            print(f"\nDRY RUN. {len(planned)} changes staged, nothing written.")
            print("Re-run with --commit to apply.")
            print("\nRecord the counts BEFORE committing. Only the Sazerac change can move")
            print("them, and it can move them DOWN for a bourbon-only shelf:")
            print('  python3 -c "import matching; '
                  "print([(u, matching.get_recommendations(u)['total_makeable'], "
                  "matching.get_recommendations(u)['total_one_away']) for u in (1,4,5)])\"")
            conn.close()
            return

        for kind, rid, _recipe, _a, _b, extra in planned:
            if kind == "sazerac":
                conn.execute(
                    "UPDATE recipe_ingredients SET raw_name = ?, bottle_type = ?, notes = ? "
                    "WHERE id = ?",
                    (SAZERAC_BASE_NAME, SAZERAC_BASE_TYPE, SAZERAC_BASE_NOTE, rid))
            elif kind == "instr":
                conn.execute("UPDATE recipes SET instructions = ? WHERE id = ?", (extra, rid))
            elif kind == "note":
                conn.execute("UPDATE recipe_ingredients SET notes = ? WHERE id = ?", (_b, rid))
            elif kind == "delrow":
                conn.execute("DELETE FROM recipe_ingredients WHERE id = ?", (rid,))

        conn.commit()
        print(f"\nDone. {len(planned)} changes applied.")
        print("Re-check the counts. Only the Sazerac should have moved:")
        print('  python3 -c "import matching; '
              "print([(u, matching.get_recommendations(u)['total_makeable'], "
              "matching.get_recommendations(u)['total_one_away']) for u in (1,4,5)])\"")

    except Exception as exc:
        conn.rollback()
        print(f"FAILED, rolled back: {exc}")
        conn.close()
        sys.exit(1)

    conn.close()


if __name__ == "__main__":
    main()
