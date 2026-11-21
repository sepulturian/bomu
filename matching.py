"""Cocktail matching logic.
Given the user's bottles + stocked ingredients, returns:
  - "makeable" recipes: every required ingredient is present
  - "one_away" recipes: exactly one required ingredient is missing
Garnishes and "to taste" stuff are ignored (requirement_type = 'optional').

Matching is split into two strategies:

  Fungible spirits (gin, rum, vodka, etc.) — match by category. Any gin
  satisfies any gin requirement.

  Non-fungible liqueurs (Campari, Maraschino, Cherry Heering, Baileys, etc.)
  — match by specific name. Asking for Campari does NOT match a Cointreau
  bottle just because they're both 'liqueur' type.
"""

import re
import unicodedata
from datetime import date

from database import get_all_recipes, get_all_bottles, get_all_ingredients, get_all_ratings


def _fold(s):
    """Lowercase and strip accents, for name matching only.

    Name-matched requirements are satisfied by literal substring search against
    the user's bottle names. That made the comparison accent-sensitive, so a
    row reading 'Bénédictine' could never be satisfied by a bottle the user had
    typed as 'Benedictine', which is how the label reads and how everyone types
    it. Bobby Burns (row: 'Benedictine') matched the same bottle fine. Same
    shelf, one drink visible and one not, with nothing on screen to explain it.

    Folding here rather than fixing the affected rows is deliberate. The rows
    were fixed too, in fix_namematch_requirements.py, but data fixes do not
    stop the next accented liqueur from being typed in. Guard where the value
    is consumed, not only where it is produced.
    """
    if not s:
        return ""
    s = unicodedata.normalize("NFKD", s)
    return "".join(ch for ch in s if not unicodedata.combining(ch)).lower()


# Category accepts THIS broader set when matching. e.g. recipe asks for
# generic "whiskey" → any whiskey/bourbon/scotch satisfies. "bourbon"
# specifically only accepts bourbon.
FUNGIBLE_TYPES = {
    # Generic parents accept every sub-type beneath them.
    "whiskey": {"whiskey", "bourbon", "scotch", "rye", "irish"},
    "bourbon": {"bourbon"},
    "scotch": {"scotch"},
    # Rye and Irish were added after the fact, so plenty of legacy bottles are
    # still sitting on the generic "whiskey" type. Accept those here: we don't
    # know a generic whiskey ISN'T rye, and being permissive about an unknown
    # beats a false negative. Bourbon and scotch stay strict because the
    # scanner has always identified those reliably.
    "rye": {"rye", "whiskey"},
    "irish": {"irish", "whiskey"},
    "brandy": {"brandy", "cognac"},
    "cognac": {"cognac"},
    "rum": {"rum"},
    "gin": {"gin"},
    "vodka": {"vodka"},
    "tequila": {"tequila", "mezcal"},  # mezcal can sub for tequila in a pinch
    "mezcal": {"mezcal"},
    # Sweet and dry vermouth are different products, not points on a scale.
    # A Martini wants dry, a Manhattan wants sweet, and an Affinity wants both
    # in the same glass. Same permissive rule for untyped legacy bottles.
    "vermouth": {"vermouth", "vermouth_sweet", "vermouth_dry"},
    "vermouth_sweet": {"vermouth_sweet", "vermouth"},
    "vermouth_dry": {"vermouth_dry", "vermouth"},
}

# These categories are too varied to match by type alone — Campari, Aperol,
# Cointreau, Maraschino, Baileys, Kahlua, Chartreuse, Pernod, Lillet, etc.
# are all different drinks and not interchangeable.
NAME_MATCH_TYPES = {"liqueur", "amaro", "other"}

# Specialty spirits that don't fit our broad categories cleanly. Even if Claude
# tagged Cachaca as 'rum' or Pisco as 'brandy' during import, we want to force
# a name-based match so a generic rum bottle doesn't satisfy a Caipirinha.
SPECIALTY_KEYWORDS = (
    "cachaca", "cachaça",
    "pisco",
    "sake",
    "soju",
    "aquavit", "akvavit",
    "schnapps",
    "shochu",
    "grappa",
    "calvados",
    "armagnac",
    "absinthe",
)


def _is_specialty(raw_name):
    if not raw_name:
        return False
    lower = _fold(raw_name)
    return any(kw in lower for kw in SPECIALTY_KEYWORDS)


def _liqueur_keys(raw_name, notes):
    """Extract candidate keywords to look for in bottle names. We try the full
    name, the name minus 'liqueur', and the notes field if present."""
    keys = set()
    for source in (raw_name, notes):
        if not source:
            continue
        s = _fold(source)
        keys.add(s.strip())
        # Strip noise words (at word boundaries) and brackets to isolate the brand/spirit name
        cleaned = re.sub(r"[()]", " ", s)
        cleaned = re.sub(r"\b(?:liqueur|liquor|the)\b", " ", cleaned)
        cleaned = " ".join(cleaned.split())  # collapse whitespace
        if cleaned:
            keys.add(cleaned)
    # Drop empties
    return {k for k in keys if k}


def _bottle_match_strings(bottles):
    """Build a list of lowercase 'name + brand' strings for substring matching."""
    out = []
    for b in bottles:
        name = _fold(b["name"] or "")
        brand = _fold(b["brand"] or "") if b["brand"] else ""
        out.append(f"{name} {brand}".strip())
    return out


def _liqueur_satisfied(raw_name, notes, bottle_strings):
    """Check whether ANY of the user's bottles' names contain the liqueur's
    distinctive keyword."""
    keys = _liqueur_keys(raw_name, notes)
    if not keys:
        return False
    for bs in bottle_strings:
        for k in keys:
            # Need at least 4 chars to avoid e.g. "the" matching everything
            if len(k) >= 4 and k in bs:
                return True
    return False


def _use_name_match(ingredient):
    """Decide whether to match this ingredient by specific name (vs. by category).
    True for liqueurs, amaros, 'other', and specialty spirits like cachaca/pisco
    even if Claude classified them as rum/brandy/etc."""
    req_type = ingredient.get("bottle_type")
    if req_type in NAME_MATCH_TYPES:
        return True
    if _is_specialty(ingredient.get("raw_name")):
        return True
    return False


def is_name_matched(ingredient):
    """Public helper indicating whether an ingredient matches by bottle name."""
    return _use_name_match(ingredient)


def _assign_distinct_bottles(slots, user_bottles):
    """Work out which category slots can be filled using a DIFFERENT bottle each.

    `slots` is a list of accepted-type sets, one per deduplicated bottle_type
    requirement. Returns the set of slot indices that CANNOT be filled.

    Why this is needed: checking each slot independently lets one bottle satisfy
    several slots at once. Cameron's Kick asks for Scotch and Irish whiskey, and
    a lone bottle of Laphroaig used to satisfy both, because Scotch is a member
    of the accepted set for a generic whiskey requirement. The drink's entire
    point is that they are two different whiskeys.

    Note that identical requirements are deduplicated by the caller BEFORE they
    reach this function, which is deliberate. Penicillin lists blended Scotch
    plus an Islay float; both are bottle_type 'scotch', they collapse to one
    slot, and one bottle of Scotch is a perfectly reasonable way to make it.
    Two genuinely different requirements are what we insist on separating.

    This is bipartite maximum matching solved with augmenting paths. Recipes top
    out at a handful of spirits, so the naive version is more than fast enough.
    """
    # Candidate bottle indices for each slot.
    candidates = []
    for accepted in slots:
        candidates.append([
            i for i, b in enumerate(user_bottles) if b["type"] in accepted
        ])

    bottle_to_slot = {}   # bottle index -> slot index currently holding it

    def try_assign(slot_idx, visited):
        for b_idx in candidates[slot_idx]:
            if b_idx in visited:
                continue
            visited.add(b_idx)
            # Free bottle, or its current owner can be rehoused elsewhere.
            holder = bottle_to_slot.get(b_idx)
            if holder is None or try_assign(holder, visited):
                bottle_to_slot[b_idx] = slot_idx
                return True
        return False

    unfilled = set()
    for slot_idx in range(len(slots)):
        if not try_assign(slot_idx, set()):
            unfilled.add(slot_idx)
    return unfilled


def matching_user_bottles(ingredient, user_bottles):
    """Given a recipe ingredient with requirement_type='bottle_type',
    return the list of user's bottles that would satisfy it. Empty if none."""
    if ingredient.get("requirement_type") != "bottle_type":
        return []
    if _use_name_match(ingredient):
        keys = _liqueur_keys(ingredient.get("raw_name"), ingredient.get("notes"))
        out = []
        for b in user_bottles:
            bs = _fold(f"{b['name'] or ''} {b['brand'] or ''}")
            for k in keys:
                if len(k) >= 4 and k in bs:
                    out.append(b)
                    break
        return out
    bottle_type = ingredient.get("bottle_type")
    if not bottle_type:
        return []
    accepted = FUNGIBLE_TYPES.get(bottle_type, {bottle_type})
    return [b for b in user_bottles if b["type"] in accepted]


def used_user_bottles(recipe_data, user_bottles, max_n=2):
    """For a makeable recipe, return up to max_n distinct user bottles that
    satisfy this recipe's bottle_type requirements. Iterates ingredients in
    sort order so the base spirit (typically first) leads, deduping by bottle id.
    Used by /recommend to show 'Use your: X' hints inline on each card."""
    seen = set()
    out = []
    for ing in recipe_data["ingredients"]:
        if ing["requirement_type"] != "bottle_type":
            continue
        matches = matching_user_bottles(ing, user_bottles)
        if not matches:
            continue
        b = matches[0]
        if b["id"] in seen:
            continue
        seen.add(b["id"])
        out.append(b)
        if len(out) >= max_n:
            break
    return out


def match_recipe(recipe_data, user_bottles, stocked_ingredient_names):
    """Check a single recipe.
    Returns ('makeable' | 'one_away' | 'not_close', list of missing requirements)."""
    bottle_strings = _bottle_match_strings(user_bottles)

    # Collected in ingredient sort order. Category slots can't be judged until
    # every one is known, since they compete for the same bottles, so they go in
    # as placeholders and get resolved together once the loop finishes.
    entries = []            # list of ('resolved', dict) | ('slot', slot_index)
    slots = []              # slot_index -> accepted type set
    slot_labels = []        # slot_index -> name to report when unfilled
    seen_bottle_reqs = set()
    seen_ingredient_reqs = set()

    for ing in recipe_data["ingredients"]:
        if ing["requirement_type"] == "optional":
            continue

        if ing["requirement_type"] == "bottle_type" and ing["bottle_type"]:
            req_type = ing["bottle_type"]

            if _use_name_match(ing):
                # Dedup by raw_name so two different liqueurs/specialty spirits
                # in the same recipe are tracked separately.
                key = ("name", (ing["raw_name"] or "").lower())
                if key in seen_bottle_reqs:
                    continue
                seen_bottle_reqs.add(key)

                if not _liqueur_satisfied(ing["raw_name"], ing["notes"], bottle_strings):
                    entries.append(("resolved", {
                        "type": "bottle_type",
                        "name": ing["raw_name"] or req_type,
                    }))
            else:
                # Fungible spirit — dedup by category, then hand to the
                # distinct-bottle assignment below.
                key = ("type", req_type)
                if key in seen_bottle_reqs:
                    continue
                seen_bottle_reqs.add(key)

                slots.append(FUNGIBLE_TYPES.get(req_type, {req_type}))
                slot_labels.append(req_type)
                entries.append(("slot", len(slots) - 1))

        elif ing["requirement_type"] == "ingredient" and ing["ingredient_name"]:
            req = ing["ingredient_name"]
            if req in seen_ingredient_reqs:
                continue
            seen_ingredient_reqs.add(req)
            if req.lower() not in stocked_ingredient_names:
                entries.append(("resolved", {"type": "ingredient", "name": req}))

    # Each category slot needs its own bottle. Without this a single bottle of
    # Scotch could fill both halves of a two-whiskey drink.
    unfilled = _assign_distinct_bottles(slots, user_bottles) if slots else set()

    missing = []
    for kind, payload in entries:
        if kind == "resolved":
            missing.append(payload)
        elif payload in unfilled:
            missing.append({"type": "bottle_type", "name": slot_labels[payload]})

    if not missing:
        return "makeable", []
    if len(missing) == 1:
        return "one_away", missing
    return "not_close", missing


def missing_ingredient_ids(recipe_data, user_bottles, stocked_ingredient_names):
    """For a single recipe, return the set of ingredient row IDs the user
    can't fulfill. Used by the recipe detail page to highlight missing items."""
    bottle_strings = _bottle_match_strings(user_bottles)
    missing = set()

    # Mirrors match_recipe: dedup category requirements, then check they can be
    # filled with a distinct bottle each. Kept in step deliberately, otherwise
    # the detail page highlights a different set of rows than the Make list used
    # when it decided the drink was makeable.
    slots = []
    slot_row_ids = []       # slot_index -> the ingredient rows that map to it
    seen_types = {}         # req_type -> slot index

    for ing in recipe_data["ingredients"]:
        if ing["requirement_type"] == "optional":
            continue
        if ing["requirement_type"] == "bottle_type" and ing["bottle_type"]:
            if _use_name_match(ing):
                if not _liqueur_satisfied(ing["raw_name"], ing["notes"], bottle_strings):
                    missing.add(ing["id"])
            else:
                req_type = ing["bottle_type"]
                if req_type in seen_types:
                    slot_row_ids[seen_types[req_type]].append(ing["id"])
                else:
                    seen_types[req_type] = len(slots)
                    slots.append(FUNGIBLE_TYPES.get(req_type, {req_type}))
                    slot_row_ids.append([ing["id"]])
        elif ing["requirement_type"] == "ingredient" and ing["ingredient_name"]:
            if ing["ingredient_name"].lower() not in stocked_ingredient_names:
                missing.add(ing["id"])

    if slots:
        for slot_idx in _assign_distinct_bottles(slots, user_bottles):
            missing.update(slot_row_ids[slot_idx])

    return missing


def get_one_away_grouped(user_id):
    """For the /one-away page: every recipe that's exactly one ingredient short,
    grouped by the missing item's name. Sorted by group size descending."""
    bottles = get_all_bottles(user_id)
    ingredients = get_all_ingredients(user_id)
    stocked = {i["name"].lower() for i in ingredients if i["in_stock"]}
    ids_by_name = {i["name"].lower(): i["id"] for i in ingredients}

    groups = {}  # missing.name (lowercased) -> {missing: dict, recipes: [recipe_data], ...}
    for r in get_all_recipes():
        status, missing = match_recipe(r, bottles, stocked)
        if status != "one_away":
            continue
        m = missing[0]
        # Case-insensitive key so 'Triple sec' and 'Triple Sec' merge into
        # one group instead of splitting (which also broke the ranking).
        key = m["name"].lower()
        if key not in groups:
            ing_id = ids_by_name.get(key) if m.get("type") == "ingredient" else None
            bottle_type, name_matched = (
                _bottle_requirement({"missing": m, "recipe": r})
                if m.get("type") == "bottle_type"
                else (None, False)
            )
            groups[key] = {
                "missing": dict(m),
                "recipes": [],
                "ingredient_id": ing_id,
                "bottle_type": bottle_type,
                "name_matched": name_matched,
            }
        elif groups[key]["missing"]["name"].islower() and not m["name"].islower():
            # Prefer the nicer-cased variant for display
            groups[key]["missing"]["name"] = m["name"]
        groups[key]["recipes"].append(r)

    # Sort: groups with more drinks first, then alphabetical
    sorted_groups = sorted(
        groups.values(),
        key=lambda g: (-len(g["recipes"]), g["missing"]["name"].lower()),
    )
    return sorted_groups


# Base-spirit classification for the "group by spirit" view on /recommend.
# Multiple raw types collapse into one display group: bourbon/scotch under
# "Whiskey", mezcal under "Tequila & Mezcal", cognac under "Brandy".
SPIRIT_GROUPS = {
    "gin": "Gin",
    "vodka": "Vodka",
    "rum": "Rum",
    "tequila": "Tequila & Mezcal",
    "mezcal": "Tequila & Mezcal",
    "whiskey": "Whiskey",
    "bourbon": "Whiskey",
    "scotch": "Whiskey",
    "rye": "Whiskey",
    "irish": "Whiskey",
    "brandy": "Brandy & Cognac",
    "cognac": "Brandy & Cognac",
    "vermouth": "Vermouth",
    "vermouth_sweet": "Vermouth",
    "vermouth_dry": "Vermouth",
}

# Display order for grouped /recommend page. Groups not listed go to the end
# alphabetically. "Other" always last.
SPIRIT_GROUP_ORDER = [
    "Gin", "Whiskey", "Rum", "Tequila & Mezcal",
    "Vodka", "Brandy & Cognac", "Vermouth",
]


def classify_base_spirit(recipe_data):
    """Return the display group name for a recipe's base spirit.
    Strategy: take the first non-optional bottle_type ingredient that's a
    fungible spirit. If the first bottle_type is a name-match liqueur (Campari,
    Cointreau, etc.), keep scanning -- they're rarely the 'base'. Falls back
    to 'Liqueur-led' if no fungible spirit is found, 'Other' if no bottle_type
    at all."""
    fallback = None
    for ing in recipe_data["ingredients"]:
        if ing["requirement_type"] != "bottle_type":
            continue
        bt = ing.get("bottle_type")
        if not bt:
            continue
        # Specialty spirits (cachaca, pisco, etc.) get their own bucket
        if _is_specialty(ing.get("raw_name")):
            return "Specialty"
        if _use_name_match(ing):
            # Liqueur-led drinks (Negroni-style) -- track but keep looking
            # for a fungible base spirit first.
            fallback = fallback or "Liqueur-led"
            continue
        # Fungible spirit found -- this is the base
        return SPIRIT_GROUPS.get(bt, bt.title())
    return fallback or "Other"


def get_recommendations_grouped(user_id, max_per_group=50):
    """Like get_recommendations but groups makeable drinks by base spirit.
    One-away list and ratings come along unchanged."""
    base = get_recommendations(user_id, max_makeable=200, max_one_away=25)
    groups = {}
    for r in base["makeable"]:
        spirit = classify_base_spirit(r)
        groups.setdefault(spirit, []).append(r)

    # Sort within each group preserving the rating-bucket order from the
    # base call (already sorted: liked > unrated > disliked).

    # Order groups: SPIRIT_GROUP_ORDER first, then anything else alphabetical,
    # with Other/Liqueur-led/Specialty at the end.
    end_buckets = {"Liqueur-led", "Specialty", "Other"}
    ordered = []
    for name in SPIRIT_GROUP_ORDER:
        if name in groups:
            ordered.append((name, groups.pop(name)[:max_per_group]))
    leftovers_end = []
    for name in sorted(groups.keys()):
        item = (name, groups[name][:max_per_group])
        if name in end_buckets:
            leftovers_end.append(item)
        else:
            ordered.append(item)
    ordered.extend(leftovers_end)

    base["groups"] = ordered
    return base


def _bottle_requirement(entry):
    """For a one-away entry blocked by a bottle, work out what kind of bottle.

    Returns (bottle_type, name_matched). Fungible blockers report their category
    slug as the name ("vermouth_dry"); name-matched ones report the row's
    raw_name ("Cointreau"), so the recipe's own rows are the only place the
    category ("liqueur") can be read back from.
    """
    name = (entry["missing"]["name"] or "").lower()
    for ing in entry["recipe"]["ingredients"]:
        if ing["requirement_type"] != "bottle_type" or not ing["bottle_type"]:
            continue
        if _use_name_match(ing) and (ing["raw_name"] or ing["bottle_type"]).lower() == name:
            return ing["bottle_type"], True
    return entry["missing"]["name"], False


def build_one_away_spotlight(one_away_entries, ingredients, ratings, min_drinks=2, day_seed=None):
    """The single ingredient that would unlock the most drinks, for Tonight.

    Every one-away recipe is blocked by exactly one thing, so grouping blockers
    by name and counting is exact: no drink is counted twice and the number on
    screen is a promise the app can keep.

    Replaced build_mixer_gap() on 2026-11-15. That summed the top three
    MIXERS into one line ("+3 mixers unlock 9 more drinks"), which hid that each
    was its own small opportunity and ignored bottles entirely, although 45 of
    Aaron's 70 one-away drinks were blocked by a bottle.

    Ranking: most drinks wins, but a mixer gets a one-drink head start, because
    a mixer is very often something the user already owns and never ticked (on
    2026-07-25 three unticked checkboxes were worth 14 drinks), while a bottle
    is a shopping trip. So a bottle takes the spotlight only when it unlocks at
    least two more drinks than the best mixer. Rotates daily across the top 4
    eligible blockers so Tonight doesn't pin the same bottle indefinitely.

    Mixer blockers that are not a real checklist row are skipped: the
    "I have this" button needs an ingredient id to tick.

    Returns None when the best group is below min_drinks, so the template can
    test for truthiness.
    """
    ids_by_name = {i["name"].lower(): i["id"] for i in ingredients}

    groups = {}
    for entry in one_away_entries:
        missing = entry["missing"]
        kind = "ingredient" if missing.get("type") == "ingredient" else "bottle"
        key = (kind, (missing["name"] or "").lower())
        if key not in groups:
            g = {"kind": kind, "name": missing["name"], "ingredient_id": None,
                 "bottle_type": None, "name_matched": False, "drinks": []}
            if kind == "ingredient":
                g["ingredient_id"] = ids_by_name.get(key[1])
                if g["ingredient_id"] is None:
                    continue
            else:
                g["bottle_type"], g["name_matched"] = _bottle_requirement(entry)
            groups[key] = g
        elif groups[key]["name"].islower() and not missing["name"].islower():
            groups[key]["name"] = missing["name"]
        groups[key]["drinks"].append(entry["recipe"]["recipe"])

    # Floor BEFORE ranking. Applied after, the mixer head start let a 1-drink
    # mixer outrank a 2-drink bottle and then fail the floor, which hid the
    # spotlight entirely from Shehan (0 makeable, Amaretto -> 2 drinks).
    eligible = [g for g in groups.values() if len(g["drinks"]) >= min_drinks]
    if not eligible:
        return None

    def rank(g):
        head_start = 1 if g["kind"] == "ingredient" else 0
        return (-(len(g["drinks"]) + head_start), g["kind"] != "ingredient", g["name"].lower())

    if day_seed is None:
        day_seed = date.today().toordinal()
    top_tier = sorted(eligible, key=rank)[:4]
    best = top_tier[day_seed % len(top_tier)]

    # The headline names one drink, so it should be the most tempting one:
    # liked first, never a disliked one if there's a choice, then the LOWEST
    # recipe id. The oldest rows are the original classics catalog, so for
    # bourbon that's Old Fashioned rather than alphabetical Gold Rush.
    bucket = {1: 0, 0: 1, -1: 2}
    headline = min(best["drinks"], key=lambda r: (bucket[ratings.get(r["id"], 0)], r["id"]))
    rest = sorted((r for r in best["drinks"] if r["id"] != headline["id"]),
                  key=lambda r: (bucket[ratings.get(r["id"], 0)], r["name"].lower()))
    best["drinks"] = [headline] + rest
    best["headline_drink"] = headline
    best["other_groups"] = len(groups) - 1
    return best


ALCOHOLIC_CHECKLIST = {"champagne", "prosecco", "red wine", "white wine"}
PRETICKED_STAPLES = {"sugar (white)", "salt"}

ONBOARD_BOTTLES = [
    {"key": "gin", "name": "Gin", "label": "Gin", "type": "gin"},
    {"key": "vodka", "name": "Vodka", "label": "Vodka", "type": "vodka"},
    {"key": "rum", "name": "Rum", "label": "Rum", "type": "rum"},
    {"key": "tequila", "name": "Tequila", "label": "Tequila", "type": "tequila"},
    {"key": "bourbon", "name": "Bourbon", "label": "Bourbon", "type": "bourbon"},
    {"key": "scotch", "name": "Scotch", "label": "Scotch", "type": "scotch"},
    {"key": "rye", "name": "Rye", "label": "Rye", "type": "rye"},
    {"key": "cognac", "name": "Cognac", "label": "Cognac", "type": "cognac"},
    {"key": "vermouth_sweet", "name": "Sweet Vermouth", "label": "Sweet vermouth", "type": "vermouth_sweet"},
    {"key": "vermouth_dry", "name": "Dry Vermouth", "label": "Dry vermouth", "type": "vermouth_dry"},
    {"key": "campari", "name": "Campari", "label": "Campari", "type": "liqueur"},
    {"key": "triple_sec", "name": "Triple Sec", "label": "Triple sec", "type": "liqueur"},
]

ONBOARD_MIXER_NAMES = [
    "Lemon juice (fresh)",
    "Lime juice (fresh)",
    "Simple syrup",
    "Sugar (white)",
    "Salt",
    "Soda water / club soda",
    "Tonic water",
    "Cola",
    "Ginger beer",
    "Angostura bitters",
    "Honey",
    "Orange juice",
]

SHORT_MIXER_LABELS = {
    "lemon juice (fresh)": "Lemon juice",
    "lime juice (fresh)": "Lime juice",
    "soda water / club soda": "Soda water",
    "sugar (white)": "Sugar",
    "angostura bitters": "Angostura",
    "tabasco / hot sauce": "Hot sauce",
    "worcestershire sauce": "Worcestershire",
}


def _short_mixer_label(name):
    return SHORT_MIXER_LABELS.get((name or "").lower(), name)


def build_kitchen_check(bottles, ingredients, recipes, max_items=10):
    """For a user with bottles logged but 0 ready drinks, select up to
    max_items unticked non-wine mixers (across 1/2/3+ away) that unlock the
    most cocktails for their exact bottle shelf via greedy set cover.

    Never names a key 'items' in the returned dict (Jinja dict.items() footgun).
    """
    stocked = {i["name"].lower() for i in ingredients if i["in_stock"]}
    by_lower = {i["name"].lower(): i for i in ingredients}

    mixer_only = []
    for rec in recipes:
        st, missing = match_recipe(rec, bottles, stocked)
        if st == "makeable" or not missing:
            continue
        if not all(m["type"] == "ingredient" for m in missing):
            continue
        ms = [m["name"] for m in missing]
        if any(x.lower() in ALCOHOLIC_CHECKLIST for x in ms):
            continue
        if not all(x.lower() in by_lower for x in ms):
            continue
        mixer_only.append((rec["recipe"]["id"], rec["recipe"]["name"], ms))

    if not mixer_only:
        return None

    chosen = set()
    chosen_order = []
    for _ in range(max_items):
        cands = {m for _, _, ms in mixer_only for m in ms if m not in chosen}
        if not cands:
            break
        best = None
        best_score = (-1, -1)
        for c in sorted(cands, key=str.lower):
            s = chosen | {c}
            full = sum(1 for _, _, ms in mixer_only if all(x in s for x in ms))
            prog = sum(1 for _, _, ms in mixer_only if c in ms and not all(x in chosen for x in ms))
            if (full, prog) > best_score:
                best_score = (full, prog)
                best = c
        if not best or best_score == (0, 0):
            break
        chosen.add(best)
        chosen_order.append(best)

    picks = []
    for name in chosen_order:
        ing = by_lower[name.lower()]
        picks.append({
            "id": ing["id"],
            "name": ing["name"],
            "label": _short_mixer_label(ing["name"]),
            "preticked": ing["name"].lower() in PRETICKED_STAPLES,
        })

    recipes_js = []
    for rec_id, rec_name, ms in mixer_only:
        if all(m in chosen for m in ms):
            recipes_js.append({
                "id": rec_id,
                "name": rec_name,
                "req_ids": [by_lower[m.lower()]["id"] for m in ms],
            })

    if not recipes_js:
        return None

    return {
        "picks": picks,
        "max_unlockable": len(recipes_js),
        "recipes": recipes_js,
    }


def build_onboarding_data(ingredients, recipes):
    """Build starter bottle + kitchen mixer options and a compact matching map
    for live client-side recipe unlock counting during empty-bar onboarding."""
    by_lower = {i["name"].lower(): i for i in ingredients}
    already_stocked = {i["name"].lower() for i in ingredients if i["in_stock"]}

    resolved_mixers = []
    onboard_mixer_names = set()
    for name in ONBOARD_MIXER_NAMES:
        ing = by_lower.get(name.lower())
        if not ing:
            continue
        onboard_mixer_names.add(ing["name"].lower())
        in_stock = bool(ing["in_stock"])
        resolved_mixers.append({
            "id": ing["id"],
            "name": ing["name"],
            "label": _short_mixer_label(ing["name"]),
            "in_stock": in_stock,
            "preticked": (not in_stock) and (ing["name"].lower() in PRETICKED_STAPLES),
        })

    starter_bottles = [
        {"id": idx + 1, "key": spec["key"], "name": spec["name"], "type": spec["type"], "brand": ""}
        for idx, spec in enumerate(ONBOARD_BOTTLES)
    ]

    compact_recipes = []
    for rec in recipes:
        req_mixer_ids = []
        seen_mixer_ids = set()
        mixer_ok = True
        for ing in rec["ingredients"]:
            if ing["requirement_type"] == "ingredient" and ing["ingredient_name"]:
                req_lower = ing["ingredient_name"].lower()
                if req_lower in already_stocked:
                    continue
                if req_lower in onboard_mixer_names and req_lower in by_lower:
                    iid = by_lower[req_lower]["id"]
                    if iid not in seen_mixer_ids:
                        seen_mixer_ids.add(iid)
                        req_mixer_ids.append(iid)
                else:
                    mixer_ok = False
                    break
        if not mixer_ok:
            continue

        seen_bottle_reqs = set()
        bottle_slot_keys = []
        slots_accepted = []
        bottle_ok = True
        for ing in rec["ingredients"]:
            if ing["requirement_type"] == "optional":
                continue
            if ing["requirement_type"] == "bottle_type" and ing["bottle_type"]:
                req_type = ing["bottle_type"]
                if _use_name_match(ing):
                    key = ("name", (ing["raw_name"] or "").lower())
                    if key in seen_bottle_reqs:
                        continue
                    seen_bottle_reqs.add(key)
                    matches = matching_user_bottles(ing, starter_bottles)
                    keys = [b["key"] for b in matches]
                    if not keys:
                        bottle_ok = False
                        break
                    bottle_slot_keys.append(keys)
                else:
                    key = ("type", req_type)
                    if key in seen_bottle_reqs:
                        continue
                    seen_bottle_reqs.add(key)
                    matches = matching_user_bottles(ing, starter_bottles)
                    keys = [b["key"] for b in matches]
                    if not keys:
                        bottle_ok = False
                        break
                    bottle_slot_keys.append(keys)
                    slots_accepted.append(FUNGIBLE_TYPES.get(req_type, {req_type}))

        if not bottle_ok:
            continue
        if slots_accepted and _assign_distinct_bottles(slots_accepted, starter_bottles):
            continue

        compact_recipes.append({"b": bottle_slot_keys, "m": req_mixer_ids})

    return {
        "bottles": ONBOARD_BOTTLES,
        "mixers": resolved_mixers,
        "recipes": compact_recipes,
    }


def get_recommendations(user_id, max_makeable=50, max_one_away=25):
    """Top-level: read the user's bar, score every recipe, return two lists.
    Makeable drinks are sorted: thumbs-up first, unrated next, thumbs-down last.
    Within each group, alphabetical by name."""
    bottles = get_all_bottles(user_id)
    ingredients = get_all_ingredients(user_id)
    ratings = get_all_ratings(user_id)
    all_recipes = get_all_recipes()

    stocked_ingredients = {
        i["name"].lower() for i in ingredients if i["in_stock"]
    }

    makeable = []
    one_away = []

    for r in all_recipes:
        status, missing = match_recipe(r, bottles, stocked_ingredients)
        if status == "makeable":
            makeable.append(r)
        elif status == "one_away":
            one_away.append({"recipe": r, "missing": missing[0]})

    # Pick the spotlight BEFORE one_away gets truncated for display, so the
    # count reflects every blocked drink rather than the first handful.
    spotlight = build_one_away_spotlight(one_away, ingredients, ratings)
    kitchen_check = (
        build_kitchen_check(bottles, ingredients, all_recipes)
        if len(makeable) == 0 and len(bottles) > 0
        else None
    )

    # Sort makeable by rating bucket: liked (1) -> unrated (0) -> disliked (-1).
    # bucket map keeps liked at top, disliked at bottom.
    bucket = {1: 0, 0: 1, -1: 2}
    makeable.sort(
        key=lambda r: (
            bucket[ratings.get(r["recipe"]["id"], 0)],
            r["recipe"]["name"].lower(),
        )
    )

    # Attach user-bottle hints so the recommend cards can show "Use your: X"
    # without having to re-run matching in the template layer.
    for r in makeable:
        r["your_bottles"] = used_user_bottles(r, bottles)

    return {
        "makeable": makeable[:max_makeable],
        "one_away": one_away[:max_one_away],
        "total_makeable": len(makeable),
        "total_one_away": len(one_away),
        "ratings": ratings,
        "spotlight": spotlight,
        "kitchen_check": kitchen_check,
        "bottles": bottles,
        "ingredients": ingredients,
    }
