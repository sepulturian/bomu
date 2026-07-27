"""
Automated spec sanity check over the whole recipe corpus.

This does NOT try to decide whether a spec is *correct* against the canon --
only a human or a published source can do that. What it does is find internal
inconsistencies, which is where the cheap, real bugs live: an ingredient row
the instructions never use, a measure on the row that disagrees with the
measure in the step, an `ingredient` requirement pointing at a checklist row
that does not exist (permanently unsatisfiable, per CLAUDE.md), a bottle_type
row with no type (silently skipped by the matcher, fails open).

Recipes that trip a check get web-verified by hand afterwards.
"""

import json
import os
import re
import sqlite3
import sys
import unicodedata
from collections import defaultdict

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bomu.db")


def load_corpus():
    """Read the live catalog straight from the database. Read-only, no writes,
    safe to run on the server at any time."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    corpus = {}
    for r in conn.execute("SELECT * FROM recipes ORDER BY name"):
        ings = conn.execute(
            "SELECT raw_name, raw_measure, requirement_type, bottle_type, "
            "ingredient_name, notes FROM recipe_ingredients "
            "WHERE recipe_id = ? ORDER BY sort_order", (r["id"],)
        ).fetchall()
        cols = r.keys()
        corpus[r["name"]] = {
            "name": r["name"],
            "glass": r["glass"],
            "instructions": r["instructions"],
            "about": r["about"] if "about" in cols else None,
            "tip": r["tip"] if "tip" in cols else None,
            "ingredients": [
                [i["raw_name"], i["raw_measure"], i["requirement_type"],
                 i["bottle_type"], i["ingredient_name"], i["notes"]] for i in ings
            ],
        }
    valid = {row[0] for row in conn.execute("SELECT name FROM ingredients")}
    conn.close()
    return corpus, valid

# Words that appear in a step to signal the build method.
METHOD_WORDS = {
    "shake": ("shake", "shaken", "shaking"),
    "stir": ("stir ", "stirred", "stir,", "stir."),
    "build": ("build", "fill the glass", "top with", "pour in"),
    "blend": ("blend", "blender"),
    "swizzle": ("swizzle",),
    "muddle": ("muddle", "press"),
}

# Glasses that should basically never receive a shaken-and-strained drink
# with no ice mentioned, and vice versa. Soft signal only.
STRAIGHT_UP_GLASSES = {"cocktail glass", "coupe", "martini glass", "nick and nora"}


def norm(s):
    """Lowercase, collapse whitespace, and strip accents. The accent strip
    matters: rows say 'Kahlua' and 'Cachaca' while the instructions say
    'Kahlúa' and 'cachaça', which read as a missing ingredient otherwise."""
    s = unicodedata.normalize("NFKD", (s or ""))
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return re.sub(r"\s+", " ", s.strip().lower())


def strip_marker(text):
    return text.replace("[BOMU_REWRITTEN_v1]", "").strip()


def split_shape(text):
    """Return (lead_prose, steps, trail_prose) for an instructions blob."""
    lines = [l.strip() for l in strip_marker(text).splitlines() if l.strip()]
    numbered = [i for i, l in enumerate(lines) if re.match(r"^\d+\.", l)]
    if not numbered:
        return lines, [], []
    first, last = numbered[0], numbered[-1]
    return lines[:first], lines[first:last + 1], lines[last + 1:]


# Measure tokens like "2 oz", "3/4 oz", "1 1/2 oz", "2 dashes", "1 tsp"
MEASURE_RE = re.compile(
    r"(\d+\s+\d+/\d+|\d+/\d+|\d+(?:\.\d+)?)\s*"
    r"(oz|ml|dash(?:es)?|tsp|tbsp|barspoon|leaves|leaf|cube[s]?|drop[s]?)",
    re.I,
)


def measures_in(text):
    out = set()
    for qty, unit in MEASURE_RE.findall(text):
        out.add((norm(qty), norm(unit).rstrip("s")))
    return out


def qty_to_float(q):
    q = q.strip()
    m = re.match(r"^(\d+)\s+(\d+)/(\d+)$", q)
    if m:
        return int(m.group(1)) + int(m.group(2)) / int(m.group(3))
    m = re.match(r"^(\d+)/(\d+)$", q)
    if m:
        return int(m.group(1)) / int(m.group(2))
    try:
        return float(q)
    except ValueError:
        return None


# Stop words so "Lime juice" matches a step saying "lime juice" but a row named
# "Fresh mint" isn't considered mentioned just because a step says "fresh".
GENERIC = {
    "fresh", "juice", "syrup", "the", "a", "of", "and", "or", "twist", "wedge",
    "wheel", "peel", "slice", "leaves", "leaf", "cold", "chilled", "dry",
    "sweet", "light", "dark", "aged", "white", "blanco", "reposado", "good",
    "bitters", "liqueur", "water", "soda", "ice", "cream", "sugar",
}


def keywords(raw_name):
    """Distinctive tokens from a row name. Min length 3, not 4: 'rye' and 'gin'
    are the whole identity of a row named 'Rye Whiskey' or 'London Dry Gin',
    and dropping them made every rye drink read as uncovered."""
    toks = re.findall(r"[a-z']+", norm(raw_name))
    strong = [t for t in toks if t not in GENERIC and len(t) >= 3]
    return strong or toks


def check(name, r, valid_ings):
    issues = []
    instr = strip_marker(r["instructions"])
    lead, steps, trail = split_shape(instr)
    body = norm(" ".join(steps) if steps else instr)
    full = norm(instr)

    # --- structural -------------------------------------------------------
    if not steps:
        issues.append(("SHAPE", "no numbered steps; renders as one prose blob"))
    if len(lead) > 1:
        issues.append(("SHAPE", f"{len(lead)} prose lines before step 1"))
    if trail:
        issues.append(("SHAPE", f"trailing prose renders as a numbered step: {trail[0][:60]}..."))

    # --- requirement integrity -------------------------------------------
    for raw, meas, rtype, btype, ing_name, notes in r["ingredients"]:
        if rtype == "bottle_type" and not (btype or "").strip():
            issues.append(("MATCHER", f"'{raw}' is bottle_type with no type; matcher silently skips it"))
        if rtype == "ingredient":
            if not (ing_name or "").strip():
                issues.append(("MATCHER", f"'{raw}' is ingredient with no ingredient_name"))
            elif ing_name not in valid_ings:
                issues.append(("MATCHER", f"'{raw}' -> '{ing_name}' is not in the ingredients table; unsatisfiable"))
        if rtype == "optional" and ing_name and ing_name not in valid_ings:
            issues.append(("DATA", f"optional '{raw}' -> unknown ingredient '{ing_name}'"))

    # --- coverage: row present but never used in the steps ----------------
    for raw, meas, rtype, btype, ing_name, notes in r["ingredients"]:
        kws = keywords(raw)
        if not kws:
            continue
        if not any(k in full for k in kws):
            sev = "MINOR" if rtype == "optional" else "COVERAGE"
            issues.append((sev, f"'{raw}' never mentioned in the instructions"))

    # --- measure agreement ------------------------------------------------
    # Only meaningful when the step actually states a quantity for that
    # ingredient. "Top with ginger beer" against a row reading 4 oz is not a
    # contradiction, it is a normal build instruction, and flagging it buried
    # the real disagreements in noise.
    step_measures = measures_in(body)
    for raw, meas, rtype, btype, ing_name, notes in r["ingredients"]:
        if not meas or rtype == "optional":
            continue
        rowm = measures_in(meas)
        if not rowm:
            continue
        kws = keywords(raw)
        quantified = any(
            re.search(
                MEASURE_RE.pattern + r"[^.;]{0,30}?" + re.escape(k),
                body, re.I,
            )
            for k in kws
        )
        if not quantified:
            continue
        for qty, unit in rowm:
            same_unit = [(q, u) for (q, u) in step_measures if u == unit]
            if not same_unit:
                continue
            rq = qty_to_float(qty)
            if rq is None:
                continue
            if not any(abs((qty_to_float(q) or -99) - rq) < 1e-6 for q, u in same_unit):
                issues.append((
                    "MEASURE",
                    f"'{raw}' row says {meas}, no matching {unit} figure in the steps "
                    f"(steps have: {sorted(set(q for q, u in same_unit))})",
                ))

    # --- method vs glass --------------------------------------------------
    methods = {m for m, words in METHOD_WORDS.items() if any(w in body for w in words)}
    glass = norm(r.get("glass"))
    if "shake" in methods and any(g in glass for g in ("highball", "collins")) and "strain" in body:
        if "over" not in body and "fresh ice" not in body:
            issues.append(("MINOR", "shaken and strained into a tall glass with no ice step"))
    if not methods and steps:
        issues.append(("MINOR", "no recognisable build method in the steps"))

    # --- egg white safety -------------------------------------------------
    if any("egg" in norm(i[0]) for i in r["ingredients"]):
        if not re.search(r"dry[- ]shake|without ice|no ice", body):
            issues.append(("TECHNIQUE", "egg white with no dry-shake step"))

    return issues


NAME_MATCH_TYPES = {"liqueur", "amaro", "other"}


def check_name_matching(corpus):
    """Cross-recipe check on name-matched requirements.

    matching.py satisfies a `liqueur` / `amaro` / `other` row by testing whether
    the row's keyword is a literal substring of a bottle's name. It lowercases
    but does NOT strip accents, so a row reading 'Bénédictine' can never be
    satisfied by a bottle the user typed as 'Benedictine'. And because the
    keyword is whatever the row happens to be called, two recipes wanting the
    same product under different names (Absinthe vs Pernod) disagree about
    whether the user owns it.

    Both failures are silent and permanent: the drink simply never appears.
    """
    issues = defaultdict(list)

    # Product families that are interchangeable in practice. If two recipes
    # name the same family differently, one of them is unreachable.
    FAMILIES = {
        "anise": ("absinthe", "pernod", "ricard", "pastis", "herbsaint"),
        "cherry liqueur": ("cherry heering", "cherry brandy", "cherry liqueur"),
    }

    seen = defaultdict(set)
    for name, r in corpus.items():
        for raw, meas, rtype, btype, ing_name, notes in r["ingredients"]:
            if rtype != "bottle_type" or (btype or "") not in NAME_MATCH_TYPES:
                continue
            key = (raw or "").strip()

            # 1. Accent trap: the key cannot match an ASCII-typed bottle.
            if any(ord(ch) > 127 for ch in key):
                ascii_key = norm(key)
                twin = [
                    other for other in seen
                    if norm(other) == ascii_key and other != key
                ]
                issues[name].append((
                    "NAMEMATCH",
                    f"'{key}' has an accent; matching.py does not strip accents, so a "
                    f"bottle typed '{ascii_key}' never matches"
                    + (f" (another recipe uses '{twin[0]}', which does match)" if twin else ""),
                ))

            # 2. Family split: same product, different keyword.
            for fam, members in FAMILIES.items():
                if norm(key) in members:
                    seen[f"family:{fam}"].add(norm(key))

            seen[key].add(name)

    for fam, members in FAMILIES.items():
        used = seen.get(f"family:{fam}", set())
        if len(used) > 1:
            for name, r in corpus.items():
                for raw, meas, rtype, btype, ing_name, notes in r["ingredients"]:
                    if rtype == "bottle_type" and norm(raw) in members:
                        others = sorted(used - {norm(raw)})
                        issues[name].append((
                            "NAMEMATCH",
                            f"'{raw}' is the same product as {others} used elsewhere, but "
                            f"name matching is literal, so one bottle cannot satisfy both",
                        ))
    return issues


def main():
    corpus, valid = load_corpus()

    by_sev = defaultdict(list)
    flagged = {}
    nm = check_name_matching(corpus)
    for name, r in sorted(corpus.items()):
        iss = check(name, r, valid) + nm.get(name, [])
        if iss:
            flagged[name] = iss
            for sev, msg in iss:
                by_sev[sev].append((name, msg))

    print(f"{len(corpus)} recipes checked, {len(flagged)} with at least one flag\n")
    order = ["MATCHER", "NAMEMATCH", "COVERAGE", "MEASURE", "TECHNIQUE", "SHAPE", "DATA", "MINOR"]
    for sev in order:
        rows = by_sev.get(sev, [])
        if not rows:
            continue
        print(f"---- {sev}  ({len(rows)}) " + "-" * (54 - len(sev)))
        for name, msg in rows:
            print(f"  {name:<28} {msg}")
        print()

    if "--json" in sys.argv:
        out = os.path.join(os.path.dirname(DB_PATH), "spec_flags.json")
        json.dump(flagged, open(out, "w"), indent=1)
        print(f"Wrote {out}")


if __name__ == "__main__":
    main()
