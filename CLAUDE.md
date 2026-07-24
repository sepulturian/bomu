# Bomu

A web app for finding cocktails you can actually make from the bottles you own.
Flask + SQLite, hosted on PythonAnywhere. Built for Aaron and his friends.

> **Note:** this file was rewritten from scratch on 2026-07-24. The previous
> CLAUDE.md went missing (untracked, never committed, so unrecoverable). Anything
> it recorded before this date — earlier session log entries, older decisions — is
> lost. **Commit this file.** It is the durable substitute for chat history and it
> is only safe once git is tracking it.

---

## Where things stand

Live and healthy as of 2026-07-24. 125 recipes, 5 users, 35 bottles logged.

Aaron (user 1): 18 bottles, 12 makeable, 49 one-away.
Shehan (user 4): 16 bottles, **0 makeable** — he has only ticked 4 mixers. This is
the clearest evidence yet that onboarding, not catalog size, is the real problem.

Just landed: 25 new whiskey and split-base recipes, whiskey/vermouth sub-types,
distinct-bottle matching, and an RTD tagging fix. All three commits deployed and
verified server-side.

Nothing is half-finished. Next session can start clean on the backlog below.

---

## Running it

Live: https://sepulturian.pythonanywhere.com
Server path: `/home/sepulturian/bomu`, deployed by `git pull` from GitHub.

### Deploy sequence

Do these in order. Every step exists because skipping it has caused a problem.

```bash
cd ~/bomu
python3 backup_db.py          # 1. ALWAYS back up before touching data
git pull origin main          # 2. bomu.db is gitignored, so this is data-safe
python3 <migration>.py        # 3. dry run first, read the output
python3 <migration>.py --commit
```

Then hit **Reload** on the PythonAnywhere Web tab. Database changes take effect
immediately because the app reads live, but Python code is held in memory by the
running worker and needs the reload.

### Verification

**Check the matcher server-side, not through the browser.** Chrome caches
`/recommend` and `/one-away` aggressively. On 2026-07-24 a stale render showed a
bottle that does not exist in the database and sent an hour into chasing a bug
that was never real. Authoritative check:

```bash
python3 -c "
import matching
r = matching.get_recommendations(1)
print(r['total_makeable'], r['total_one_away'])
print(sorted(x['recipe']['name'] for x in r['makeable']))"
```

If you must check in a browser, append a cache-busting query string.

---

## Gotchas

**The local `bomu.db` is stale and pre-multi-user.** It has no `user_id` column
on `bottles` and zero rows in `users`, so anything per-user fails against it. It
is only useful for reading recipe/ingredient conventions. Real per-user work has
to happen on the server. Fixing local dev (run `migrate_multiuser.py`, or write
a `seed_dev_db.py`) is the highest-value chore outstanding.

**SQLite side files can eat committed data.** On 2026-07-23 a `.db-journal`
rolled the live database back. Both `.gitignore` and every migration script now
refuse to proceed if `bomu.db-journal`, `-wal` or `-shm` is present. Keep that
guard in any new script.

**`.git` is not writable from the Cowork sandbox.** Agent tooling can stage files
but cannot create commits (it can't remove `.git/index.lock`). Commits and pushes
have to be run by hand in PowerShell:

```powershell
cd "C:\Users\sepulturian\Documents\Claude\projects\bomu"
del .git\index.lock
git commit -m "..."
git push origin main
```

---

## Data model

`users`, `bottles`, `ingredients`, `user_stock`, `recipes`, `recipe_ingredients`,
`ratings`, `scan_log`.

Users as of 2026-07-24: 1 aaron, 2 Avishka, 3 Rajapaksha, 4 lenasheh (Shehan,
Aaron's brother), 5 Maho.

### recipe_ingredients

The important table. `requirement_type` is one of:

| value | meaning |
|---|---|
| `bottle_type` | needs a bottle. See matching rules below. |
| `ingredient` | matches the user's Mixers checklist by exact `ingredient_name`. Must already exist in `ingredients` (48 rows) or it can never be satisfied. |
| `optional` | garnishes, rinses, floats. Never blocks makeability. |

### recipes

- 125 rows: 100 `source='thecocktaildb'`, 25 `source='manual_verified'`
- Instructions carry a `[BOMU_REWRITTEN_v1]` marker, stripped by the
  `clean_instructions` filter
- 52 have no `image_url` and fall back to a plain card. Deprioritised, but it is
  now 40% of the catalog.

---

## The matcher (`matching.py`)

Two strategies, chosen per ingredient:

**Fungible spirits** match by category via `FUNGIBLE_TYPES`. Generic parents
accept their sub-types, so `whiskey` accepts bourbon/scotch/rye/irish.

**Name-matched** types (`liqueur`, `amaro`, `other`, plus specialty keywords like
cachaca and pisco) match by substring against the bottle's name. This means
`notes` on those rows **must** contain a distinctive keyword of 4+ characters, or
the requirement is permanently unsatisfiable. Campari must not match Cointreau
just because both are liqueurs.

### Sub-types (added 2026-07-24)

`rye`, `irish`, `vermouth_sweet`, `vermouth_dry`.

Legacy bottles still on a generic type stay **permissive**: `rye` accepts
`{rye, whiskey}` and `vermouth_sweet` accepts `{vermouth_sweet, vermouth}`. The
reasoning is that we don't know an unlabelled whiskey *isn't* rye, and a false
negative (hiding a drink someone can make) is worse than mild permissiveness.
`bourbon` and `scotch` stay strict because the scanner has always identified
those reliably.

### Distinct-bottle assignment

Each deduplicated category slot must be fillable by a *different* bottle, solved
with bipartite matching in `_assign_distinct_bottles`. Without it one bottle of
Laphroaig satisfied both halves of Cameron's Kick, whose entire point is two
different whiskeys.

Identical requirements are deduplicated *before* this runs, deliberately.
Penicillin lists blended Scotch plus an Islay float; both are `scotch`, they
collapse to one slot, and one bottle is a fine way to make it.

**`match_recipe` and `missing_ingredient_ids` duplicate this logic and must be
kept in step**, or the detail page highlights different rows than the Make list
used to decide the drink was makeable.

---

## Scanner

Claude vision, `claude-sonnet-4-6`, prompts inline in `app.py`
(`scan_bottle_image`, `scan_shelf_image`). Both prompts must be edited together.

They now explicitly cover:

- **Ready-to-drink products.** A Vodka Cruiser was tagged `vodka` and, because
  vodka is fungible, was telling a user he could make a Martini out of an
  alcopop. RTDs, seltzers, beer, wine and prosecco all go to `other`.
- **Whiskey and vermouth sub-types**, with "don't guess, generic is the safe
  answer" stated explicitly.

`BOTTLE_TYPE_CHOICES` in `app.py` is the single source of truth for the dropdowns
in all four bottle templates. Add new types there, not in the templates.

Anything user-facing that displays a raw type must go through the `type_label`
filter, or values like `vermouth_dry` leak into the UI.

---

## Adding recipes

Written as standalone, reviewable, idempotent scripts (see
`import_whiskey_expansion.py` as the template). Requirements:

- Dry run by default, `--commit` to write
- Validate every row against the live `ingredients` table *before* writing
- Single transaction, roll back on error
- Match on name so re-running is a no-op
- Journal/WAL guard

Prefer reusing the existing 48 ingredients over adding new ones. All 25 recipes
added on 2026-07-24 resolve against them, so nobody had to re-tick anything.

---

## Backlog

1. **Empty-state onboarding.** The single biggest real problem. Shehan logged 16
   bottles and saw *zero* drinks, purely because he never filled in the Mixers
   checklist (he had 4 items ticked: coffee, red wine, vanilla extract, water).
   With mixers ticked he'd have 30+. Scanning bottles is fun, the checklist is a
   chore, and nothing in the app pushes you toward it.
2. **Fix local dev** so per-user work doesn't require the live server.
3. **Rum and gin sub-types.** Identical defect to the vermouth one just fixed:
   light vs aged vs Jamaican rum are not interchangeable, and sloe gin is a
   liqueur, not gin.
4. **Ambiguous bottle prompts.** A one-tap "sweet or dry?" nudge in My Bar would
   resolve legacy generic bottles over time.
5. **Recipe images** (52 missing).
6. **Grow the catalog** past 125.

---

## Session log

Entries before 2026-07-24 were lost with the original file.

### 2026-07-23
Database corruption from a stray SQLite journal file. Source of the side-file
guards now baked into every migration script.

### 2026-07-24

Started from Shehan's feedback that the app suggested him nothing despite a
six-bottle scotch shelf, and that he expected some kitchen-sink drink blending
everything he owned.

**Diagnosis.** He had 0 makeable, 12 one-away. Not a matcher bug and not a catalog
gap: he had ticked 4 mixers (coffee, red wine, vanilla extract, water). With
mixers ticked he'd have had 30+. Long Island Iced Tea *was* already in the
catalog; he lacks tequila. No classic cocktail blends scotch, vodka, gin and
cognac, and none should — scotch is too assertive to disappear into a mixed base.

**Shipped, three commits:**

- `f1090f6` — 25 recipes (6 scotch, 13 rye/bourbon, 6 split-base), each spec
  verified against Difford's, IBA, Imbibe or PUNCH with the source URL recorded
  per recipe. Also retagged a Vodka Cruiser from `vodka` to `other`.
- `f88022a` — `rye`/`irish`/`vermouth_sweet`/`vermouth_dry` sub-types, plus
  distinct-bottle bipartite matching. 3 bottles and 36 recipe rows migrated.
- `ae782a1` — `type_label` filter so raw slugs stop leaking to the UI, and fixes
  for brand suggestions that the new sub-types had silently broken.

**Impact.** Aaron 14 → 12 makeable, nothing gained. All losses were genuine false
positives: he owns three *sweet* vermouths and no dry one, so Affinity, Dry Rob
Roy and **Vodka Martini** had been offered on a bottle he doesn't own. The Vodka
Martini case predated all of today's work.

**Two lessons worth keeping.** Wiring up the label filter surfaced three further
bugs that would otherwise have shipped (dead brand suggestions for the new types,
`irish` falling through to `irish cream` and recommending Baileys, and two junk
buckets in the group-by-spirit view) — the small cosmetic task was worth more than
it looked. And an hour went into chasing a Boulevardier bug that did not exist,
because Chrome served a cached `/recommend` showing a bottle absent from the
database. Verify through the matcher, not the browser.
