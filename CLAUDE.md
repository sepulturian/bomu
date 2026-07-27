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

Live and healthy. 171 recipes, 51 ingredients, 5 users, 35 bottles logged.

**Counts below were read off the live server on 2026-07-26** via
`matching.get_recommendations()`, not simulated. This closes old backlog #11.

| id | user | bottles | mixers ticked | makeable | one-away |
|---|---|---|---|---|---|
| 1 | aaron | 18 | 16 / 51 | 22 | 72 |
| 2 | Avishka | 0 | 0 | 0 | 0 |
| 3 | Rajapaksha | 0 | 0 | 0 | 0 |
| 4 | lenasheh (Shehan) | 16 | 4 | 0 | 14 |
| 5 | Maho | 1 | 12 | 1 | 13 |

Aaron moved 17 → 22 across the 2026-07-26 work. Shehan is still on **0 makeable
from 16 bottles**, which is the single worst number in this file and is backlog
#2. Two users still have nothing at all (backlog #1).

Landed 2026-07-26: commits `e4ead3b` and `9c034e0` (About + Worth knowing on
every recipe, plus the catalog audit that came out of writing it,
`check_specs.py` 37 flagged → 0), then `055a96c` and `2745190`.

### One thing IS half-finished

`sweep_namematch.py` is committed and deployed at `2745190`, **and the deployed
copy is wrong.** It reads the `ingredient_name` column where it must read
`raw_name`, which makes it report roughly 35 false BROKEN rows out of 87. The
corrected version is sitting uncommitted on the laptop. Next session:

```powershell
cd "C:\Users\sepulturian\Documents\Claude\projects\bomu"
del .git\index.lock
git add -A
git commit -m "sweep_namematch: read raw_name, not ingredient_name"
git push origin main
```

Do not trust any output from the server copy until that lands.

---

## Running it

Live: https://sepulturian.pythonanywhere.com
Server path: `/home/sepulturian/bomu`, deployed by `git pull` from GitHub.

### Deploy sequence

**Two machines. Say which one every time.** On 2026-07-25 a deploy block was
handed over without that label and got pasted into PowerShell on the laptop,
where `python3` doesn't exist, `&&` isn't a separator in Windows PowerShell 5.1,
and `~/bomu` is the wrong path anyway. Nothing broke, but nothing worked either.

**Laptop, PowerShell — commit and push only.** Never run migrations here: the
local `bomu.db` is the stale pre-multi-user copy (see Gotchas).

```powershell
cd "C:\Users\sepulturian\Documents\Claude\projects\bomu"
del .git\index.lock
git add -A                    # -A matters: picks up deleted files too
git commit -m "..."
git push origin main
```

**Server, PythonAnywhere Bash console — everything else.** In order; every step
exists because skipping it has caused a problem.

```bash
cd ~/bomu
python3 backup_db.py          # 1. ALWAYS back up before touching data
git pull origin main          # 2. bomu.db is gitignored, so this is data-safe
python3 <migration>.py        # 3. dry run first, read the output
python3 <migration>.py --commit
```

Then hit **Reload** on the PythonAnywhere Web tab. Database changes take effect
immediately because the app reads live, but Python code is held in memory by the
running worker and needs the reload. A migration can therefore look like it
worked while the UI changes in the same commit are still not being served.

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

**Render every template before deploying template changes.** `py_compile` passes
things that 500 on render — that's how `gap.items` nearly shipped.

`verify_routes.py` now exists and is committed (was backlog #6, written twice
and thrown away before). Run it:

```bash
python3 verify_routes.py                 # against bomu.db
python3 verify_routes.py --db copy.db     # against a migrated copy
```

It copies the database, brings the copy up to the multi-user schema, seeds one
user with a shelf chosen to exercise the fungible / sub-typed / name-matched
paths (an empty state renders fine and proves nothing), points
`database.DB_PATH` at the copy **before** importing `app`, then walks every
route logged out and logged in, including every recipe page and the POST paths.
It also asserts `safe_bottle_type()` still coerces junk to `other`.

**The `--db` form is the point when shipping a migration.** Run it once against
the current database to prove the templates render *without* the new columns,
so the code can deploy before the migration runs, then again against a migrated
copy to prove they render *with* them.

**Audit the catalog with `check_specs.py`.** Read-only, safe on the server, no
arguments. It finds internal inconsistencies: rows the instructions never
mention, measures that disagree between row and step, `ingredient` rows
pointing at checklist names that don't exist, `bottle_type` rows with no type,
name-matched rows that can never match. `--json` writes `spec_flags.json`
(gitignored). It should report 0 flags; anything else is either a real bug or a
gap in the checker, and both are worth ten minutes.

**Audit name matching with `sweep_namematch.py`** (added 2026-07-26). Read-only,
opens the database `mode=ro`, safe on the live server with no backup. It answers
one question `check_specs.py` does not: can this name-matched row ever be a
substring of a real bottle name?

```bash
python3 sweep_namematch.py            # ./bomu.db
python3 sweep_namematch.py --json     # also writes sweep_namematch.json (gitignored)
```

Three sections. **BROKEN** is certain and needs no judgement: every key carries
punctuation or a connective, so no bottle name can contain it. **REVIEW**
deliberately over-flags any key needing more than two words, because there is no
way to tell `White Creme de Cacao` (a real product) from `Blue Curacao orange
liqueur` (a product wearing a description) without knowing the products; expect
false positives there and read them. **IMPACT** is per user and is a *candidate*
count, not a count of drinks unlocked, since the recipe may be blocked by
something else too.

Live baseline on 2026-07-26: **87 name-matched rows, 1 BROKEN, 6 REVIEW**, and
all 6 REVIEW entries were confirmed false positives by hand.

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
| `ingredient` | matches the user's Mixers checklist by exact `ingredient_name`. Must already exist in `ingredients` (51 rows) or it can never be satisfied. |
| `optional` | garnishes, rinses, floats. Never blocks makeability. |

**`raw_name` and `ingredient_name` are two different columns and confusing them
is expensive.** Full column list: `id`, `recipe_id`, `raw_name`, `raw_measure`,
`requirement_type`, `bottle_type`, `ingredient_name`, `notes`, `sort_order`.

| column | holds | NULL when |
|---|---|---|
| `raw_name` | the product name, e.g. `Creme de Cassis`, `Pimm's No. 1` | rarely |
| `ingredient_name` | a key into the Mixers checklist | **always, on every `bottle_type` row** |

The matcher reads **`raw_name`** everywhere it does name matching:
`_liqueur_satisfied`, `match_recipe`, `missing_ingredient_ids` all use
`ing["raw_name"]`. `notes` is a second chance at a match, not the primary key.

On 2026-07-26 a new audit script read `ingredient_name` on bottle rows, got
NULL for all of them, and so judged every row on its descriptive `notes` string
alone. It reported **35 broken rows out of 84. The real number was 1 out of 87.**
Reading the wrong column here does not under-report, it invents a catastrophe,
and the invented version is convincing because the notes really are prose.
Check which column a script reads before believing what it says.

A `bottle_type` row with a NULL/empty `bottle_type` is **silently skipped** by
both `match_recipe` and `missing_ingredient_ids` — it can never block a drink.
Consistent between the two, so no drift, but it means a malformed import row
fails open rather than loudly. Validate in the import script, not here.

### recipes

- 171 rows
- Instructions carry a `[BOMU_REWRITTEN_v1]` marker, stripped by the
  `clean_instructions` filter
- 98 have no `image_url` and fall back to a plain card — 57% of the catalog,
  since none of the 46 added on 2026-07-25 had images.

**`about` and `tip` columns (added 2026-07-26).** Both nullable and both
rendered behind an `{% if %}`, so a recipe missing them degrades to exactly the
old page. `about` is 1-3 sentences of origin and flavour; `tip` is an optional
technique note shown under "Worth knowing". All 171 have an `about`, 125 have a
`tip`. Copy lives in `about_text.py`, keyed by recipe name.

**`instructions` is now numbered steps and nothing else.** This is the load-
bearing part. `instruction_steps()` in app.py splits on line breaks and does not
care whether a line is prose or a step, so the flavour line every recipe opened
with was rendering as **step 1** — "1. A Sour with a little more dignity." Same
at the bottom: 31 recipes added on 07-24 and 07-25 ended with a trailing note
that rendered as a final numbered step. Nobody reported it in three months.

Anything that writes `instructions` must therefore write steps only. Prose
belongs in `about` or `tip`. The rule is not enforced in code; `check_specs.py`
catches violations under SHAPE.

**Rules the copy in `about_text.py` follows**, and any addition should:

- Nothing invented. Documented origin where one exists, "contested" where
  sources disagree, and flavour-only where there is no real history. A
  plausible-sounding invented origin is worse than no origin.
- Tips are instructions, not trivia. A tip earns its place by changing what you
  do. 46 recipes have no tip because there was nothing worth saying.
- Steps name ingredients exactly as the `recipe_ingredients` rows do. A step
  saying "orange liqueur" above a list saying "Triple sec" reads as two
  different drinks on one page.

### ingredients

Checklist rows are **user-facing shopping instructions**, not internal keys. The
mixer-gap nudge names them out loud and tells people to go buy them, so a wrong
or ambiguous label is the app confidently sending someone to the wrong shelf.
That is why `Grape Soda` became `Grapefruit soda` on 2026-07-25.

A rename is four things, not one: the `ingredients` row, every
`recipe_ingredients` row pointing at it, the `user_stock` ticks, **and the photo
in `static/ingredients/`**. The photo is matched purely by slug
(`ingredient_slug(name)`), so renaming the row silently repoints the tile at a
file that doesn't exist — or worse, leaves a correct-looking tile showing the
wrong product. `grape_soda.jpg` really was a picture of purple grape soda.

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

Keys come from `_liqueur_keys(raw_name, notes)`, which returns **whole strings
only**: the folded source, plus one variant with `NOISE_WORDS` removed. It never
splits a string into candidate sub-names. So a source that reads like a sentence
is unsatisfiable, because no bottle is named `Elderflower Liqueur (St-Germain)`.
This is what `sweep_namematch.py` audits. Two known sharp edges:

- `NOISE_WORDS` is applied by plain `str.replace`, not word boundaries, so
  `"the"` is stripped from inside words: `Green Creme de Menthe` also yields the
  key `green creme de men`. Harmless today only because the unstripped key still
  matches. Word-boundary replacement would fix it (backlog #14).
- Brackets are in `NOISE_WORDS` but their *contents* are not, so
  `Cointreau (orange liqueur)` yields `cointreau orange`, splicing two words
  that were never adjacent. Neither key matches a bottle named `Cointreau`.

Name matching is **accent-insensitive** as of 2026-07-26. `_fold()` normalises
both sides. Before that, a row reading `Bénédictine` could never be satisfied by
a bottle the user had typed `Benedictine`, while Bobby Burns (row:
`Benedictine`) matched the same bottle fine. Same shelf, one drink visible and
one not, nothing on screen to explain it.

**Two traps to check whenever a name-matched row is added:**

1. *Accents.* Covered by `_fold()` now, but `check_specs.py` still flags them
   because an accented row is a smell even when it works.
2. *Brand names where a category belongs.* The Sazerac required a bottle
   literally named `Ricard` and the Zombie one named `Pernod`, while four other
   anise drinks wanted `Absinthe`. A user with a bottle labelled Absinthe could
   make four of the six. Requiring a brand is not a requirement, it is a typo
   with consequences. `check_specs.py` knows about the anise and cherry-liqueur
   families; add to `FAMILIES` there when a new one appears.

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

### The mixer gap (added 2026-07-25)

`build_mixer_gap()` answers "which few checklist ingredients would unlock the
most drinks?" It's computed inside `get_recommendations` from the *untruncated*
one-away list, before that list is sliced for display, so it costs no extra
matcher pass and the count reflects every blocked drink rather than the first
five.

Every one-away recipe is blocked by exactly one thing, so grouping blockers by
name and counting is exact — no drink is counted twice and the number on screen
is a promise the app can keep. Only `ingredient` blockers are considered; a
missing bottle is a shopping trip, a missing mixer is usually something the user
already owns and never ticked.

The returned dict uses the key **`picks`, not `items`**. Jinja resolves
`gap.items` to `dict.items()` before it looks for a key of that name, so the
template silently iterates a bound method and 500s at render. `py_compile`
does not catch this — only actually rendering the template does.

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
in all four bottle templates. Add new types there, not in the templates. (This
was written on 2026-07-24 as a statement of fact and was not true:
`add_bottle.html` still carried a hardcoded copy of the whole list until
2026-07-25. It happened to match. Assert the invariant, then go and check it.)

Anything user-facing that displays a raw type must go through the `type_label`
filter, or values like `vermouth_dry` leak into the UI. `my_bar.html` was still
printing the raw slug as its group headings a full day after the filter shipped —
adding a display filter is not done until every existing render site has been
grepped for and converted.

### Untrusted type values

`safe_bottle_type()` coerces anything not in `BOTTLE_TYPE_CHOICES` to `other`,
and every write path (`/add`, `/edit`, `/confirm-bulk`) runs through it. `other`
is name-matched, so it can never fungibly satisfy a category requirement — the
honest answer for "we don't know what this is".

This exists because `confirm_bulk.html` had no blank `<option>`. A bottle whose
label the scanner couldn't read arrived with `type=""`, matched nothing, and the
browser fell through to the first option in the list — **Gin** — which is
fungible, so the app then offered Martinis on it. Same failure as the Vodka
Cruiser, reached through a different door. Any new `<select>` of bottle types
needs a blank option AND server-side coercion; the template alone is not enough.

---

## Adding recipes

Written as standalone, reviewable, idempotent scripts (see
`import_whiskey_expansion.py` as the template). Requirements:

- Dry run by default, `--commit` to write
- Validate every row against the live `ingredients` table *before* writing
- Single transaction, roll back on error
- Match on name so re-running is a no-op
- Journal/WAL guard

Prefer reusing the existing ingredients over adding new ones, and treat every
new checklist row as a real cost: it starts **unticked for every existing user**,
so the recipes depending on it are invisible until people go back and update
their Mixers list. The 2026-07-25 batch added only 3 new ingredients for 46
recipes, each one justified in the script's docstring.

Also prefer recipes needing ONE fungible spirit. Drinks requiring two or three
name-matched liqueurs (Naked and Famous, Nuclear Daiquiri, Brandy Crusta,
Harvey Wallbanger) only inflate the one-away list, which is already 67 deep for
Aaron.

---

## Templates

Design system lives in one `<style>` block in `base.html`: warm editorial dark
palette (`--coral` #e9694a, `--gold` #d6a84e over charcoal-brown), Bodoni Moda
for display, Poppins for body. Page-specific styling is inline. That's fine at
this size, but anything reused across two templates belongs in `base.html` —
the login/signup password fields carried a hardcoded copy of the shared input
rule, complete with a stale border colour, until 2026-07-25.

**Never `|safe` a `join()` that contains user input.** `/recommend` had:

```jinja
{{ r.your_bottles | map('short_name') | join(' &middot; ') | safe }}
```

The `|safe` existed only to render the `&middot;` entity, but it marks the
*entire joined string* as trusted HTML — including bottle names the user typed.
Naming a bottle `<img src=x onerror=...>` executed it. Self-XSS only (bottles are
per-user and shown to nobody else), so the blast radius was small, but the fix is
free: use the literal `·` character and drop the filter. Grep for `|safe` before
adding another one; the two remaining uses are on `suggestions.py` output and
recipe names, both app-controlled.

**Duplicate checkboxes need syncing.** The checklist renders new ingredients
twice — once in "New since last visit", once in their category — with the same
`name` and `value`. Submitting worked by accident (either box ticked put one
value in the POST), but the two could sit on screen visibly disagreeing, and
unticking the lower one didn't undo the upper. Now kept in lockstep by JS.

**Safari draws its own `<summary>` marker** regardless of `list-style: none`.
Summaries with custom row layouts use the `.bare` class in `base.html`; ones
without it keep the triangle deliberately, since it's the only affordance saying
"this opens".

---

## Backlog

1. **Never-started users.** Two of five accounts (Avishka, Rajapaksha) have zero
   bottles and zero mixers. They signed up and did nothing. The mixer nudge
   cannot reach them — their problem is getting to a first bottle, not ticking a
   checklist. This is now the biggest untouched gap and it needs a different fix
   from #2: a reason to scan the first bottle, or a starter bar they can accept
   in one tap.
2. **Empty-state onboarding, partially addressed.** The mixer-gap nudge shipped
   2026-07-25 and helps, but unevenly: Aaron 3 ingredients → 14 drinks, Shehan
   3 → 3, because Shehan's blockers are mostly *bottles*. The original theory
   ("he just never filled in the checklist, he'd have 30+") was right for Aaron
   and only partly right for Shehan. Do not over-trust it again without checking
   whose blockers are mixers vs bottles.
3. **Tune the nudge.** It shows for any gap at all, including one tick for one
   drink. A floor (hide below ~3 drinks) would keep it feeling like a discovery
   rather than nagging. Left uncapped deliberately to observe real behaviour
   first.
4. **Fix local dev** so per-user work doesn't require the live server.
5. **Rum and gin sub-types.** Identical defect to the vermouth one already
   fixed: light vs aged vs Jamaican rum are not interchangeable, and sloe gin is
   a liqueur, not gin.
6. ~~**Commit a `verify_routes.py`.**~~ Done 2026-07-26. See Verification.
7. **Ambiguous bottle prompts.** A one-tap "sweet or dry?" nudge in My Bar would
   resolve legacy generic bottles over time.
8. **Audit the remaining checklist labels** the way `Grape Soda` was audited.
   That one was found by reading the Paloma's note, not by any systematic pass;
   there may be others that are ambiguous or plain wrong, and the nudge now
   reads every label out loud as a shopping instruction.
9. **Recipe images** (98 missing of 171 — the 46 added 2026-07-25 all lack
   images, so this is now 57% of the catalog).
10. **Grow the catalog** past 171. Lowest priority: 2026-07-25 proved catalog
    size is not what's limiting anyone.
11. ~~**Record the real server counts.**~~ Done 2026-07-26, table at the top of
    this file is now live data read via `matching.get_recommendations()`.
12. **Sub-types for rum and gin** is #5, but the same class of defect now has a
    second instance worth naming: `sherry` has no type at all. Adonis, Bamboo
    and Sherry Cobbler all sit on `other` and match by the word "sherry", which
    works but means fino, amontillado and cream sherry are interchangeable to
    the matcher. Adonis specifically says cream sherry will ruin it.
13. **The Sazerac base is a live judgement call.** Moved from bourbon to rye on
    2026-07-26 for correctness, which *removes* the drink from a bourbon-only
    shelf. `SAZERAC_BASE_TYPE` at the top of `fix_recipe_specs.py` reverts it in
    one line. Revisit if anyone complains.
14. **Push the corrected `sweep_namematch.py`.** The deployed copy at `2745190`
    reads the wrong column and reports ~35 false BROKEN rows. Fix is written and
    sitting uncommitted on the laptop. Do this before running it again. See
    "Where things stand".
15. **Hugo Spritz, `recipe_ingredients` row 398.** The one genuine BROKEN row on
    the live server. `raw_name` is `Elderflower Liqueur (St-Germain)`; the
    brackets make every key it generates unmatchable, so the drink can never
    appear for anybody. Verified against three plausible bottle names, all
    False. Set `raw_name` to `St-Germain` or `Elderflower Liqueur`. Zero users
    own an elderflower liqueur today, so this is correctness, not impact.
16. **Word-boundary `NOISE_WORDS` in `_liqueur_keys`.** `str.replace` strips
    `"the"` from inside `Menthe`. Latent, not currently biting. See The matcher.

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

### 2026-07-25 (first session)

Started as "add more cocktails", ended as a fairly hard lesson about what the
app's actual constraint is.

**Shipped, two commits:**

- `87dbe95` — 46 recipes via `import_catalog_expansion_2.py` (12 rum, 9 agave,
  10 vodka/gin, 7 brandy, 8 low-ABV), plus 3 new checklist ingredients
  (Passion Fruit Syrup, Clamato / Caesar mix, White Wine). Catalog 125 → 171,
  ingredients 48 → 51. No image URLs on any of them.
- `106fce7` — the mixer-gap nudge: `build_mixer_gap()` in `matching.py`,
  `add_ingredients_to_stock()` in `database.py`, `POST /stock-add`, and a
  banner at the top of `/recommend`. Reads "You're 3 ingredients from 14 more
  drinks", names the ingredients, expands to name the drinks, pre-ticked
  checkboxes so one tap adds the lot but you can untick what you don't own.
  `/stock-add` **adds only** — reusing `set_all_ingredients_stock` would have
  deleted every other tick the user had.

**Impact, and it is smaller than predicted.** Aaron 12 → 17 makeable,
49 → 67 one-away. 5 of the 46 new drinks were immediately makeable for him
(Canchánchara, Chet Baker, Milano-Torino, Ranch Water, Vermouth Cocktail).

**Three lessons worth keeping.**

*Simulating against an idealised bar overestimated by 5x.* The recipe selection
was validated in a sandbox that assumed all 48 mixers ticked, which predicted 27
immediately-makeable drinks. Aaron has 15 of 51 ticked, so the real answer was
5. Any future "will this help?" check must read actual `user_stock`, not a full
checklist.

*Catalog size is not the constraint and adding to it barely moves anything.*
125 → 171 recipes bought 5 drinks. Ticking three checkboxes would buy 14. The
recipes are worth having, but "grow the catalog" is now the lowest-value item on
the backlog and should stay there.

*Two of five users have never added anything at all.* That reframes the whole
onboarding problem: it isn't one failure, it's two. Unticked mixers (Aaron,
Shehan) and never-started accounts (Avishka, Rajapaksha) need different fixes,
and the nudge only addresses the first. Maho is a third shape again — 12 mixers
ticked, 1 bottle — which is the exact opposite of the assumed behaviour that
scanning is fun and the checklist is a chore.

**One near-miss.** `gap.items` in the template resolved to `dict.items()` rather
than the dict key, which would have 500'd `/recommend` for every user. `python3
-m py_compile` passed it clean; only rendering the template caught it. Key
renamed to `picks`. Render the template before deploying template changes.

### 2026-07-25 (second session)

Three asks: the Grape Soda rename off the backlog, a general bug/UI sweep, and
some photography. The sweep was the valuable part.

**Shipped, one commit.** `migrate_grapefruit_soda.py` plus fixes across `app.py`
and nine templates, and three new images.

**The rename.** `Grape Soda` → `Grapefruit soda`, ticks cleared rather than
carried forward (a preserved tick would claim the user can make a Paloma with
purple grape soda), Paloma row repointed, note rewritten. The backlog item
described this as a rename plus a recipe-row fix and was incomplete: the tile
photo `grape_soda.jpg` was an actual picture of purple grape soda, so renaming
the row alone would have left a wrong image under a right name — worse than
before. New photo generated, old file deleted.

**Four real bugs, none of which anyone had reported.**

*Stored XSS on `/recommend`.* `|safe` on a `join()` of user-typed bottle names.
Self-XSS only, but free to fix. See Templates.

*The bulk scanner silently added unidentified bottles as Gin.* No blank
`<option>` in `confirm_bulk.html`, so `type=""` fell through to the first entry
in the list, which is fungible. Fixed in the template and again server-side with
`safe_bottle_type()`. See Scanner.

*Raw type slugs still leaking into My Bar*, a full day after the `type_label`
filter shipped specifically to stop that.

*Two live checkboxes per new checklist ingredient*, unsynced.

Plus: `add_bottle.html` had a hardcoded dropdown contradicting this file's own
"single source of truth" claim; search in group-by-spirit left orphaned headings;
Safari was drawing its own `<summary>` triangle over the one-away rows.

**Impact: 17 makeable / 67 one-away, unchanged.** That was the goal. Every fix
was a correctness or presentation fix, so movement in those numbers would have
meant something broke.

**Three lessons worth keeping.**

*This file's assertions decay into fiction if nobody checks them.* Two claims
written on 2026-07-24 — "BOTTLE_TYPE_CHOICES is the single source of truth for
all four bottle templates" and "anything user-facing goes through `type_label`" —
were both false within a day, and one of them was false when written. They read
as descriptions but they're aspirations. Grep before trusting a line in here.

*The same class of bug keeps arriving through a new door.* The Vodka Cruiser
(RTD tagged as a fungible spirit) was fixed at the scanner prompt. It came back
through an HTML `<select>` default. Fixing the source that produced a bad value
doesn't fix the shape of the hole it went through; guard where the value is
consumed, not only where it's produced.

*A checklist label is a shopping instruction now.* Once `build_mixer_gap()`
started naming ingredients in a banner that says "go get these", every label
became load-bearing copy. `Grape Soda` was tolerable as a checklist row and
indefensible as an instruction. Backlog #8 is the systematic version of the
one-off audit that caught it.

**One process note.** The deploy block was handed over without saying which
machine it ran on and got pasted into PowerShell on the laptop instead of the
server's Bash console. No damage — Windows has no `python3` and PowerShell 5.1
has no `&&`, so it simply refused. The Deploy section now splits the two
explicitly.

### 2026-07-26

Asked for an "About this drink" section on the recipe page, plus a sanity check
across all 171 recipes and a technique tip where there was one to give. The
About section was the ask. The audit was where the value was.

**Shipped, two commits.**

- `e4ead3b` — `about` and `tip` columns, `about_text.py` (171 abouts, 125
  tips), `migrate_recipe_about.py`, `fix_namematch_requirements.py`, accent
  folding in `matching.py`, the recipe.html blocks, plus `check_specs.py` and
  `verify_routes.py` as new permanent tools.
- `9c034e0` — `fix_recipe_specs.py`: the Sazerac base spirit and the orphaned
  bitters rows, plus two fixes to `check_specs.py` itself.

**The request was a bug report and nobody knew it.** The example given was the
Bee's Knees, whose page opens "1. A Sour with a little more dignity." That line
is the first line of `instructions`, and `instruction_steps()` splits on line
breaks without caring whether a line is prose. So every recipe in the catalog
has been numbering its blurb as step 1, and 31 of the newer ones have been
numbering a trailing note as the last step. Three months, five users, zero
reports. The fix for the missing context and the fix for the phantom steps are
the same change: get the prose out of `instructions`.

**Five silent name-matching bugs**, none reported, all invisible by
construction — the drink just never appears. Two accent traps (`Bénédictine`,
`Crème de Cassis`, `Orange Curaçao`) and two brand-name-as-category splits
(`Ricard` and `Pernod` against four recipes' `Absinthe`; `Cherry brandy`
against `Cherry Heering`). Fixed in the data *and* in `_fold()`, because fixing
only the rows leaves the hole open.

**The Sazerac was specced with bourbon.** Canon is rye or cognac, the IBA spec
is cognac, bourbon is a substitution. Tolerable until the About copy went in
saying the drink is named for a cognac brand "before rye took over", at which
point the page asserted one thing in prose and required another in the list.
Moved to `rye`. This *removes* the drink from a bourbon-only shelf, which is a
real cost and a judgement call, not an obvious fix — one-line revert documented
in the script and in backlog #13.

**Twelve orphaned bitters rows**, added by an old audit that never touched the
instructions, so the ingredient list showed a dash of Angostura the method
never mentioned. Not uniformly right, so not uniformly removed: six kept and
named in the method (a Rob Roy without Angostura is not a Rob Roy; the Pisco
Sour's dash goes on the foam, a technique the method was silently omitting) and
seven removed as plausible-sounding but not part of the drink.

**Impact.** `check_specs.py` 37 flagged recipes → 0. Counts measured on
synthetic shelves against the local stale database: the about migration moved
nothing (62/31 → 62/31, which was the design and the whole verification), the
name-matching fixes gained 3, and the Sazerac change cost 1 on a bourbon-only
shelf and 0 otherwise. **Real per-user numbers were never taken on the server.
That is backlog #11 and the table at the top of this file is stale until it is
done.**

**Four lessons worth keeping.**

*A cosmetic request was the only reason the step-1 bug got found.* Same shape as
2026-07-24, where wiring up a label filter surfaced three real bugs. Twice now
the small presentation task has been worth more than it looked. Take them.

*Splitting migrations by expected effect is what made them verifiable.*
`migrate_recipe_about.py` must not move the counts and
`fix_namematch_requirements.py` must, so each one's number means something on
its own. Bundled together, neither would have been checkable. Both were also
tested for order-independence and idempotency by running all three in both
orders twice and diffing the resulting databases byte for byte.

*The audit tool missed a bug and that was the most useful thing it did.* Mezcal
Negroni's orphaned `Orange bitters` row read as covered because the method said
"express the orange peel" — a garnish vouching for an unrelated ingredient. It
was found by hand. A checker that quietly passes bad data is worse than no
checker, so bitters rows now need the word "bitters" or the brand. Two
false-positive rules were also loosened, because a tool that cries wolf gets
ignored and then it may as well not exist.

*Every "no history" answer had to be allowed.* 46 of 171 recipes have no tip and
a number have no origin story, because inventing a plausible one is the exact
failure this app already has a history of: the Grape Soda label and the Vodka
Cruiser were both the app being confidently wrong. Contested attributions are
written as contested.

### 2026-07-26 (second session)

Started as a one-line question — "are peach schnapps and triple sec in the
Mixers checklist?" — and turned into a false alarm that took most of the
session, plus the real server counts that had been outstanding since the
morning.

**The answer to the question.** No, and they never should be. Liqueurs are
`bottle_type` requirements matched by name against My Bar. The Mixers checklist
is non-alcoholic (juices, sodas, syrups, bitters, garnishes, pantry) with four
deliberate exceptions: Champagne, Prosecco, Red Wine, White Wine. A checklist
tick would make Campari and Cointreau interchangeable, which is the whole thing
`NAME_MATCH_TYPES` exists to prevent.

**Shipped, one commit.** `2745190`, `sweep_namematch.py`. **It is wrong as
deployed** — see backlog #14 — and the correction is uncommitted on the laptop.

**The false alarm, which is the thing worth remembering.** Investigating the
question, an ad-hoc query read `notes` on the liqueur rows, saw prose like
`Campari specifically` and `Cointreau (orange liqueur)`, and concluded the
matcher could never satisfy them. That was reported confidently, with a table,
across two messages. A sweep script was then built around the same assumption
and it read `ingredient_name` — NULL on every bottle row — so it agreed. **35
BROKEN out of 84.** The number was fabricated by reading the wrong column, and
it was convincing precisely because the notes really are prose.

Reading `raw_name`, which is what `matching.py` actually uses, the same live
database gives **1 BROKEN out of 87**, and the 6 REVIEW rows are all false
positives confirmed by hand. The catalog was fine the whole time. The single
real bug is Hugo Spritz, backlog #15, which affects nobody because no user owns
an elderflower liqueur.

**Real server counts, closing backlog #11.** Read via
`matching.get_recommendations()`, table at the top of this file updated. Aaron
17 → 22 makeable across the 2026-07-26 work. Shehan still 0 from 16 bottles.

**Four lessons worth keeping.**

*The wrong column does not under-report, it invents a catastrophe.* An audit
tool reading a NULL column does not go quiet, it flags everything, and every
flag comes with real-looking evidence attached. `check_specs.py` was written
carefully against the right fields; this one was written in an afternoon against
a field name that looked right. Before believing any audit output, check which
column the query selects against what the consuming code reads.

*Verify against the consumer, not against the data.* The whole error chain would
have been cut at minute one by opening `matching.py` and grepping for what
`_liqueur_satisfied` is passed. That grep was finally run only after the numbers
stopped making sense. CLAUDE.md already said "verify through the matcher, not
the browser" after the 2026-07-24 cached-Boulevardier hour; the same rule
applies to verifying through the matcher rather than through the schema.

*Confidence scaled with the size of the wrong number.* 35 broken rows out of 84
should have read as implausible on its face, because five users have been using
this app for three months and Aaron has 22 makeable drinks. A defect rate that
high is not consistent with the app working. Treat a shocking audit result as
evidence about the audit first.

*The stale local database is now actively dangerous, not just useless.* Every
wrong step this session came from developing against a 100-recipe pre-multi-user
copy where `ingredient_name` being NULL looked normal. Backlog #4 has been
sitting at "highest-value chore outstanding" since 2026-07-24. It just cost a
session.
