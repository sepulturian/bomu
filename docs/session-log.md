# Bomu session log

Every dated session entry, oldest first. Moved out of `CLAUDE.md` word for word
on 2026-11-21 so agent sessions stop loading the whole history at startup;
nothing was reworded or dropped. `CLAUDE.md` is the current state and keeps
copies of the newest 2 entries under `## Recent sessions`.

- **Adding an entry:** at session close, append a dated `### YYYY-MM-DD` entry at
  the **bottom** of this file, then refresh `## Recent sessions` in `CLAUDE.md`
  (its `## Session handoff protocol` has the steps).
- **Section references:** entries and code comments that say "see Templates",
  "under The matcher", "CLAUDE.md, Gotchas" and so on mean sections of
  `CLAUDE.md`, which keep those names. "CLAUDE.md, 2026-07-25" means the dated
  entry here.
- **Layout:** first an archive of the text that sat in `CLAUDE.md`'s
  current-state sections until 2026-11-21 and was moved out or reworded then;
  after it, `## Session log` with every dated entry. Two blocks that sat under
  `## Where things stand` are filed by date in the log, each marked where it is.

---

## Archive: moved out of CLAUDE.md's current-state sections (2026-11-21)

These paragraphs were history or narrative inside `CLAUDE.md`'s current-state
sections, or wording that was replaced when those sections were rewritten on
2026-11-21. They are kept word for word, grouped by the section they sat in.
Anything in them that is still true was rewritten into `CLAUDE.md` in the
present tense, so read `CLAUDE.md`, not this archive, for the current state.

### From the top of `CLAUDE.md`

> **Note:** this file was rewritten from scratch on 2026-07-24. The previous
> CLAUDE.md went missing (untracked, never committed, so unrecoverable). Anything
> it recorded before this date — earlier session log entries, older decisions — is
> lost. **Commit this file.** It is the durable substitute for chat history and it
> is only safe once git is tracking it.

### From `## Session handoff protocol (Claude Code & Antigravity)`

This file is the shared memory between **Claude Code** (which auto-loads `CLAUDE.md`)
and **Antigravity** (which auto-loads `AGENTS.md` -> `CLAUDE.md`). Neither agent can
see the other's chat history, so anything not written here is lost.

- **At session start:** Read `## Where things stand`, `## Running it`, and the
  newest `### YYYY-MM-DD` entries at the bottom of `CLAUDE.md` before running
  commands or editing code.
- **At session close ("close sesh" or wrap-up):** Always append a dated
  `### YYYY-MM-DD` entry at the bottom of `CLAUDE.md` (and update
  `## Where things stand` / `## Running it` if hosting, schema, or counts changed).
  Cover what changed, why, gotchas hit, and open items / next steps.
- **Never write secret values** (passwords, API keys, full `DATABASE_URL`). Names only.
- **Commit and push `CLAUDE.md`** together with the session's work.

### From `## Where things stand`

Live and healthy. 171 recipes, 49 ingredients, 5 users, 34 bottles logged.
Open signup is enabled (`INVITE_CODE` removed; guarded by an offscreen honeypot,
sliding-window auth rate limiting, and a shared `SCAN_GLOBAL_DAILY_LIMIT = 60`
cap alongside the `15`/user/day cap). Public read-only browsing is enabled on
`/explore` and `/recipe/<id>`.
Catalog & DB hygiene are clean: `check_specs.py` reports 0 flags across 171
recipes, `sweep_namematch.py` reports 0 BROKEN rows, and Neon `recipe_enhancements`
matches the SQLite constraint/index schema.

Aaron went 22 → 34 between 2026-07-26 and 2026-11-15 by ticking 3 more mixers on
the live site, 34 → 35 on 2026-11-20 when `Moscow Mule` moved from `Ginger ale`
to `Ginger beer`, and adjusted his live bar to 17 bottles / 19 mixers (`25 / 77`)
by 2026-11-21. Avishka, Rajapaksha, and Shehan still have 0 makeable in the DB
until they next open Tonight, where 2-step empty-bar onboarding (`POST /quick-setup`)
and the 0-ready Quick Kitchen Check card now guide them directly to their first pour.

**Live has diverged from the local snapshot.** `bomu_live.db` holds the frozen
2026-11-15 snapshot (Aaron at 16 mixers, 22 / 72; 51 ingredients); `bomu.db`
matches live Neon's catalog tables (`171` recipes, `49` ingredients) after the
2026-11-19 and 2026-11-20 migrations, while per-user tables (`user_stock`,
`bottles`, `ratings`) on Neon drift as people use the app. Read user counts from
Neon, never from the snapshot.

### From `## Where things stand` › `### Untracked local working directories`

On 2026-11-21, all `44` unused legacy static files (`static/ingredients/*`,
`static/*.jpg`, `static/beach-bar-diorama.webp`, `static/beach-bar-sunset.webp`)
were removed from git tracking (`static/` dropped from `7.90 MB` to `2.27 MB`).
Only untracked `.claude/` and `redesign/` working directories remain in the local
tree; keep them unstaged and don't sweep blindly with `git add -A`.

### From `## Running it`

- **Live:** https://www.bomu.lol (`https://bomu.lol` 308-redirects to `www.bomu.lol`; Vercel preview/alias: `https://bomu.vercel.app`)
- **Hosting & Auto-Deploy:** Vercel project `sepulturian/bomu` (Flask preset, `vercel.json` -> `app.py`). Every push to `main` on `https://github.com/sepulturian/bomu.git` builds and deploys to production automatically.
- **Database:** **Neon Postgres** project `broad-water-80207736` in production (`DATABASE_URL`), with automatic local SQLite fallback when `DATABASE_URL` is unset (or `FORCE_SQLITE=1`).
- **Local Dev Data & Env:**
  - `.env` (gitignored) holds `DATABASE_URL`, `DATABASE_URL_UNPOOLED`, and `ANTHROPIC_API_KEY` pointing to the active Neon Postgres database (verify with `matching.get_recommendations(1)`). Unset `DATABASE_URL` (or pass `FORCE_SQLITE=1`) to run against local SQLite.
  - `bomu_live.db` (gitignored) is the untouched 171-recipe, 51-ingredient multi-user SQLite snapshot downloaded from PythonAnywhere on 2026-11-15 (`venv\Scripts\python.exe verify_routes.py --db bomu_live.db`).
  - `bomu.db` was seeded from `bomu_live.db` on 2026-11-15 and has since received the 2026-11-19 and 2026-11-20 catalog migrations (matching live Neon's catalog tables, behind Neon on per-user tables).
  - **`load_dotenv()` finds `.env` relative to the calling script, not the cwd.** A helper script saved outside the repo (scratchpad, `%TEMP%`) silently gets no `DATABASE_URL` and runs against SQLite while you think you're reading Neon. Print `database._is_postgres()` before trusting any "live" number.
- **Vercel Environment Variables (names only):** `DATABASE_URL`, `ANTHROPIC_API_KEY`, `SECRET_KEY`, `SECURE_COOKIES`. Updated under Vercel -> Project Settings -> Environment Variables (requires a Redeploy to take effect).

### From `## Running it` › `### Deploy sequence`

**Production deploys on Vercel automatically on push to `main`:**

```powershell
cd "C:\Users\sepulturian\Documents\Claude\projects\bomu"
git status -s                  # avoid sweeping dirty static/*.jpg or redesign/
git add <changed files>
git commit -m "..."
git push origin main           # triggers automatic Vercel production build
```

**Legacy host note (PythonAnywhere, retired 2026-11-15):** `sepulturian.pythonanywhere.com` now 301-redirects every path to `https://www.bomu.lol` (WSGI file replaced 2026-11-15; old one backed up at `~/wsgi_before_redirect_2026-11-15.py`, `~/bomu` and its `bomu.db` left in place). Free-tier app: click "Run until 1 month from today" on the PA Web tab monthly or the redirect goes dark. `/static/` is still served directly by PA's static mapping, so it doesn't redirect. Before moving to Vercel + Neon, the app ran at `https://sepulturian.pythonanywhere.com` (`/home/sepulturian/bomu`) with manual `python3 backup_db.py`, `git pull`, `python3 <migration>.py --commit`, and Web tab Reload. Schema/data migrations targeting Postgres now run against `DATABASE_URL` instead (test first via `FORCE_SQLITE=1` / `verify_routes.py`).

### From `## Running it` › `### Verification`

**Check the matcher directly, not through the browser.** Chrome caches
`/` (Tonight; `/recommend` now just redirects there) and `/one-away`
aggressively. On 2026-07-24 a stale render showed a bottle that does not exist
in the database and sent an hour into chasing a bug that was never real.
Authoritative check, run from the repo root so `.env` is found:

The `python3 ...` forms further down date from the PythonAnywhere era; on the
laptop use `venv\Scripts\python.exe`.

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

### From `## Gotchas`

**The local `bomu.db` used to be stale and pre-multi-user. It no longer is.**
Until 2026-11-15 it had no `user_id` on `bottles` and zero users, and developing
against it caused the 2026-07-26 false alarm. It is now a copy of the
PythonAnywhere snapshot (see Running it). Older docstrings still warn that
`bomu.db` is stale (`verify_routes.py`, `migrate_enhancements.py`); those
comments predate the swap.

**SQLite side files can eat committed data.** On 2026-07-23 a `.db-journal`
rolled the live database back. Both `.gitignore` and every migration script now
refuse to proceed if `bomu.db-journal`, `-wal` or `-shm` is present. Keep that
guard in any new script.

**`.git` is not writable from the Cowork sandbox** (that sandbox only; Claude
Code in the desktop app and Antigravity outside its sandbox can commit). Agent tooling there can stage files
but cannot create commits (it can't remove `.git/index.lock`). Commits and pushes
have to be run by hand in PowerShell:

```powershell
cd "C:\Users\sepulturian\Documents\Claude\projects\bomu"
del .git\index.lock
git commit -m "..."
git push origin main
```

### From `## Data model`

**`recipe_enhancements`** (added 2026-07-29, pruned 2026-11-20 to 24 genuine riffs across 23 recipes after moving standard garnishes into `recipe_ingredients` as `optional`): optional "make it your
own" suggestions shown on the recipe page. Columns `recipe_id`, `name`,
`ingredient_name` (checklist key, may be NULL), `measure`, `note`, `source`,
`sort_order`. Copy lives in `enhance_text.py`. **The matcher never reads it**, so
it cannot change makeability. `migrate_enhancements.py` refuses rows with no
source, rows naming a nonexistent checklist ingredient, and rows duplicating
something the recipe already requires. It deletes rows whose name is no longer
in `enhance_text.py` (renames), and `--postgres` writes to Neon. `migrate_hygiene_2026_11.py` restored `UNIQUE (recipe_id, name)`, `NOT NULL` defaults, and `idx_recipe_enhancements_recipe` on Neon on 2026-11-19 (matching `database.init_db()`), while still using update-then-insert for portability. The page shows `source` only as a tag, "By the book" or "Bartender's habit"; the copy rules are rule 4 in `enhance_text.py`.

Users as of 2026-07-24: 1 aaron, 2 Avishka, 3 Rajapaksha, 4 lenasheh (Shehan,
Aaron's brother), 5 Maho.

### From `## Data model` › `### recipe_ingredients`

The important table. `requirement_type` is one of:

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

### From `## Data model` › `### recipes`

- 171 rows
- Instructions carry a `[BOMU_REWRITTEN_v1]` marker, stripped by the
  `clean_instructions` filter
- Images: 73 have a TheCocktailDB `image_url`; the other 98 have none and use a
  studio WebP at `static/recipes/<slug>.webp` instead. `recipe_image_url()` in
  `app.py` checks the local WebP first, then `image_url`. Every recipe has an
  image as of 2026-11-15.

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

### From `## Data model` › `### ingredients`

Checklist rows are **user-facing shopping instructions**, not internal keys. The
nudge and spotlight read them out loud and tell people to go buy them, so a wrong
or ambiguous label is the app confidently sending someone to the wrong shelf.
That is why `Grape Soda` became `Grapefruit soda` on 2026-07-25 and
`Coconut cream` became `Cream of coconut` on 2026-11-20.

A rename touches five places: the `ingredients` row, `recipe_ingredients` rows
(`ingredient` and `optional`), `recipe_enhancements` rows, `user_stock` ticks
(if merging or clearing), plus `SEED_INGREDIENTS` in `database.py` and
`SUGGESTIONS` in `suggestions.py` where applicable. (My Bar dropped ingredient
tile photos in the `07db78f` redesign and `ingredient_slug()` was deleted in
`deb8d0e`, so `static/ingredients/` is no longer read by the app.)

### From `` ## The matcher (`matching.py`) ``

Two strategies, chosen per ingredient:

**Fungible spirits** match by category via `FUNGIBLE_TYPES`. Generic parents
accept their sub-types, so `whiskey` accepts bourbon/scotch/rye/irish.

**Name-matched** types (`liqueur`, `amaro`, `other`, plus specialty keywords like
cachaca and pisco) match by substring against the bottle's name. This means
`notes` on those rows **must** contain a distinctive keyword of 4+ characters, or
the requirement is permanently unsatisfiable. Campari must not match Cointreau
just because both are liqueurs.

Keys come from `_liqueur_keys(raw_name, notes)`, which returns **whole strings
only**: the folded source, plus one variant with brackets and noise words
(`\b(?:liqueur|liquor|the)\b`) stripped on word boundaries. It never splits a
string into candidate sub-names. So a source that reads like a sentence is
unsatisfiable, because no bottle is named `Elderflower Liqueur (St-Germain)`.
This is what `sweep_namematch.py` audits. One known sharp edge:

- Brackets are stripped, not their *contents*, so `Cointreau (orange liqueur)`
  yields `cointreau orange`, splicing two words that were never adjacent.
  Neither key matches a bottle named `Cointreau`. Keep notes concise.

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

### From `` ## The matcher (`matching.py`) `` › `### Sub-types (added 2026-07-24)`

Legacy bottles still on a generic type stay **permissive**: `rye` accepts
`{rye, whiskey}` and `vermouth_sweet` accepts `{vermouth_sweet, vermouth}`. The
reasoning is that we don't know an unlabelled whiskey *isn't* rye, and a false
negative (hiding a drink someone can make) is worse than mild permissiveness.
`bourbon` and `scotch` stay strict because the scanner has always identified
those reliably.

### From `` ## The matcher (`matching.py`) `` › `### Distinct-bottle assignment`

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

### From `` ## The matcher (`matching.py`) `` › `### The one-ingredient spotlight (replaced the mixer gap, 2026-11-15)`

`build_one_away_spotlight()` answers "which ONE ingredient, mixer or bottle,
would unlock the most drinks?" and Tonight shows it as a card under the
featured pour: a headline naming a drink, the ingredient in a pill, photo tiles
of every drink it unlocks (each opens the recipe), and one action.

- Computed inside `get_recommendations` from the *untruncated* one-away list,
  so no extra matcher pass. Every one-away recipe is blocked by exactly one
  thing, so grouping blockers by name and counting is exact.
- **Mixers and bottles both count.** A mixer gets a one-drink head start in the
  ranking (often already owned, never ticked), so a bottle wins only when it
  unlocks 2+ more drinks. Floor of 2 drinks, applied **before** ranking:
  applied after, a 1-drink mixer outranked Shehan's 2-drink Amaretto, failed the
  floor, and hid the card from the one user with 0 makeable.
- **Headline drink** = liked first, never disliked if avoidable, then the
  lowest recipe id (oldest rows are the classic catalog: bourbon → Old
  Fashioned, not alphabetical Gold Rush).
- **Action.** Mixer: "I have this" POSTs one id to `/stock-add` (adds only).
  Bottle: "Add to my bar" links to `/bar?sheet=add&type=…` with the type
  preselected, plus `&name=…` for name-matched bottles, because a name-matched
  requirement only matches a bottle whose *name* contains the key. `/bar`
  passes `type` through only if it is in `VALID_BOTTLE_TYPES`.
- **Copy** lives in `SPOTLIGHT_LINES` in `app.py`, rotated by date. Built as
  `(text, is_drink)` segments so no `|safe` is needed. The ingredient is kept
  out of the headline on purpose: in a pill its casing (`Angostura bitters`,
  `Lemon juice (fresh)`) never has to survive mid-sentence.
- Mixer blockers that aren't a real checklist row are skipped (no id to tick).

**Old lesson still worth keeping:** the mixer-gap dict used the key **`picks`,
not `items`**, because Jinja resolves `gap.items` to `dict.items()` before it
looks for a key and the template 500s at render. `py_compile` does not catch
this; only rendering the template does. Same rule for any new dict passed to
a template.

### From `## Scanner`

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

### From `## Scanner` › `### Untrusted type values`

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

### From `## Adding recipes`

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

### From `## Templates`

Design system lives in one `<style>` block in `base.html` ("Espresso & Zest"
since `07db78f`): espresso surfaces (`--bg-base` #110d0a), `--zest` #f4c430
yellow, sage / terracotta for status, Barlow Condensed for display, Plus Jakarta
Sans for body. (Until 2026-11-15 this line still described the pre-redesign
coral / Bodoni Moda / Poppins system.) Page-specific styling is inline.

**Buttons: "the pour"** (2026-11-15, ninth session; replaced first the
stamped offset-shadow buttons, then a plain solid/hairline set Aaron found
"okay, could be way better"). `.btn` is solid zest (`#efb92b`) with Barlow
Condensed 600 in sentence case, and is the ONE main action on a view. Its
`::before` is a liquid level with a pale meniscus line: hover raises it halfway,
press fills it, and a `pointerdown` handler in `base.html` adds `.is-pouring`
so a tap shows the fill on phones. `.btn-glass` is the "empty glass" (dark face,
zest rim, cream text) that pours full on press; it needs `data-label` matching
its text, because `::after` is a dark copy of the label revealed at the liquid
line (uses `@property --lvl`). It's used for the spotlight's "I have this" /
"Add to my bar". The quiet styles use the body font: `.btn-secondary` is a dark
hairline face (zest only on hover), `.btn-ghost` is plain text, `.btn-danger`
is an underlined red text link. Tonight: "Mix it" is the solid button; the
spotlight card keeps yellow to the drink name and the glass only. Don't
reintroduce offset shadows, all-caps button text, serif buttons, gradients,
glows or 999px radii on buttons: Aaron called the glossy gradient pill "an AI
giveaway". Chips and status pills stay rounded on purpose. That's fine at
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

### 2026-07-29 commits (no session log was written at the time)

*Filed here by date on 2026-11-21; until then it sat under `## Where things stand` in `CLAUDE.md`. Written on 2026-11-15 from the commit messages and migration docstrings.*

- `20747dc` — **"Make it your own" enhancements.** New `recipe_enhancements`
  table (see Data model), copy in `enhance_text.py`, loaded by
  `migrate_enhancements.py`, rendered on `recipe.html`. Also
  `migrate_normalize_optional.py` (collapsed garnish spellings like
  `Orange Peel / Orange twist / Orange slice`, dropped `Ice` / `Water` rows that
  were tagged optional) and the double-numbered-steps fix. Both migrations were
  designed to move the matcher by **zero**: neither table/row type is read by
  `matching.py`.
- `80d4f63` — loosened the enhancement bar from "documented" to
  "documented-or-practice" and labelled the difference on the page.

### 2026-11-14

Planning session only, no app code changed. Read Lenny's Newsletter piece on
pushing AI design past its defaults (seed strings for randomness, a fresh-context
critic reviewing screenshots only, image/video generation, a final cut pass) and
turned it into a brief for a full UI/UX overhaul to run in Antigravity.

**Written:** `redesign/REDESIGN_BRIEF.md`, `redesign/CRITIC_PROMPT.md`,
`redesign/inspiration/` (two coffee-app mockups Aaron likes the feel of), and
`redesign/dev.db` added to `.gitignore`.

**Decisions.** Stay on Flask: the look lives in templates and CSS, and the
"feels like a website" problem is handled with cross-document View Transitions
and optionally htmx, not a React rewrite. Phone-first. The agent may merge pages
and change routes (old URLs redirect); proposed nav is four tabs, Tonight / Bar /
Explore / Saved. Randomness is bounded: fixed anchors from the moodboard, seeded
variables for accent, type, shape, texture, motion and a signature element. Two
review rounds on Argon, screenshots only, same prompt both times, no target score
in the prompt. Recipe images: 6-image style test before generating the other 92.

**Priorities, Aaron's call:** aesthetic, usability and navigation. Friends'
feedback is explicitly not an input for this redesign.

### 2026-11-15 — UI/UX Overhaul + Moved to Vercel, Neon Postgres & bomu.lol

**Shipped commits (`main`):**
- `07db78f` — **Espresso & Zest UI redesign**: responsive mobile + desktop
  (`1280x800`) templates (`base.html`, `tonight.html`, `explore.html`, `my_bar.html`,
  `saved.html`, `one_away.html`, `recipe.html`), custom nav icons (`static/nav/*.webp`),
  `static/empty-bar.webp`, `manifest.json`, `sw.js`, and 94 newly generated studio
  cocktail WebPs (`static/recipes/*.webp`, 98 total files covering 171/171 recipes).
- `295e47b` — **Neon Postgres + Vercel setup**: dual-mode `database.py` (Postgres
  when `DATABASE_URL`/`POSTGRES_URL` is set, SQLite fallback otherwise; batched
  `get_all_recipes()` down to 2 queries), serverless `/tmp` upload handling in
  `app.py`, `vercel.json` Flask routing, `requirements.txt` (`psycopg2-binary==2.9.13`),
  and `migrate_to_postgres.py`. Migrated 1:1 from PythonAnywhere snapshot
  `bomu_live.db` (`users=5`, `ingredients=51`, `recipes=171`, `recipe_ingredients=762`,
  `recipe_enhancements=106`, `bottles=35`, `user_stock=32`, `ratings=4`, `scan_log=12`).
- `9a335ba` — Hardened `_pg_url()` in `database.py` to strip whitespace/CR/LF,
  surrounding quotes, and `channel_binding=` parameters for Vercel Linux `libpq`.
- `e5f4e3b`, `ba53ac9` — Added `AGENTS.md` pointer and shared cross-agent
  `Session handoff protocol` in `CLAUDE.md`.

**Production infrastructure & DNS:**
- **Live URL:** `https://www.bomu.lol` (`https://bomu.lol` 308-redirects to `www`;
  Vercel alias `https://bomu.vercel.app`). Auto-deploys on push to `main`.
- **Porkbun DNS (`bomu.lol`):** Replaced default `pixie.porkbun.com` parking records
  with `A @ -> 76.76.21.21` and `CNAME www -> cname.vercel-dns.com` (TTL 600).
- **Neon Postgres (`broad-water-80207736`):** Claimed into Aaron's Neon account.
- **Vercel env vars (names only):** `DATABASE_URL`, `ANTHROPIC_API_KEY`,
  `SECRET_KEY`, `SECURE_COOKIES`.

**Gotchas hit & resolved:**
- **Post-claim Neon password rotation:** Claiming `broad-water-80207736` rotated
  `neondb_owner`'s password, causing `POST /login` on `www.bomu.lol` to return 500
  (`password authentication failed`) while `GET /login` returned 200 (no DB query).
  Retrieved the active pooled connection string from Neon Console, updated
  `DATABASE_URL` in Vercel, redeployed to Production, and updated local `.env`
  (`DATABASE_URL` and `DATABASE_URL_UNPOOLED`) to match.
- **Sandbox constraints in Antigravity:** `.git`, `npm`/`npx`, network connections,
  and `.env` writes require running commands outside the default sandbox.

**Verified at close:**
- Live site login (`https://www.bomu.lol`) verified working by Aaron after redeploy.
- `venv\Scripts\python.exe verify_routes.py` -> `171 ok, 0 failed`.
- `matching.get_recommendations(1)` against live Neon Postgres via updated `.env` ->
  `34 makeable, 70 one-away`.

**Open / optional items:**
- Vercel's Domains settings suggest updating Porkbun DNS from `76.76.21.21` /
  `cname.vercel-dns.com` to per-project targets (`216.198.79.1` /
  `da4ba196cd936738.vercel-dns-017.com.`), though current records work with active SSL.
- Local dirty files (`static/*.jpg`, `static/icon-*.png`, untracked `redesign/`)
  remain intentionally unstaged.
- Note: a browser subagent intermediate output (`179a4452-.../browser_sandbox/outputs/step_88.json`)
  under AppData brain logs still holds the extracted connection string from recovery.

### Completed 2026-11-15: UI/UX overhaul + Vercel / Neon / bomu.lol migration

*Filed here by date on 2026-11-21; until then it sat under `## Where things stand` in `CLAUDE.md` as the summary of the entry above.*

- **Espresso & Zest UI redesign (`07db78f`)**: Responsive phone + desktop templates
  (`base.html`, `tonight.html`, `explore.html`, `my_bar.html`, `saved.html`,
  `one_away.html`, `recipe.html`), custom nav icons (`static/nav/*.webp`), and
  complete studio cocktail photography coverage (`static/recipes/*.webp`, 98 WebP files
  for the 98 recipes with no `image_url`; the other 73 still use TheCocktailDB URLs).
- **Production migration (`295e47b`, `9a335ba`)**: Moved live hosting from
  PythonAnywhere to **Vercel** (`sepulturian/bomu`) at **https://www.bomu.lol**,
  backed by **Neon Postgres** (`broad-water-80207736`) migrated 1:1 from `bomu_live.db`.

### 2026-11-15 (second session) — Review and CLAUDE.md audit (Claude Code)

Docs only, no app code or data changed. Asked for a "where are we" review; did
it by checking this file against git, the code, the local SQLite files and live
Neon, not by re-reading it.

**Found and corrected in this file:**

- *User counts.* The top table still showed the 2026-07-26 numbers (Aaron 22).
  Live Neon has Aaron at **34 makeable / 70 one-away** on 19 mixers, matching the
  first 2026-11-15 entry. The +12 came entirely from 3 more mixer ticks; the
  catalog on Neon is identical to the snapshot (762 recipe_ingredients rows,
  291 / 326 / 145 by type). Other users unchanged.
- *Local dev.* The "bomu.db is stale and pre-multi-user" gotcha was false:
  `bomu.db` is byte-identical to `bomu_live.db`. Backlog #4 closed.
- *Images.* "98 recipes have no image" and backlog #9 were stale. The 98
  studio WebPs cover exactly the 98 recipes with no `image_url`. #9 closed.
- *`recipe_enhancements`* was missing from Data model, and the 2026-07-29
  commits had no write-up. Both added (from the commit messages and migration
  docstrings, not from memory).
- *Backlog hygiene.* #14's text contradicted its strikethrough; #5 and #12
  duplicated each other (merged); The matcher pointed at #14 for what is #16.
  Added #17 (leaked connection string, still on disk) and #18 (DNS, optional).
- *Verification* commands updated for the laptop + Neon world.

**Gotcha hit.** The first "live" count came back 22 / 72, identical to the
snapshot. That was SQLite: the helper script lived in `%TEMP%`, and
`load_dotenv()` searches for `.env` from the *script's* directory, not the cwd.
No error, no warning, plausible numbers. Recorded under Running it. Same lesson
as 2026-07-26 in a new form: a result that agrees suspiciously well with the
wrong source is evidence about the tool first.

**Still open:** Hugo Spritz row 398 (#15), Shehan 0 from 16 (#2), the two
never-started users (#1), and the leaked string + password rotation (#17).

### 2026-11-15 (third session) — "One ingredient away" spotlight (Claude Code)

Aaron didn't like "+3 mixers unlock 9 more drinks" and wanted the "one
ingredient short" idea to get real attention. Designed together via questions:
mixers *and* bottles, one spotlight plus "More ingredients →", an "I have this"
button, a headline that names a drink with a bit of wit.

**Changed:** `matching.py` (`build_mixer_gap` → `build_one_away_spotlight`,
result key `mixer_gap` → `spotlight`), `app.py` (headline copy + helpers,
`/bar` prefill args), `templates/tonight.html` (banner → spotlight card),
`templates/my_bar.html` (prefill + Sweet Vermouth chip fix). See "The
one-ingredient spotlight" under The matcher.

**Why the old banner was weak, measured on live:** it summed three separate
3-drink mixers into "+9", and ignored bottles although 45 of Aaron's 70
one-away drinks were blocked by one (bourbon → 5, dry vermouth → 5).

**Found while building:**
- *Shehan got no spotlight at all* on the first version. Ranking-before-floor
  bug, see the matcher section. Fixed; he now sees "Pick up Amaretto" →
  French Connection, Godfather.
- *The Sweet Vermouth quick chip in the Add Bottle sheet was dead.* It set
  `sweet_vermouth`; the type is `vermouth_sweet`. The select stayed empty and
  the form refused to submit until a type was picked from the dropdown. Fixed.

**Verified:** makeable / one-away unchanged on SQLite (22/72) and Neon (34/70)
for all 5 users; Tonight, grouped Tonight and My Bar (with good, name-matched
and junk prefill args) render 200 for every user on both backends (GET only on
Neon); all 4 headline variants checked for a/an; `verify_routes.py` passes.
In the browser on a scratch copy of the snapshot: "I have this" ticked Ginger
beer (Aaron 22 → 27, spotlight moved to Champagne); "Add to my bar" opened the
sheet with Amaretto + Liqueur prefilled, and submitting it took Shehan 0 → 2.
Phone (375px) layout checked.

**Live today:** Aaron's spotlight is "Pick up Bourbon" (Old Fashioned headline,
5 drinks); Maho's is Lemon juice (fresh) → Tom Collins, Bee's Knees.

### 2026-11-15 (fourth session) — "Ready" / "One away" wording (Claude Code)

Aaron liked the look of the Tonight stat line but not what it said:
`34 make now · 70 1 away →`. Objective problems: "70 1 away" reads as one
number ("701"); "make now" has no noun and disagreed with the "More ready"
heading right below it; and the digit form "1 Ingredient Away" clashed with
the new spotlight's spelled-out "One ingredient away".

**Agreed:** keep both stats; **"Ready"** for makeable and **"One away"** for
one-ingredient-short, used everywhere, not just on that line.

**Changed (templates only, 14 lines):** Tonight stat line →
`34 ready · 70 one away →`; Tonight row subtitles and carousel heading;
Explore filter chips (`Ready (n)`, `One away (n)`) and row status; Saved row
status; one-away page title and H1 (`One Away`). The URL stays `/one-away` and
Explore's filters key off `data-val`, so no behaviour changed. The spotlight's
"One ingredient away" / "One bottle away" kicker stays as is, being the
specific form of the same idea.

**Verified:** grep finds no remaining "make now", "1 away" or "1 Ingredient
Away" in templates; `verify_routes.py` passes; checked Tonight, Explore and
One Away in the browser on a scratch copy.

**Open at close of day:** Hugo Spritz row 398 (#15), Shehan 0 from 16 (#2,
the Amaretto spotlight may now help), never-started users (#1), and the leaked
connection string + Neon password rotation (#17, Aaron's action).

### 2026-11-15 (fifth session) — Header, login photo, stamped buttons (Claude Code)

Aaron asked for three visual changes and to be asked questions first.

**Shipped:** `e6b89f6`, templates only (`base.html`, `login.html`,
`signup.html`, `recipe.html`), pushed and confirmed live on www.bomu.lol.

- *Header:* avatar dropdown replaced by plain text `aaron · out`, the style the
  app used before the redesign. "out" opens a `<dialog>`: "Calling it a
  night?" / "One more round" (stay, autofocused) / "Close my tab" (POST
  `/logout`). Aaron proposed "One for the road" for the stay button; changed
  because it idiomatically means a last drink *before leaving*, so it reads
  as "yes" on a leaving prompt. His call to revert, one line in `base.html`.
  Backdrop tap closes via `closedby="any"` plus a bounds-checked JS fallback
  (a bare `e.target === dlg` check also fires on the dialog's own padding).
- *Login/signup photo:* `aspect-ratio: 3/2` + `max-height: 210px` transfers
  to a ~315px width, so the card sat left under a 420px form. Now
  `max-width: 315px; margin: 0 auto`. Aaron chose centred-same-size over
  full width.
- *Buttons:* see Templates. Shadow colour picked by rendering four candidates
  side by side: `#8a6410` was invisible on the espresso background, cream read
  grey, terracotta added a second accent to every button; amber `#b07d0c` won.
  Recipe dock Back / Liked / Pass converted too. Chips, filter toggles and
  status pills deliberately untouched ("buttons only").

**Verified:** `verify_routes.py` passes; on a scratch copy of `bomu.db`
(`FORCE_SQLITE=1`) checked login, Tonight, the dialog's three exits and the
recipe dock at desktop and 375px. Live: `/login` serves the new CSS. The
logged-in header was not checked on live.

**Gotchas:**
- *A session cookie with `user_id` but no `username` hides the account UI
  entirely.* `current_username` comes from `session["username"]`; the browser
  pane had an old cookie like that and showed no header text at all. Any real
  user with such a cookie has no way to sign out short of clearing cookies.
  Pre-existing (the avatar had the same gate). Cheap fix: look the name up in
  the context processor when `user_id` is set and `username` isn't. Backlog #19.
- *The local preview runs `debug=False`, so Jinja caches templates;* restart
  the server after a template edit or you'll be checking the old render.

**Open:** #19 below, plus Hugo Spritz row 398 (#15), Shehan 0 from 16 (#2),
never-started users (#1), leaked connection string + Neon password (#17).

### 2026-11-15 (sixth session) — Auth redesign: Isometric Sri Lankan beach bar diorama (Antigravity)

Aaron asked to redesign the login and signup pages inspired by his "Timelines" login screen (miniature diorama, editorial note, card bridge). Initially explored a Japanese watercolor bar, then pivoted to an open-air coastal beach bar diorama set in Unawatuna / Tangalle, Sri Lanka, with a hanging wooden "BOMU" sign.

**Changes:**
- *Artwork:* Generated `static/beach-bar-diorama.webp` (`783x922` transparent WebP). An isometric 3D miniature cutaway diorama of an open-air teak and cadjan-thatch beach bar on golden sand, coastal rocks, and translucent turquoise ocean surf, featuring a rustic hand-painted "BOMU" hanging signboard, warm string lights, king coconuts (*thambili*), limes, three woven barstools, bottles on backbar shelves, leaning coconut palm, striped surfboard, frangipani blossoms, and a sleeping ginger cat beside a brass lantern. Rendered with transparent background and soft drop shadow, floating directly over `#110d0a`.
- *Editorial copy:* Added `Cormorant Garamond` serif headings and clean 1-sentence italic narratives:
  - Login: "Bar Note No. 09 · Unawatuna Shore" / *"A good home bar gathers one bottle at a time."*
  - Signup: "Bar Note No. 01 · Starting the Shelf" / *"Every shelf starts with one bottle."*
- *Dynamic time kicker:* Created `templates/components/bar_clock.html`, displaying the visitor's local 12-hour time and mood tag (e.g. `7:54 PM · EVENING POUR`, shifting across Nightcap, Quiet Counter, Daylight Pour, Golden Hour, Aperitivo, Evening Pour, After Hours) in place of static coordinates.
- *Layout:* Desktop split view with `.auth-form-card` overlapping the lower-right sand edge of the diorama (34px bridge). Mobile stacks cleanly with the entire layout fitting above the fold (`771px` height) with zero horizontal overflow.
- *Cache & Service Worker:* Bumped `CACHE_VERSION` to `bomu-v6` in `static/sw.js`.

**Verified:**
- `verify_routes.py` passes (171 ok, 0 failed; `GET /login` and `GET /signup` HTTP 200).
- Visual inspection on desktop (1280x800) and mobile (375x812) via browser subagent and user live preview.

**Open:** #19 below, plus Hugo Spritz row 398 (#15), Shehan 0 from 16 (#2),
never-started users (#1), leaked connection string + Neon password (#17).

### 2026-11-15 (seventh session) — "Make it your own" copy rewrite (Claude Code)

Aaron flagged the Negroni's "Make it your own" card as too long and
unreadable: "Not in the Difford's or IBA build...", "how is anyone reading
supposed to know that?" The copy had been written to make the
"nothing invented" rule auditable, so every note cited its source and
the page printed it. Correct for a reviewer, footnotes for a drinker.

**Decided with Aaron:** two plain sentences per note (what to do, then
why); the source line becomes a tag, "By the book" (named source) or
"Bartender's habit" (PRACTICE), sharing a line with "In your bar" / "Needs X";
rewrite all 166; one review pass by a Fable 5.2 critic subagent, then act on it.

**Changed:** `enhance_text.py` (all 166 notes, 11 names de-jargoned, e.g.
"Slapped mint bouquet" → "Big mint sprig", "Muddle skin-side down" → "Press
the lime gently"; new rule 5 on plain English), `templates/recipe.html` (tag;
full source kept as a hover `title`), `migrate_enhancements.py` (prunes rows
renamed out of `enhance_text.py`, `--postgres` mode, update-then-insert).
Median note 148 → 116 chars. `source` values unchanged.

**The critic earned its keep.** 26 flags, about 34 edits. Worst: simplifying
"Trader Vic's own garnish" into "Trader Vic, who created the drink" invented a
claim that `about_text.py` says is contested; "sold ready-mixed" had drifted to
"sold in cans". Same lesson as before in a new place: a rewrite for clarity can
add facts, so diff meaning against the old copy, not just length. It also found
the Caipirinha's old name ("skin-side down") contradicting its own note; the
new wording takes no side.

**Gotcha:** the first Neon commit failed (and rolled back) because the Neon
table lacks the UNIQUE (recipe_id, name) constraint the SQLite schema has, so
`ON CONFLICT` had nothing to match. `migrate_to_postgres.py` may have dropped
other constraints the same way; not audited.

**Verified:** scratch copy of `bomu.db` migrated twice (second run no-op),
`verify_routes.py --db` all routes render, Negroni and Mojito checked in the
browser. On Neon: 106 rows, 9 renamed in / 9 stale deleted, re-run no-op, all
5 users' makeable / one-away unchanged (34/70, 0/0, 0/0, 0/14, 1/13).
`check_specs.py` reports 3 flagged recipes on `bomu.db` (e.g. Caesar lime-juice
measure), unrelated to this change and not investigated.

**Open:** audit Neon for other constraints lost in the Postgres migration;
the 3 `check_specs.py` flags; plus #19, #15, #2, #1, #17.

### 2026-11-15 (eighth session) — Button redesign (Claude Code)

Aaron called the stamped yellow buttons "terrible": the offset shadow, the
all-caps condensed type and the chunky proportions. Four directions were mocked
on the real tokens (A bar-menu serif outline, B soft solid, C cream label
with a double rule, D dark brass inlay). A Fable 5.2 critic reviewed
screenshots only and ranked B > D > A > C: only B made the primary action
unmistakable at 375px, D was the best quiet button, A's serif went thin at small
sizes, and C was still shouty and wrapped on phones. It recommended a hybrid
(B's fill for primary, D's face for secondary, text-only tertiary, outline
danger), which Aaron approved from the mockup.

**Changed:** `base.html` button block (see Templates), `--radius-btn` 4 → 10px;
`recipe.html` dock (Back is text; Like / Pass are dark hairline buttons that keep
their sage / terracotta rated states); sentence-case labels across 11
templates; `→` on Log in / Create account.

**Verified:** `verify_routes.py` passes; on the scratch copy at 375px: recipe
dock, Tonight spotlight ("I have this", "Mix it"), My Bar header button,
sign-out dialog (no wrap), edit bottle (Save / Cancel / Delete), and the login
form (rendered from a cookie-less fetch, since `/login` redirects when logged in).
Desktop (1280) checked on edit bottle and the recipe page.

### 2026-11-15 (ninth session) — The pour: signature buttons (Claude Code)

Aaron found the eighth session's buttons "okay, could be way better". The
diagnosis: competent but generic, with yellow on nearly every screen and
nothing that said Bomu. Three variants were mocked on real screens (V1 the pour in
the body font, V2 the pour in Barlow Condensed, V3 an empty glass), all sharing a
restraint pass. A Fable critic reviewed screenshots only and picked V2. It
flagged that the pour was invisible in V1/V2 (yellow on yellow is about 1.1:1)
and that V3's mid-pour label was illegible, and it suggested reusing V3's glass
for "I have this" only. A refined mock followed; Aaron chose the brand-type
version.

**Changed:** `base.html` (button block rewritten, see Templates; tap JS),
`tonight.html` ("I have this" / "Add to my bar" → `.btn-glass`, muted spotlight
kicker, cream "More ingredients", "Mix it" pours on card hover), `edit_bottle.html`
unchanged in markup (`.btn-danger` is now a text link).

**Verified:** `verify_routes.py` passes; at 375px on the scratch copy: Tonight
(rest, plus the glass frozen full), edit bottle. Login was not re-checked
after rollout; it uses the same `.btn`.

**Gotcha:** the glass label's dark copy only lines up if the label can't wrap,
so `.btn` has `white-space: nowrap`. A long label in a narrow container will
overflow rather than wrap; none do today.

**Open at close:** Neon constraints possibly lost in the Postgres migration
(found in session seven); 3 `check_specs.py` flags; #19 sign-out for
cookies without `username`; #15 Hugo Spritz; #2 Shehan 0 from 16; #1
never-started users; #17 leaked connection string and Neon password (Aaron's
action). An untracked `.claude/launch.json` (local preview config pointing at a
scratchpad runner) was deliberately left out of commits.

### 2026-11-15 (ninth session, addendum) — Bottle type picker

The Add Bottle sheet's type chips (round pills, gradient, glow under the
selected one) broke the button rules above. Now an even 4×2 grid of flat 10px
tiles in Barlow Condensed: Gin, Vodka, Rum, Tequila / Bourbon, Rye, **Scotch**
(new; Shehan's shelf is mostly Scotch), Sweet vermouth. The chosen tile pours
full of zest. "Other type…" became a quiet "More types ▾" text link that opens
the full dropdown. Class names and ids unchanged, so the JS wiring is
untouched. `verify_routes.py` passes; checked at 375px with `?type=rye`
prefilled. The sheet's scan cards followed in the same session: flat tiles,
cream hairline, Barlow in sentence case ("Scan a bottle" / "Scan a shelf"),
with no gradient or shadow.

### 2026-11-15 (ninth session, addendum 2) — Two wording fixes

- Tonight stat line: `34 ready · 70 one away →` → `34 ready · 70 almost
  there →`. "70 one away" put a number next to a word-number. Aaron's call:
  Tonight's line only. "One away" stays everywhere else (Explore chip, rows,
  the One Away page), where it never sits right after a number.
- Login note: "Bar Note No. 09 · Unawatuna Shore" → "· South Coast".

### 2026-11-15 (tenth session) — Mobile auth layout polish (Antigravity)

Aaron pointed out that while desktop looked great, mobile felt awkward (small 245px diorama floating in a black void, harsh horizontal divider cutting across the note, disjointed stacked feel).

**Changes:**
- *Mobile diorama scale:* Increased from `max-width: 245px` to `295px` (`width: 82vw`), giving the miniature beach bar a confident hero presence on phone screens.
- *Ambient warmth:* Added a soft radial amber/gold glow (`rgba(244, 196, 48, 0.18)`) via `.auth-art::before`, lifting the diorama off the obsidian background.
- *Single divider:* Dropped the top horizontal border on `.bar-note` on mobile, keeping only a single subtle hairline under the note. Added a soft text shadow for crisp contrast.
- *Tactile overlap:* Pulled the editorial note and form card UP via `margin-top: -2.25rem` on mobile, bridging 36px over the lower water and rocks of the diorama to mirror desktop's layered feel.
- *Templates:* Applied to both `templates/login.html` and `templates/signup.html`.

**Verified:**
- `verify_routes.py` passes (171 ok, 0 failed).
- Verified via browser subagent at mobile 375x812 (all content fits above the fold in 777px, zero horizontal overflow) and desktop 1280x800 (clean 34px horizontal card overlap).

### 2026-11-15 (eleventh session) — 16:9 widescreen Sri Lankan sunset beach bar diorama with beach dog & Arrack sign (Antigravity)

Aaron requested an isometric beach bar redesign with true horizontal presence across mobile and desktop, genuine sunset atmosphere, and down-south authenticity:
- Dropped the previous 2D sunburst/cloudburst overlay, which clashed with the 3D isometric perspective.
- Shifted to an expansive 16:9 widescreen 3D isometric miniature diorama (`1376x768` RGBA WebP) created as `static/beach-bar-sunset-diorama.webp` (and mirrored to `static/beach-bar-sunset.webp`).
- *Down-south authenticity:* Replaced the cat with a friendly golden-tan Sri Lankan beach stray dog curled up asleep on the front teak deck, added a carved wooden "Arrack" sign on the back shelf next to the "BOMU" eave sign, and featured a traditional wooden outrigger boat (*oruwa*) resting in the turquoise bay.
- *Sunset horizon:* A serene golden sun setting onto the Indian Ocean horizon on the left, casting a shimmering warm light trail across calm turquoise ripples, with the sky smoothly dissolving into `#110d0a` (zero sunbursts or harsh god-rays).
- *Perimeter feathering:* Alpha boundary feathered softly into `#110d0a` around the perimeter with zero visible box borders, seams, or clipping.
- *Mobile Layout:* Configured `.auth-art-col` with `width: calc(100% + 1.25rem); margin: -0.25rem -0.625rem 0;` and `.auth-art { aspect-ratio: 1376 / 768; }`, spanning ~97% of the phone screen width with commanding horizontal presence, zero horizontal overflow, and fitting all content comfortably above the fold (~650px total on 812px viewport).
- *Desktop Layout:* Centered 2-column stage (`1.22fr 0.78fr`) with `max-width: 560px` diorama and 20px card overlap, balanced gutters, and no horizontal scroll.
- *Templates:* Applied to both `templates/login.html` and `templates/signup.html`.

**Verified:**
- `verify_routes.py` passes cleanly (171 ok, 0 failed).
- Verified visually on both mobile (375x812) and desktop (1280x800) via browser subagent.

### 2026-11-16 — Centered beach bar diorama with natural irregular sand spit (Antigravity)

Aaron flagged that the original diorama was off-balance on mobile: the bar sat on the right edge, the left edge had an awkward sharp 90° acrylic box cutaway, and the sunset was far to the left. An initial test with an oval platform felt too artificial and circular ("the fact that it's a circle doesn't look good... could it be a bit more natural?"). Generated 3 distinct natural concepts (Natural Sand Spit, Open Beach, Rocky Cove) for review; Aaron selected **Concept 1 (Natural Irregular Sand Spit)**.

**Changes:**
- *Recomposed Artwork (`static/beach-bar-sunset-diorama.webp`, `static/beach-bar-sunset.webp`):* Generated and deployed a 16:9 widescreen 3D isometric diorama (`1376x768` RGBA WebP):
  - **Natural Irregular Shoreline:** Flowing natural turquoise surf, seafoam, wet sand tide lines, and smooth pebbles—completely free of circular disks, cylinders, or 90° box cutaways.
  - **Dead-Center Bar & Deck:** Centered the rustic timber thatched-roof hut ("BOMU"), 3 rattan barstools, counter (bottles, limes, shaker, king coconuts, "Arrack" sign), and front wooden deck with the sleeping golden beach dog and brass lantern directly on the horizontal centerline, aligning with the login card and submit button.
  - **Centered Sunset Horizon:** Placed the golden setting sun directly on the horizon behind the peak of the thatched roof, radiating warm twilight color continuously across both the left and right flanks.
  - **Balanced Flanking Scenery:** Traditional Sri Lankan outrigger canoe (*oruwa*) in turquoise water on the left; leaning coconut palm, vintage surfboard, and white frangipani blossoms on the right.
  - **Clean Alpha Feathering:** Alpha channel feathered smoothly into `--bg-base: #110d0a` with zero hard edges or bounding box seams.
- *Service Worker (`static/sw.js`):* Bumped `CACHE_VERSION` from `bomu-v6` to `bomu-v8` for cache busting.

**Verified:**
- `verify_routes.py` passes (171 ok, 0 failed; `GET /login` and `GET /signup` HTTP 200).
- Live preview active on local dev server (`http://localhost:5000/login` and `http://192.168.2.12:5000/login`).

### 2026-11-19 — Open signup, 2-step onboarding, 0-ready Quick Kitchen Check & hygiene sweep (Antigravity)

Started with a `/grill-me` alignment interview to prioritize what matters most after the UI/infra overhaul: getting 0-ready and never-started users to their first pours, removing the invite code on `/signup`, adding Spotlight rotation, and knocking out the small correctness/schema backlog.

**Decisions with Aaron:**
- Remove `INVITE_CODE` from `/signup` completely; protect the Anthropic scan bill with a shared global daily scan limit (`SCAN_GLOBAL_DAILY_LIMIT = 60` via `scan_log`) alongside the `15`/user/day cap and an offscreen honeypot (`website`).
- Empty-bar onboarding directly on Tonight (`bottle_count == 0`) as a 2-step quick setup (12 starter spirits / Scan shortcuts → 12 kitchen basics with `Sugar (white)` and `Salt` pre-ticked and live recipe count updates).
- Personalized **Quick Kitchen Check** card on Tonight for users with bottles logged and 0 ready drinks (e.g. Shehan), keeping `Sugar` / `Salt` pre-ticked and all other mixers unticked; hands back to the normal Spotlight once `makeable >= 1`.
- Daily Spotlight rotation across the top 4 eligible blockers by date (`day_seed`) with no extra UI.

**Changes:**
- *Open signup & scan caps (`app.py`, `database.py`, `templates/signup.html`):* Removed `INVITE_CODE` gate and invite input, added offscreen `.hp-field` honeypot, added `scans_today_global()` in `database.py` and `SCAN_GLOBAL_DAILY_LIMIT = 60` check in `_scan_allowed()`. Updated desktop signup grid so username spans full width above password + confirm.
- *Empty-bar 2-step onboarding & Quick Kitchen Check (`matching.py`, `app.py`, `templates/tonight.html`):* Added `build_onboarding_data()`, `build_kitchen_check()` (greedy set cover over non-wine mixer-only 1/2/3+ away blockers), `POST /quick-setup` (additive via `add_ingredients_to_stock()`), and live client-side matching counters matching `matching.match_recipe()` (using pour-fill `.pour-tile` toggles). Removed `hide_account` from empty-bar Tonight and redirected bottle-add from an unstocked bar back to `/` so new users land on Quick Kitchen Check.
- *Spotlight & hygiene fixes (`matching.py`, `app.py`, `database.py`, `templates/my_bar.html`, `migrate_hygiene_2026_11.py`):*
  - Daily top-4 rotation in `build_one_away_spotlight()`.
  - Word-boundary `NOISE_WORDS` in `_liqueur_keys()` (`#16`: `Green Creme de Menthe` no longer emits `green creme de men`).
  - `inject_current_user()` DB fallback when session has `user_id` without `username` (`#19`).
  - Replaced dead `'powdered sugar'` in `templates/my_bar.html` `essential_keys` with `'sugar (white)'`.
  - Created and ran `migrate_hygiene_2026_11.py` on both local `bomu.db` and live Neon Postgres (`--postgres --commit`): fixed Hugo Spritz row 398 (`raw_name = 'Elderflower Liqueur'`, `notes = 'St-Germain'`), fixed Paloma / Ti' Punch / Caesar instructions so `check_specs.py` hits 0 flags, and restored Postgres `recipe_enhancements` parity (`UNIQUE (recipe_id, name)`, `NOT NULL` on `source`/`sort_order`, `idx_recipe_enhancements_recipe`) matching `database.init_db()`.

**Verified:**
- `migrate_hygiene_2026_11.py` ran cleanly and idempotently on both `bomu.db` and live Neon Postgres (0 planned actions on re-run, 0 user matcher count changes across all 5 accounts).
- `check_specs.py` (`FORCE_SQLITE=1`): `171 recipes checked, 0 with at least one flag` (down from 3).
- `sweep_namematch.py` (`FORCE_SQLITE=1`): `0 BROKEN, 6 REVIEW` (down from 1 BROKEN).
- Python unit checks: verified `#16`, Hugo Spritz matching (`St-Germain`, `St-Germain Elderflower`, `Giffard Elderflower Liqueur`), 4-day Spotlight rotation, Shehan `build_kitchen_check` (`10` non-wine kitchen picks unlocking up to `21` drinks), and 50-trial exact parity between `build_onboarding_data()` JS matching logic and `matching.match_recipe()`.
- Extended `verify_routes.py` (covering open signup, honeypot block, `/quick-setup`, 0-ready Quick Kitchen Check, legacy cookie `username` fallback, `scans_today_global()`); passes all routes + `171/171` recipe pages.
- Browser subagent visual verification at `375x812` and `1280x800` against scratch preview server: verified `/signup`, empty-bar 2-step onboarding + live count, `testkitchen` Quick Kitchen Check unlock flow (`0 -> 6` ready drinks), and active Tonight view with zero horizontal overflow. (Caught and fixed missing `.btn` class on Step 2's `<- Back` `.btn-ghost` button afterward.)
- Authoritative live Neon read (`backend: postgres`, `recipes: 171`): Aaron `34/70` (spotlight `Grapefruit juice`), Avishka `0/0`, Rajapaksha `0/0`, Shehan `0/14` (`kitchen_check` 10 picks / max `21` unlockable), Maho `1/13`.

**Still open:** `#17` (Aaron to delete old `step_88.json` log and rotate Neon password), `#5`, `#7`, `#8`, `#10`, `#13`, `#18`.

### 2026-11-19 (second session) — QA review, recipe spec fixes & app bug bundle (Antigravity)

Followed up the login-link invite-copy fix (`0949ece`) with a comprehensive codebase, image, schema, and template QA pass, then shipped the recipe spec + app bug bundle and recorded the remaining visual/cleanup items for next session.

**Recipe spec fixes (`migrate_qa_specs_2026_11.py`, `about_text.py`, `enhance_text.py`):**
- **Americano:** Inserted required `Soda water / club soda` (`2 oz`, shifting optional twists to `sort_order` 3/4) and updated step 3 so it is no longer spec-identical to Milano-Torino.
- **White Russian:** Promoted `Light cream` row from `optional` (`ingredient_name=NULL`) to required `ingredient` pointing at `Heavy cream` (`1 oz`) and updated step 3 so it is no longer spec-identical to Black Russian.
- **Vodka Martini & Woo Woo:** Downgraded garnish rows (`Olive` / `Lime wedge`) from required `ingredient` to `optional`.
- **Sazerac & Mint Julep:** Downgraded `Water` rows from required `ingredient` (`ingredient_name='Water'`) to `optional` (`ingredient_name=NULL`).
- **Dry Rob Roy:** Promoted `Angostura bitters` from `optional` to required `ingredient` (matching `Rob Roy` and its own note).
- **Martinez:** Renamed `'Martinez 2'` -> `'Martinez'` in DB, `about_text.py`, and `enhance_text.py`.

**App & UI bug bundle:**
- *Login copy (`0949ece`):* Removed remaining `"Sign up with an invite code"` copy in `templates/login.html` -> `"Create an account"`.
- *Mixers autosave race & HTML overhead (`templates/my_bar.html`, `app.py`):* Serialized `POST /checklist` `fetch` calls with an `inFlight` + `pending` queue and `X-Requested-With: fetch`; `/checklist` now deduplicates ids and returns `{"ok": true, "stocked_count": N}` JSON instead of redirecting/rendering full HTML.
- *Apostrophe casing (`templates/my_bar.html`):* Dropped `|title` on ingredient labels (`Peychaud'S Bitters` -> `Peychaud's bitters`).
- *Split-base missing row hint (`templates/recipe.html`):* Checked `{% if is_missing %}` before `{% elif bottle_hints.get(i.id) %}` so an unfilled second whiskey slot shows `Missing from bar` rather than contradicting itself with `Use your: ...`.
- *Manual `/add` vs scan redirect (`app.py`, `templates/confirm_bottle.html`):* Manual bottle adds on `/bar` stay on `/bar` even when `stocked_count == 0`; only `from_scan=1` (`confirm_bottle.html`) and `/confirm-bulk` redirect 0-mixer users back to `/` for Quick Kitchen Check.
- *Tonight cap, scan credit safety, spotlight casing & `sqlite3.Row` (`app.py`, `matching.py`):* Raised `home()` `max_makeable` `60 -> 200`; moved `log_scan()` in `/scan` and `/scan-bulk` after successful API identification (`error` / empty parse no longer burns daily scan slots); upgraded lowercase `build_one_away_spotlight()` group labels to title case when seen; fixed `recipe_image_url()` to use `recipe.keys()` so raw `sqlite3.Row` works; removed dead `ingredient_slug()`, `get_ingredient_images()`, and unused `ingredient_have` in `recipe()`.
- *Disliked thumbnails (`templates/saved.html`):* "Not for me" accordion now renders recipe photos with fallback glass SVG instead of glass SVG only.

**QA image audit finding (saved as Backlog #20 for next session):**
- **0 byte-identical files, 0 duplicate resolved URLs, 0 missing images, 0 orphan WebPs** across all 171 recipes (`98` local WebPs + `73` CocktailDB URLs) and `39/51` ingredient photos (`0` duplicate ingredient photos; `12` ingredients without photos aren't displayed since the My Bar redesign dropped ingredient tile photos).
- **However, 94/98 local WebPs share ~5 recycled base studio backdrops** (`74` share the angled dark-wood scene; `11` share brass-rail + candle), producing visual near-twins at card size (`affinity` ↔ `greenpoint`, `adonis`/`harvard`/`bamboo`/`old_pal`, `dirty_martini` ↔ `gibson`, `cardinale` ↔ `milano_torino`, `bees_kiss` ↔ `mary_pickford`, `brooklyn`/`camerons_kick`/`rob_roy`/`remember_the_maine`, `algonquin` ↔ `brown_derby`, `mamie_taylor` ↔ `scotch_highball`).

**Verified:**
- `migrate_qa_specs_2026_11.py` ran cleanly and idempotently on both `bomu.db` and live Neon Postgres (`--postgres --commit`; 12 actions -> 0 on re-run).
- `check_specs.py` (`FORCE_SQLITE=1`): `171 recipes checked, 0 with at least one flag`.
- `sweep_namematch.py` (`FORCE_SQLITE=1`): `0 BROKEN, 6 REVIEW`.
- `match_recipe()` vs `missing_ingredient_ids()` parity: `0` mismatches across all 5 users × 171 recipes.
- Extended `verify_routes.py` (`FORCE_SQLITE=1`): all routes + `171/171` recipe pages pass (including `recipe_image_url(sqlite3.Row)`, `POST /checklist` `X-Requested-With: fetch` JSON, `Peychaud'S Bitters` absence, manual vs `from_scan=1` redirects).
- Authoritative live Neon read (`backend: postgres`, `recipes: 171`, `Martinez` id=9):
  - `aaron`: `34/70` (`spot=Grapefruit juice`, unchanged)
  - `Avishka` & `Rajapaksha`: `0/0`
  - `lenasheh` (Shehan): `0/14 -> 0/13` (`Dry Rob Roy` now honestly requires `Angostura bitters`; `kitchen_check` still 10 picks unlocking up to `21` drinks)
  - `Maho`: `1/13` (unchanged)

**Pick up next session:**
1. **Regenerate near-twin recipe WebPs + check 73 CocktailDB URLs (`#20`).**
2. **Security chore (`#17`):** Aaron to delete `step_88.json` log and rotate Neon password.
3. **Remaining backlog (`#5` rum/gin/sherry sub-types, `#7` ambiguous bottle prompts, `#8` checklist label & cream/cherry cleanup, `#13` Sazerac base, `#18` optional Porkbun DNS).**

### 2026-11-20 — Backlog cleanup, #8 Mixers checklist overhaul & #20 recipe photo refresh (Antigravity)

Audited the 20-item backlog against the codebase and `bomu.db`, pruned completed/redundant items and stale context in `CLAUDE.md`, shipped `#8` across both local `bomu.db` and live Neon Postgres, and shipped `11/13` photo regenerations + `73/73` remote URL checks for `#20` to `origin/main` after Aaron previewed locally.

**Backlog & doc cleanup (`CLAUDE.md`, `matching.py`):**
- Pruned 12 completed/merged items (`#1`–`#4`, `#6`, `#9`, `#11`, `#12`, `#14`–`#16`, `#19`) and 4 redundant/moot items (`#7` legacy generic bottles no longer exist except Japanese blend Nikka; `#10` catalog growth already settled; `#13` Sazerac base settled; `#18` optional Porkbun DNS already working). Trimmed "gin / sloe gin" from `#5`. Left `#17` untouched.
- Updated the 4 stale context sections (`bomu.db` vs `bomu_live.db`, Neon `recipe_enhancements` constraint parity, removal of `static/ingredients/` / `ingredient_slug()` from rename steps, word-boundary `_liqueur_keys()`), and removed dead `NOISE_WORDS` constant in `matching.py`.

**`#8` Mixers checklist overhaul (`migrate_checklist_2026_11.py`, `database.py`, `suggestions.py`, `bomu.db`, Neon Postgres):**
- Removed unused `Water` (0 required recipes; cleared 2 `user_stock` ticks); kept `Maraschino cherries` so the 8 `recipe_enhancements` tags keep working. Checklist `51 -> 49` rows on both SQLite and Neon.
- Merged `Light Cream` -> `Heavy cream` (portable `user_stock` tick transfer + `recipe_ingredients`/`recipe_enhancements` repoint + delete).
- Normalized 12 checklist labels (`Coconut cream` -> `Cream of coconut` plus sentence casing across Title Case items), clarified `Pina Colada`'s coconut note (`Coco López`), fixed 10 misplaced `ingredients.category` buckets, and updated `Moscow Mule` from `Ginger ale` -> `Ginger beer` (ingredient row + step 3).
- Updated `SEED_INGREDIENTS` in `database.py` (`Cream of coconut` in `auto`, `Heavy cream` in `pantry`) and added `"cream of coconut"` in `suggestions.py`.
- `migrate_checklist_2026_11.py --postgres --commit` executed 41 actions cleanly and re-ran idempotently (`0` planned actions).

**`#20` Recipe photos (`static/recipes/*.webp`, `static/sw.js`):**
- Probed all `73/73` TheCocktailDB `image_url` values over HTTPS (`HEAD` / `GET` fallback): **`73/73` HTTP 200 (`image/*`)**, `0` broken.
- Regenerated and visually inspected `11/13` near-twin local WebPs (`480x480` RGB WebP): `old_pal`, `bamboo`, `harvard`, `vermouth_cocktail`, `greenpoint`, `camerons_kick`, `rob_roy`, `gibson`, `mary_pickford`, `milano_torino`, `brown_derby` (distinct glasses, surfaces, angles, and zero recycled brass-rail/candle props). Bumped `CACHE_VERSION` to `bomu-v9` in `static/sw.js`.
- **Quota hit on final 2:** `mamie_taylor.webp` and `woo_woo.webp` failed with `429 RESOURCE_EXHAUSTED` on `gemini-3.1-flash-image` (quota resets `2026-11-20T20:00:45Z`). Pairwise RMSE check across all 98 WebPs dropped `< 18` twin pairs from 6 clusters / 14 files down to 1 (`harvard` ↔ `vermouth_cocktail` at 16.2, visually distinct cut-crystal walnut vs smooth glass on linen coaster).

**Verified:**
- Local (`FORCE_SQLITE=1`): `check_specs.py` `171` checked / `0` flags; `sweep_namematch.py` `0 BROKEN, 6 REVIEW`; `verify_routes.py` (both `bomu.db` and `--db bomu_live.db`) all routes + `171/171` recipe pages pass; `match_recipe()` vs `missing_ingredient_ids()` `0` mismatches across 5 users × 171 recipes; rendered `/bar?tab=mixers`, `Moscow Mule`, `Pina Colada`, `get_suggestions('Cream of coconut')`, and `171/171` image inventory.
- Authoritative live Neon read (`backend: postgres`, `recipes: 171`, `ingredients: 49`, `bottles: 35`):
  - `aaron`: `34/70 -> 35/69` (`Moscow Mule` unlocked by `Ginger beer` tick; `18/49` mixers ticked after removing `Water`; spotlight `vermouth_dry`, 6 drinks)
  - `Avishka` & `Rajapaksha`: `0/0`
  - `lenasheh` (Shehan): `0/13` (`3/49` mixers ticked after removing `Water`; spotlight `Amaretto`, 2 drinks)
  - `Maho`: `1/13` (`12/49` mixers ticked; spotlight `Lemon juice (fresh)`, 2 drinks)

**Open / next:**
1. Optionally regenerate `mamie_taylor.webp` & `woo_woo.webp` (`#20`) after `2026-11-20T20:00:45Z`.
2. Security chore (`#17`): Aaron to delete `step_88.json` log and rotate Neon password.
3. Remaining backlog (`#5` rum and sherry sub-types).

### 2026-11-20 (second session) — Copy overhaul: About, Worth knowing tips & Make it your own (Antigravity)

**Changes made:**
- **About & Worth knowing (`about_text.py`):** Rewrote all `171` `recipes.about` entries and `125` `recipes.tip` entries (`46` recipes remain tipless) in plain, conversational bartender prose: removed all em-dashes/en-dashes (`0` remaining across all copy), stripped menu-copy fluff (`crisp`, `bright`, `silky`, `velvety`, `lively`, `sunny`, `ruby`, `plush`, `magic`, `effortless`, `timeless`, `sleek`, `unapologetically`, `art form`), eliminated fragment `"Ingredient list — tagline"` and repetitive past-participle (`Named/Born/Created/...`) openings, and kept facts grounded.
- **Make it your own (`enhance_text.py`, `templates/recipe.html`):** Audited and pruned `recipe_enhancements` from `106` rows down to `57` genuinely additive riffs across `55` recipes (`116` recipes omit the section), rewrote all `57` notes in plain human English with `0` em-dashes, replaced `&mdash;` in the `templates/recipe.html` section subtitle with a period, contrasted paired riffs (e.g., Negroni's `Orange bitters` vs `Orange twist or slice`), and fixed Zombie copy (`four rums` -> `three rums`) and checklist links (including `5` `Maraschino cherries` links).
- **Idempotent copy migration (`migrate_copy_2026_11.py`):** Created dual-mode script (dry-run default, `--commit`, `--db`, `--postgres`) updating only `recipes.about` and `recipes.tip` and asserting zero matcher delta across all users before committing.

**Verified:**
- Local SQLite (`FORCE_SQLITE=1`): `migrate_copy_2026_11.py --commit` (`171` updates, re-run `0` planned), `migrate_enhancements.py --commit` (`57` rows across `55` recipes, `0` skipped warnings, re-run `0 new / 57 present / 0 stale`), `0` dashes across all `353` copy blocks + `templates/recipe.html`, `check_specs.py` (`171` checked / `0` flags), `sweep_namematch.py` (`0 BROKEN, 6 REVIEW`), `verify_routes.py` (all routes + `171/171` recipe pages pass).
- Authoritative live Neon (`--postgres`): `migrate_copy_2026_11.py --postgres --commit` (`171` updates) and `migrate_enhancements.py --postgres --commit` (`57` rows across `55` recipes). Live Neon read confirmed `about=171/171`, `tip=125`, `recipe_enhancements=57` across `55` recipes, `0` em/en-dashes in `recipes` or `recipe_enhancements`, and unchanged matcher counts (`aaron 35/69`, `Avishka 0/0`, `Rajapaksha 0/0`, `lenasheh 0/13`, `Maho 1/13`).

**Open / next:**
1. **Start next session with self-critique + alignment questions on `#21` (personality pass on `about_text.py` & `enhance_text.py`):** review where the de-AI pass overcorrected into dry textbook/bibliography or `"X is simply a Y made with Z"` copy, ask Aaron alignment questions on voice/wit, and rewrite while keeping `0` em-dashes and `0` AI menu fluff.
2. Regenerate the final 2 `#20` WebPs (`mamie_taylor.webp` & `woo_woo.webp`, quota resets `2026-11-20T20:00:45Z`).
3. Security chore (`#17`): Aaron to delete `step_88.json` log and rotate Neon password.
4. Remaining backlog (`#5` rum and sherry sub-types).

### 2026-11-20 (third session) — #21 Bartender-voice pass, standard garnishes moved to optional recipe rows & UI copy critique (Antigravity)

Reviewed the live copy critique with Aaron and aligned on four decisions:
1. For drinks without a major origin story, focus on mood, occasion, and *why* it works in the glass.
2. Drop dry bibliography/publication-year openings (`1862 Jerry Thomas`, `1930 Savoy`, `1922 MacElhone`, `1914 Straub`, `1939 Baker`, `1974 Mr. Boston`) unless there is a great quote or story attached.
3. Give the copy a bit more point of view and dry bartender wit while keeping `0` em-dashes and `0` menu fluff.
4. Move standard classic garnishes out of "Make it your own" (`enhance_text.py`) into the recipes themselves as `optional` rows in `recipe_ingredients` (which render at soft opacity `0.84` with the `optional` badge and never affect makeability) plus explicitly optional final-step phrasing (`"...if you have one"` / `"...if you like"`). Reserve `enhance_text.py` strictly for real bartender riffs.

**Changes made:**
- **Bartender-voice pass (`about_text.py`):** Rewrote `51` `about` entries to replace bibliography citations and mechanical `"X is simply a Y made with Z"` definitions with warm, opinionated bartender prose focused on flavour, mood, and occasion (`0` em/en-dashes).
- **Standard garnishes moved to `optional` recipe rows (`migrate_copy_2026_11.py`):** Added `35` `optional` garnish rows across `30` classic recipes (e.g., `Negroni`, `Old Fashioned`, `Daiquiri`, `Hemingway Daiquiri`, `Moscow Mule`, `Mint Julep`, `Penicillin`, `Bramble`, `Clover Club`, `Corpse Reviver #2`, `The Last Word`, `Mai Tai`, `Jungle Bird`, `Zombie`, `Gold Rush`, `Brandy Sour`) and updated their final instruction step so every row is covered and clearly phrased as optional.
- **Pruned & sharpened `enhance_text.py`:** Pruned `recipe_enhancements` from `57` rows down to `24` genuine bartender riffs across `23` recipes (orange bitters riffs, Pink G&T, flamed orange twist on Cosmopolitan, orange twist on Black Russian/Godfather/French Connection, grated dark chocolate on Grasshopper, grated nutmeg on Irish Coffee/Planter's Punch/Toasted Almond, crushed Oreo rim on Oreo Mudslide, celery salt & cracked pepper on Bloody Mary, orange flower water drop on Ramos Gin Fizz).
- **Stale UI count fix (`templates/tonight.html`):** Updated Quick Kitchen Check link from `"All 51 mixers →"` to `"All 49 mixers →"` to match the 49-item checklist after `#8`.
- **UI writing & micro-copy polish (`app.py`, `templates/tonight.html`, `templates/one_away.html`, `templates/saved.html`):**
  - Added a 1-line clamped `.featured-teaser` on Tonight's Featured Pour hero card showing the opening sentence of `featured.recipe.about`.
  - Dropped the redundant `"Ready ·"` prefix on every drink card inside Tonight's Ready section (keeping `"Ready ·"` on mixed-status lists in Explore and Saved).
  - Tightened `SPOTLIGHT_LINES[0]` in `app.py` to `"One {unit} stands between you and {drink}."`.
  - Updated `/one-away` type label from `"Mixer / Ingredient"` to `"Kitchen / Mixer"`, and warmed up `/saved`'s empty state (`"Nothing on your tab yet"` / `"Tap 'Like' on any cocktail you mix to keep your go-to pours ready here."`).

**Verified:**
- Local SQLite (`FORCE_SQLITE=1`): `migrate_copy_2026_11.py --commit` (`51` about edits, `35` optional rows, `30` step updates; 0 matcher delta), `migrate_enhancements.py --commit` (`24` rows across `23` recipes), `0` em/en-dashes across all `recipes` and `recipe_enhancements`, `check_specs.py` (`171` checked / `0` flags), `sweep_namematch.py` (`0 BROKEN, 6 REVIEW`), `verify_routes.py` (all routes + `171/171` recipe pages HTTP 200 on both `bomu.db` and `--db bomu_live.db`).
- Live Neon Postgres (`--postgres --commit`): `migrate_copy_2026_11.py --postgres --commit` and `migrate_enhancements.py --postgres --commit` ran cleanly; matcher counts verified unchanged (`aaron 35/69`, `Avishka 0/0`, `Rajapaksha 0/0`, `lenasheh 0/13`, `Maho 1/13`).

**Open / next:**
1. Regenerate the final 2 `#20` WebPs (`mamie_taylor.webp` & `woo_woo.webp`, quota resets `2026-11-20T20:00:45Z`).
2. Security chore (`#17`): Aaron to delete `step_88.json` log and rotate Neon password.
3. Remaining backlog (`#5` rum and sherry sub-types).

### 2026-11-20 (fourth session) — Complete #20 recipe photos & 6-item visual polish bundle (Antigravity)

Completed the remaining 2/13 recipe studio WebP regenerations for Backlog `#20` (`mamie_taylor.webp` & `woo_woo.webp`, closing `#20`), plus a 6-item visual consistency pass across icons, hero framing, `/one-away`, secondary forms, and mixers UI.

**Changes made:**
- **Regenerated `static/recipes/mamie_taylor.webp` & `static/recipes/woo_woo.webp` (`480x480` RGB WebP):** Replaced the diagonal-wood near-twins of `scotch_highball.webp` and `cape_codder.webp` with distinct studio highball shots on dark slate against matte espresso backdrops (ribbed highball + rim lime wedge for Mamie Taylor; faceted Collins + slate coaster + frothy shaken ruby-coral liquid + dropped-in lime wedge for Woo Woo).
- **Espresso & Zest app icons (`static/icon-512.png`, `static/icon-192.png`, `static/icon-180.png`, `templates/base.html`):** Replaced the pre-redesign hot-pink/navy martini favicons with supersampled (`2048x2048` LANCZOS) Espresso (`#140e0a`) & Zest (`#f4c430`) coupe emblem icons matching `manifest.json` and `icons.html`, and cache-busted icon links (`?v=2`) in `base.html`.
- **Hero framing & CocktailDB brightness consistency (`templates/recipe.html`, `templates/tonight.html`, `templates/base.html`):** Raised mobile `.recipe-hero-media` from `140px` to `230px` with `object-position: center 38%` and softened top scrim fade; switched `.recipe-hero` to a square `200px` 2-column layout at `520px+` (`250x220` at `768px+`); added `object-position: center 38%` to Tonight's Featured Pour & One Away tiles; enlarged mobile `.onboard-media` (`136px -> 168px`, `center 58%`, corrected `alt` text); extended `.drink-thumb img[src^="http"]` dark-surface brightness/contrast filter to `.featured-hero-img`, `.oneaway-img-wrap img`, and `.recipe-hero-media img`.
- **`/one-away` visual parity (`templates/one_away.html`):** Replaced `999px` pill drink links with compact `42x42` photo thumbnail rows (`.oa-drink-row` with glass fallback, condensed uppercase title, and glass label), and converted "Unlocks 1 Drink" `<details>` blocks to `.accordion-bar` with `chevron-down` disclosure icons.
- **Secondary form pages & Back links (`templates/base.html`, `add_bottle.html`, `edit_bottle.html`, `scan.html`, `scan_bulk.html`, `confirm_bottle.html`, `confirm_bulk.html`, `one_away.html`):** Added `.back-link` text style replacing inline `999px` Back chips, and wrapped all six form pages in `.form-page-narrow` (`max-width: 520px` on desktop).
- **Mixers button & remaining UI em-dashes (`templates/my_bar.html`, `add_bottle.html`, `edit_bottle.html`, `confirm_bottle.html`, `confirm_bulk.html`, `static/sw.js`):** Moved the redundant `"Save mixers"` submit button inside `<noscript>` (auto-save toast remains active for JS), replaced visible `&mdash;` in select placeholders, low-confidence pills, and `sw.js` offline fallback copy, and bumped `static/sw.js` `CACHE_VERSION` from `"bomu-v9"` to `"bomu-v10"`.

**Verified:**
- Visual inspection of regenerated `mamie_taylor.webp`, `woo_woo.webp`, `icon-512.png`, `icon-192.png`, and `icon-180.png`.
- Pairwise `32x32` RGB RMSE checks: `mamie_taylor` vs `scotch_highball` = `48.3`, `woo_woo` vs `cape_codder` = `58.6`, `0` pairs across all `98` local WebPs `< 18.0`, and `171/171` recipes resolve to valid image targets.
- Zero remaining visible `&mdash;` / `—` across all `templates/**/*.html` and `static/sw.js`.
- `venv\Scripts\python.exe verify_routes.py` and `verify_routes.py --db bomu_live.db`: all routes + `171/171` recipe pages pass (`171 ok, 0 failed`).

**Open / next:**
1. Security chore (`#17`): Aaron to delete `step_88.json` log and rotate Neon password.
2. Remaining backlog (`#5` rum and sherry sub-types).

### 2026-11-21 — Performance/serverless DB caching, rotating Featured Pour + one-tap stocking, public Explore/Recipes & hardening (Antigravity)

Reviewed the full app objectively (`B+`, `85/100`) and implemented all three recommended improvements in one pass:

**1. Serverless DB connection reuse, catalog caching & dead asset cleanup (`database.py`, `matching.py`, `app.py`, `static/`):**
- Added request-scoped DB connection pooling (`_RequestConnProxy` on `flask.g`, closed via `@app.teardown_appcontext` -> `close_request_db()`) in `database.py`, dropping warm `GET /` on Neon from 6–7 remote Postgres handshakes down to `1` connection.
- Added a 300-second TTL + SQLite mtime-aware catalog cache (`_get_ingredient_catalog()`, `_get_recipe_catalog()`, `invalidate_catalog_cache()`) for read-only `recipes`, `recipe_ingredients`, `recipe_enhancements`, and `ingredients`, returning fresh outer wrapper dicts on `get_all_recipes()` / `get_recipe()` so per-user `your_bottles` annotations never leak across requests.
- Eliminated duplicate user queries in `home()` (reusing `recs["bottles"]` and `recs["ingredients"]`) and `bar()` (passing `ingredients=` to `get_auto_added_ingredients()`), and replaced per-call `os.path.isfile()` probing in `recipe_image_url()` with a process-cached `_recipe_image_map()`.
- Removed `44` unused tracked legacy static files (`39` in `static/ingredients/` + `static/auth-login.jpg`, `static/auth-signup.jpg`, `static/hero-cocktail.jpg`, `static/beach-bar-diorama.webp`, `static/beach-bar-sunset.webp`), cutting `static/` from `7.90 MB` (`153` files) to `2.27 MB` (`109` files).

**2. Daily-rotating Featured Pour & one-tap stocking (`app.py`, `matching.py`, `templates/one_away.html`, `templates/recipe.html`):**
- Replaced Tonight's frozen `pool[0]` hero selection with `pick_featured_pour()` using deterministic per-user cycle permutations with boundary collision swapping so Tonight cycles cleanly through eligible makeable pours daily with zero consecutive repeats.
- Extended `POST /stock-add` with `_safe_next()` `next` redirect support and ingredient-ID validation, extended `matching.get_one_away_grouped()` with `ingredient_id` / `bottle_type` / `name_matched`, and wired `"I have this"` / `"Add to my bar"` buttons directly onto `/one-away` cards/accordions and missing rows in `/recipe/<id>`.

**3. Public read-only `/explore` & `/recipe/<id>` + hardening (`app.py`, `templates/base.html`, `explore.html`, `recipe.html`, `login.html`, `signup.html`, `static/sw.js`):**
- Opened `GET /explore` and `GET /recipe/<id>` to logged-out visitors (`0` user queries, no personal bar state leaked, topbar `Log in · Sign up`, recipe `og:title` / `og:description` / `og:image` / `og:url` metadata, `"Match my bar"` dock CTAs, and `"browse all 171 cocktails"` link on `/login` and `/signup`).
- Added fail-fast `SECRET_KEY` check when `VERCEL` is set, `MAX_CONTENT_LENGTH = 10 MB` + friendly `413` redirect handler, sliding-window per-IP rate limiting on `POST /login` (`15 / 10 min`) and `POST /signup` (`8 / 10 min`), deduplicated `SCANNER_CLASSIFICATION_RULES` across single/shelf vision prompts, and bumped `static/sw.js` `CACHE_VERSION` to `"bomu-v11"`.

**Verified:**
- Extended `verify_routes.py` (testing public `/explore` + `/recipe/<id>` OG tags, auth redirects, `/one-away` & `/recipe/<id>` one-tap actions, `POST /stock-add` `next=` & open-redirect guard, `<= 1` DB connection on warm `GET /`, catalog cache mutation isolation, and 14-day `pick_featured_pour()` rotation); passes cleanly on both `bomu.db` and `--db bomu_live.db` (`171 ok, 0 failed`).
- `check_specs.py` (`171` checked / `0` flags) and `sweep_namematch.py` (`0 BROKEN, 6 REVIEW`).
- Live Neon Postgres read (`backend: postgres`): verified all 5 accounts (`aaron 25/77`, `Avishka 0/0`, `Rajapaksha 0/0`, `lenasheh 0/13`, `Maho 1/13`).

**Open / next:**
1. Security chore (`#17`): Aaron to delete `step_88.json` log and rotate Neon password.
2. Remaining backlog (`#5` rum and sherry sub-types).

### 2026-11-21 (second session) — CLAUDE.md split into current state + docs/session-log.md (Claude Code)

`CLAUDE.md` had grown to 107 KB / 1,491 lines, 69% of it dated session history,
and every Claude Code and Antigravity session loaded all of it at startup. Docs
only: no app code or data changed.

**Changed:**
- New `docs/session-log.md`: all 28 dated entries moved word for word, oldest
  first, plus the two dated blocks from `## Where things stand` (the 2026-07-29
  commits and the 2026-11-15 summary) filed by date. An archive at its top keeps,
  word for word, every current-state paragraph that was moved out or reworded.
- `CLAUDE.md` rewritten as current state only, with copies of the newest 2
  entries under `## Recent sessions`. Section names that code comments and old
  entries cite (Gotchas, Adding recipes, The matcher, Verification, Templates,
  Scanner, Data model, Running it, Deploy sequence) are unchanged.
- Lessons that lived only in the log were folded into `## Gotchas` and their
  sections, a line or two each, after checking each against the code.
- `## Session handoff protocol` and `AGENTS.md`: at close, append the entry to
  the bottom of `docs/session-log.md`, refresh `## Recent sessions`, update the
  current-state sections, keep `CLAUDE.md` under ~30 KB.

**Claims that had decayed, corrected while checking them against the code:**
- No template uses `|safe` any more (the file said two uses remained).
- `BOTTLE_TYPE_CHOICES` feeds five templates, not four. The scanner prompts now
  share `SCANNER_CLASSIFICATION_RULES` but each still lists the types, so a new
  type needs both prompts as well.
- The spotlight rotates daily across the top 4 blockers (undocumented), and
  `build_onboarding_data()` plus `canFillSlots` in `tonight.html` are a third and
  fourth copy of the distinct-bottle logic.
- `check_specs.py` and `sweep_namematch.py` read local `bomu.db` only; "safe on
  the server" dated from PythonAnywhere.

**Gotcha found:** a Claude Code worktree (`.claude/worktrees/*`) has no `.env`,
but `load_dotenv()` walks up and finds the main checkout's, so the app and the
matcher run from a worktree read **live Neon**. `verify_routes.py` stays on
SQLite regardless, because `_pg_url()` ignores `DATABASE_URL` once `DB_PATH` is
overridden.

**Open item recovered:** "audit Neon for other constraints lost in the Postgres
migration" (2026-11-15, seventh session) was never closed; only
`recipe_enhancements` was fixed on 2026-11-19. Now backlog #22.

**Verified:** a script checked that all 300 paragraphs of the old `CLAUDE.md`
exist word for word in the new `CLAUDE.md` or the log, that every dated entry
appears exactly once and in order, and that no secret-like strings were added.
Pushed to `main` on Aaron's go-ahead.

**Open / next:**
1. Security chore (`#17`): Aaron to delete the `step_88.json` log and rotate the
   Neon password.
2. `#22` Neon constraint audit; `#5` rum and sherry sub-types.
3. Stale code comments left alone in a docs-only session: `verify_routes.py`,
   `migrate_enhancements.py` and `sweep_namematch.py` still call `bomu.db`
   stale, and `app.py`'s `__main__` comment still says production runs gunicorn.
