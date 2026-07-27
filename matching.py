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

import unicodedata

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

# Words to strip when comparing requirement names against bottle names.
NOISE_WORDS = {"liqueur", "liquor", "(", ")", "the"}


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
        # Strip noise words to get the brand/spirit name on its own
        cleaned = s
        for w in NOISE_WORDS:
            cleaned = cleaned.replace(w, " ")
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

    groups = {}  # missing.name (lowercased) -> {missing: dict, recipes: [recipe_data]}
    for r in get_all_recipes():
        status, missing = match_recipe(r, bottles, stocked)
        if status != "one_away":
            continue
        m = missing[0]
        # Case-insensitive key so 'Triple sec' and 'Triple Sec' merge into
        # one group instead of splitting (which also broke the ranking).
        key = m["name"].lower()
        if key not in groups:
            groups[key] = {"missing": dict(m), "recipes": []}
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


def build_mixer_gap(one_away_entries, ingredients, max_items=3):
    """Which few CHECKLIST ingredients would unlock the most drinks?

    Every one-away recipe is blocked by exactly one thing, so grouping those
    blockers by name and counting is exact -- no drink can be counted twice,
    and the totals here are a promise the app can keep.

    Only ingredient blockers are considered. A missing bottle is a shopping
    trip; a missing mixer is very often something the user already owns and
    simply never ticked. That distinction is the whole point: on 2026-07-25 the
    catalog went from 125 to 171 recipes and the owner's makeable count moved
    12 -> 17, because he had 15 of 51 mixers ticked. The drinks were there. The
    checklist was the wall.

    Returns None when there is nothing useful to say, so the template can just
    test for truthiness.
    """
    ids_by_name = {i["name"].lower(): i["id"] for i in ingredients}

    groups = {}  # lowercased name -> {name, id, drinks: [recipe names]}
    for entry in one_away_entries:
        missing = entry["missing"]
        if missing.get("type") != "ingredient":
            continue
        key = missing["name"].lower()
        ing_id = ids_by_name.get(key)
        if ing_id is None:
            # Blocker isn't a real checklist row, so we can't offer to tick it.
            continue
        g = groups.setdefault(key, {"name": missing["name"], "id": ing_id, "drinks": []})
        g["drinks"].append(entry["recipe"]["recipe"]["name"])

    if not groups:
        return None

    ranked = sorted(groups.values(), key=lambda g: (-len(g["drinks"]), g["name"].lower()))
    top = ranked[:max_items]
    for g in top:
        g["drinks"].sort()

    return {
        # NOT "items": Jinja resolves `gap.items` to dict.items() before it
        # looks for a key of that name, so the template would silently iterate
        # a bound method and blow up at render time.
        "picks": top,
        "drink_count": sum(len(g["drinks"]) for g in top),
        "ingredient_count": len(top),
        # How much is still on the table below the cut, for the "and more" line.
        "remaining_ingredients": max(0, len(ranked) - len(top)),
        "remaining_drinks": sum(len(g["drinks"]) for g in ranked[len(top):]),
    }


def get_recommendations(user_id, max_makeable=50, max_one_away=25):
    """Top-level: read the user's bar, score every recipe, return two lists.
    Makeable drinks are sorted: thumbs-up first, unrated next, thumbs-down last.
    Within each group, alphabetical by name."""
    bottles = get_all_bottles(user_id)
    ingredients = get_all_ingredients(user_id)
    ratings = get_all_ratings(user_id)

    stocked_ingredients = {
        i["name"].lower() for i in ingredients if i["in_stock"]
    }

    makeable = []
    one_away = []

    for r in get_all_recipes():
        status, missing = match_recipe(r, bottles, stocked_ingredients)
        if status == "makeable":
            makeable.append(r)
        elif status == "one_away":
            one_away.append({"recipe": r, "missing": missing[0]})

    # Work out the mixer gap BEFORE one_away gets truncated for display, so
    # the count reflects every blocked drink rather than the first handful.
    mixer_gap = build_mixer_gap(one_away, ingredients)

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
        "mixer_gap": mixer_gap,
    }
