# Bomu

A web app for finding cocktails you can actually make from the bottles you own.
Flask + Neon Postgres (with SQLite local fallback), hosted on Vercel at https://www.bomu.lol. Built for Aaron and his friends.

Current state only. The dated history is in
[`docs/session-log.md`](docs/session-log.md).

---

## Session handoff protocol (Claude Code & Antigravity)

Shared memory between **Claude Code** (auto-loads `CLAUDE.md`) and
**Antigravity** (auto-loads `AGENTS.md` -> `CLAUDE.md`). Neither can see the
other's chats, so anything not written down is lost.

- **At session start:** read `## Where things stand`, `## Running it`,
  `## Gotchas` and `## Recent sessions` before running commands or editing code.
- **At session close ("close sesh" or wrap-up):**
  1. Append a dated `### YYYY-MM-DD` entry (what changed, why, gotchas hit, open
     items / next steps) at the **bottom** of `docs/session-log.md`.
  2. Refresh `## Recent sessions` here to copies of the newest 2 entries.
  3. Update the current-state sections in the present tense. A lesson that will
     still matter next month goes in `## Gotchas` or its section, in a line or two.
- **Keep this file under ~30 KB.** History and narrative go in the log.
- **Never write secret values** (passwords, API keys, full `DATABASE_URL`). Names only.
- **Commit and push `CLAUDE.md` and `docs/session-log.md`** with the session's work.

---

## Where things stand

Live and healthy: 171 recipes, 49 ingredients, 5 users, 34 bottles. Open
signup behind a honeypot field and per-IP rate limits (login 15, signup 8 per
10 min); scans capped at 15 per user per day and 60 shared. Logged-out visitors
can browse `/explore` and `/recipe/<id>`. `check_specs.py`: 0 flags;
`sweep_namematch.py`: 0 BROKEN.

**Counts below were read off live Neon on 2026-11-21** via
`matching.get_recommendations()`, not simulated.

| id | user | bottles | mixers ticked | makeable | one-away |
|---|---|---|---|---|---|
| 1 | aaron | 17 | 19 / 49 | 25 | 77 |
| 2 | Avishka | 0 | 0 | 0 | 0 |
| 3 | Rajapaksha | 0 | 0 | 0 | 0 |
| 4 | lenasheh (Shehan) | 16 | 3 | 0 | 13 |
| 5 | Maho | 1 | 12 | 1 | 13 |

Tonight's empty-bar onboarding and Quick Kitchen Check are aimed at the three
users on 0. **Read user counts from Neon:** `bomu.db` matches its catalog, not
its per-user tables, and `bomu_live.db` is the frozen 2026-11-15 snapshot.

**Untracked in the main checkout:** `.claude/` (preview `launch.json`, agent
worktrees) and `redesign/` (the 2026-11-14 brief and mockups). Stage files by
name; never `git add -A`.

---

## Running it

- **Live:** https://www.bomu.lol (`https://bomu.lol` 308-redirects to `www`;
  Vercel alias `https://bomu.vercel.app`).
- **Deploys:** Vercel project `sepulturian/bomu`; `vercel.json` routes every
  path to `app.py`. Every push to `main` on
  `https://github.com/sepulturian/bomu.git` deploys to production.
- **Database:** Neon Postgres project `broad-water-80207736` via
  `DATABASE_URL`; local SQLite `bomu.db` when that's unset or `FORCE_SQLITE=1`.
- **Env (names only):** local `.env` (gitignored) holds `DATABASE_URL`,
  `DATABASE_URL_UNPOOLED`, `ANTHROPIC_API_KEY`. Vercel holds `DATABASE_URL`,
  `ANTHROPIC_API_KEY`, `SECRET_KEY`, `SECURE_COOKIES` (Project Settings ->
  Environment Variables; a change needs a Redeploy).
- **`load_dotenv()` searches upward from the calling script's folder**: a
  helper in `%TEMP%` or a scratchpad silently reads SQLite, and anything run in
  a Claude Code worktree (`.claude/worktrees/*`, which has no `bomu.db` or
  `venv`) finds the main checkout's `.env` and reads **live Neon**. Print
  `database._is_postgres()` before trusting a "live" number; run DB checks from
  the main checkout.
- **DNS (Porkbun):** `A @ -> 76.76.21.21`, `CNAME www -> cname.vercel-dns.com`.
- **Legacy host:** `sepulturian.pythonanywhere.com` 301-redirects to
  `www.bomu.lol` (except `/static/`). Free tier: click "Run until 1 month from
  today" on the PA Web tab monthly or the redirect goes dark. Old WSGI file:
  `~/wsgi_before_redirect_2026-11-15.py`.

### Deploy sequence

Production deploys on every push to `main`:

```powershell
cd "C:\Users\sepulturian\Documents\Claude\projects\bomu"
git status -s                  # stage by name; leave .claude/ and redesign/ alone
git add <changed files>
git commit -m "..."
git push origin main           # triggers the Vercel production build
```

Migrations run from the laptop against Neon (the 2026-11 scripts take
`--postgres`) after a dry run and a test on a SQLite copy.

### Verification

**Check the matcher, not the browser.** A stale render once cost an hour
chasing a bottle that didn't exist. From the main checkout's root:

```powershell
venv\Scripts\python.exe -c "import dotenv; dotenv.load_dotenv(); import database, matching; print('postgres' if database._is_postgres() else 'SQLITE'); r = matching.get_recommendations(1); print(r['total_makeable'], r['total_one_away'])"
```

In a browser, add a cache-busting query string.

**Render every template before deploying template changes**; `py_compile`
passes templates that 500:

```powershell
venv\Scripts\python.exe verify_routes.py                  # against bomu.db
venv\Scripts\python.exe verify_routes.py --db copy.db     # against a migrated copy
```

It seeds a scratch copy with a user whose shelf exercises the fungible,
sub-typed and name-matched paths, then walks every route, recipe page and POST,
logged out and in. It never touches Neon (`_pg_url()` ignores `DATABASE_URL`
once `DB_PATH` is overridden). For a migration, run it on the current DB (code
must render *without* the new columns, to deploy first) and on a migrated copy.

**`check_specs.py`** (read-only on `bomu.db`; `--json`) finds rows, steps and
checklist keys that disagree. Expect 0 flags: anything else is a bug or a gap
in the checker, and a bug found by hand that it missed means it needs a rule.

**`sweep_namematch.py`** (opens `bomu.db` `mode=ro`; `--json`) asks whether
each name-matched row can ever be a substring of a real bottle name. BROKEN is
certain; REVIEW over-flags keys of 3+ words on purpose, so read it; IMPACT
counts per-user *candidates*. Baseline: 0 BROKEN, 6 REVIEW, all known false
positives.

---

## Gotchas

- **This file's claims decay.** Lines here have been false within a day of
  being written. Grep the code before trusting one.
- **`bomu.db` is current** (multi-user, Neon's catalog) since 2026-11-15.
  Docstrings calling it stale (`verify_routes.py`, `migrate_enhancements.py`,
  `sweep_namematch.py`) predate that.
- **SQLite side files can eat committed data** (a `.db-journal` rolled the
  live database back on 2026-07-23). `.gitignore` and every migration script
  refuse to run while `bomu.db-journal`, `-wal` or `-shm` exists; keep that
  guard in new scripts.
- **Verify against the consumer.** Check that an audit or query reads the
  column the code reads (see `### recipe_ingredients`). A shocking number, or
  one suspiciously equal to the snapshot, is evidence about the tool first.
- **Measure real shelves.** "Will this help?" checks read actual `user_stock`;
  assuming every mixer ticked once overestimated 5x.
- **Guard where a value is consumed, not only where it's produced**
  (`_fold()`, `safe_bottle_type()`). The same bug keeps arriving through new doors.
- **Small presentation tasks keep surfacing real bugs.** Take them and look around.
- **Rows differ by backend:** `sqlite3.Row` has no `.get()`; Neon's `_PgRow`
  is a dict. Use `row["col"]` and `"col" in row.keys()`.
- **The catalog is cached** per process for 300 s. On Neon the cache can't see
  data changes, so a catalog migration takes up to 5 minutes to reach warm
  Vercel instances. `get_all_recipes()` returns fresh outer dicts around shared
  inner objects: never mutate `recipe` or `ingredients`.
- **The service worker serves `/static/` cache-first**, so a replaced image
  keeps its old copy until `CACHE_VERSION` in `static/sw.js` is bumped
  (`bomu-v11` now).
- **A rotated Neon password** shows as `POST /login` 500 (`password
  authentication failed`) while `GET /login` is still 200. Update
  `DATABASE_URL` in Vercel, redeploy, then update `.env`.
- **Templates are cached when debug is off** (`FLASK_DEBUG=0` or a preview
  runner): restart after editing one. `python app.py` runs with debug on.
- **The laptop is Windows PowerShell 5.1:** no `&&`, no `python3` (use
  `venv\Scripts\python.exe`). Say which machine and shell a command is for.
- **Sandboxes.** Cowork can't commit (it can't remove `.git/index.lock`):
  Aaron runs `del .git\index.lock`, then commit and push, by hand. Antigravity's
  default sandbox blocks `.git`, `npm`/`npx`, network and `.env` writes; run
  those outside it.

---

## Data model

`users`, `bottles`, `ingredients`, `user_stock`, `recipes`, `recipe_ingredients`,
`recipe_enhancements`, `ratings`, `scan_log`. Users: 1 aaron, 2 Avishka,
3 Rajapaksha, 4 lenasheh (Shehan, Aaron's brother), 5 Maho.

### recipe_ingredients

Columns `id`, `recipe_id`, `raw_name`, `raw_measure`, `requirement_type`,
`bottle_type`, `ingredient_name`, `notes`, `sort_order`. `requirement_type`:

| value | meaning |
|---|---|
| `bottle_type` | needs a bottle. See matching rules below. |
| `ingredient` | matches the user's Mixers checklist by exact `ingredient_name`. Must already exist in `ingredients` (49 rows) or it can never be satisfied. |
| `optional` | garnishes, rinses, floats. Never blocks makeability. |

**`raw_name` (the product, e.g. `Pimm's No. 1`) and `ingredient_name` (a
checklist key, NULL on every `bottle_type` row) are different columns.** The
matcher reads `raw_name` for name matching (`_liqueur_satisfied`,
`match_recipe`, `missing_ingredient_ids`); `notes` is a second chance, not the
key. An audit reading `ingredient_name` on bottle rows invents a catastrophe:
35 "broken" of 84 when the truth was 1 of 87.

A `bottle_type` row with an empty `bottle_type` is silently skipped by both
functions, so a malformed import row fails open. Validate in the import script.

### recipes

171 rows; `instructions` carries a `[BOMU_REWRITTEN_v1]` marker (stripped by
`clean_instructions`) and holds **numbered steps only**: `instruction_steps()`
numbers every line, so prose there renders as a step (it did, on every recipe,
for three months). Prose goes in `about` (all 171; origin and flavour) or
`tip` (125; "Worth knowing"), from `about_text.py` keyed by recipe name.
`check_specs.py` flags violations under SHAPE. Images: 73 TheCocktailDB
`image_url`s and 98 studio WebPs at `static/recipes/<slug>.webp`;
`recipe_image_url()` prefers the local file. Every recipe has one.

**Copy rules** (also in the `about_text.py` and `enhance_text.py` docstrings):

- Nothing invented: documented origin, "contested" where sources disagree,
  flavour only where there is no real history.
- Tips are instructions that change what you do; 46 recipes have none.
- Steps name ingredients exactly as the `recipe_ingredients` rows do.
- Voice (Aaron, 2026-11-20): a bartender with a point of view and dry wit. No
  em or en dashes, no menu fluff (`crisp`, `silky`...), and no opening on a
  publication year unless a story comes with it.
- A rewrite for clarity can add facts: diff meaning against the old copy.

**`recipe_enhancements`** ("Make it your own"): 24 real riffs on 23 recipes.
Copy in `enhance_text.py`, loaded by `migrate_enhancements.py` (`--postgres` for
Neon), which refuses rows with no source, unknown checklist keys or duplicates
of the recipe, and deletes renamed rows. **The matcher never reads it.**
Standard garnishes are `optional` rows in `recipe_ingredients` instead, with
the step saying "if you have one". `source` shows as a tag, "By the book" or
"Bartender's habit".

### ingredients

Checklist labels are **shopping instructions**: the spotlight and Quick Kitchen
Check tell people to go buy them (hence `Grape Soda` -> `Grapefruit soda`,
`Coconut cream` -> `Cream of coconut`). Sentence case, printed as stored. The
checklist is non-alcoholic except `Champagne`, `Prosecco`, `Red wine` and
`White wine`; liqueurs are never checklist rows (they're name-matched bottles,
so Campari can't stand in for Cointreau).

A rename touches the `ingredients` row, `recipe_ingredients` rows
(`ingredient` and `optional`), `recipe_enhancements` rows, `user_stock` ticks
(if merging or clearing), `SEED_INGREDIENTS` in `database.py` and
`SUGGESTIONS` in `suggestions.py`. There are no ingredient photos any more.

A `user_stock` row is a tick. `/stock-add` and `/quick-setup` call
`add_ingredients_to_stock()`, which only adds; `set_all_ingredients_stock()`
wipes the user's checklist first and is for `/checklist` only.

---

## The matcher (`matching.py`)

**Fungible spirits** match by category via `FUNGIBLE_TYPES`; generic parents
accept their sub-types (`whiskey` accepts bourbon/scotch/rye/irish).

**Name-matched** types (`liqueur`, `amaro`, `other`, plus `SPECIALTY_KEYWORDS`
such as cachaca and pisco) match by substring against the bottle's name and
brand, so Campari never satisfies Cointreau. Keys come from
`_liqueur_keys(raw_name, notes)`: whole strings only (the accent-folded source,
plus one copy with brackets and `liqueur|liquor|the` stripped on word
boundaries), and a key needs 4+ characters. A row that reads like a sentence
(`Elderflower Liqueur (St-Germain)`) can never match, and `Cointreau (orange
liqueur)` yields `cointreau orange`, which no bottle contains: keep notes
short. Matching is accent-insensitive (`_fold()` on both sides).

When adding a name-matched row, check accents (`check_specs.py` still flags
them) and **brand names where a category belongs**: the Sazerac once required
`Ricard` while four anise drinks wanted `Absinthe`. `check_specs.py` knows the
anise and cherry-liqueur families; add new ones to `FAMILIES`.

### Sub-types (added 2026-07-24)

`rye`, `irish`, `vermouth_sweet`, `vermouth_dry`. Generic legacy bottles stay
**permissive** (`rye` accepts `{rye, whiskey}`, `vermouth_sweet` accepts
`{vermouth_sweet, vermouth}`), because hiding a drink someone can make is worse
than mild permissiveness. `bourbon` and `scotch` stay strict: the scanner
identifies them reliably. The Sazerac is on `rye` on purpose.

### Distinct-bottle assignment

Each deduplicated slot needs a *different* bottle (bipartite matching in
`_assign_distinct_bottles`), so one Laphroaig can't fill both halves of
Cameron's Kick. Identical requirements dedupe first, on purpose: Penicillin's
blended Scotch and Islay float are one `scotch` slot.

**Four places implement this and must change together:** `match_recipe`,
`missing_ingredient_ids` (or the recipe page highlights different rows than the
lists used), `build_onboarding_data()`, and the onboarding JS in
`tonight.html` (`canFillSlots`).

### The one-ingredient spotlight (replaced the mixer gap, 2026-11-15)

`build_one_away_spotlight()` picks the ONE mixer or bottle that unlocks the
most drinks (an exact count: every one-away recipe has one blocker) for a card
on Tonight.

- Mixers get a one-drink head start (often owned, never ticked); the 2-drink
  floor applies **before** ranking (after, it hid Shehan's only card). Rotates
  daily across the top 4. Mixers with no checklist row are skipped.
- Headline drink: liked first, never disliked if avoidable, then the lowest
  recipe id (the oldest rows are the classics).
- "I have this" POSTs to `/stock-add`; "Add to my bar" links to
  `/bar?sheet=add&type=…` (`&name=…` when name-matched; `/bar` only accepts
  `VALID_BOTTLE_TYPES`). `/one-away` and recipe pages carry the same buttons.
- Copy: `SPOTLIGHT_LINES` in `app.py`, rotated by date, built as
  `(text, is_drink)` segments so no `|safe` is needed.

Also on Tonight: 0-ready users with bottles get the Quick Kitchen Check
(`build_kitchen_check()`: up to 10 non-wine mixers by greedy set cover), empty
bars the 2-step onboarding, and the Featured Pour comes from
`pick_featured_pour()` (per-user daily rotation, never the same drink two days
running).

**Never key a template dict with a dict-method name** (`items`, `keys`,
`values`, `get`): Jinja resolves `gap.items` to `dict.items()` and the page 500s
at render, which `py_compile` can't see.

---

## Scanner

Claude vision (`claude-sonnet-4-6`); prompts inline in `app.py`
(`scan_bottle_image`, `scan_shelf_image`) share `SCANNER_CLASSIFICATION_RULES`:
RTDs, seltzers, beer and wine go to `other` (a Vodka Cruiser tagged `vodka`
once offered an alcopop Martini), sub-types only when the label is clear. Each
prompt lists the types itself, so a new type means `BOTTLE_TYPE_CHOICES`, both
prompts, and `FUNGIBLE_TYPES` if fungible. A scan counts against the caps only
once it returns a bottle.

`BOTTLE_TYPE_CHOICES` (`app.py`) feeds every bottle-type `<select>` (five
templates); add types there. Raw types shown to users go through the
`type_label` filter, and a display filter isn't done until every render site
is converted.

### Untrusted type values

`safe_bottle_type()` coerces anything not in `BOTTLE_TYPE_CHOICES` to `other`
on every write path (`/add`, `/edit`, `/confirm-bulk`); `other` is
name-matched, so it never fungibly satisfies a category. Any new `<select>` of
types needs a blank option AND that coercion: without the blank, an unreadable
scan defaulted to **Gin** and the app offered Martinis.

---

## Adding recipes

Standalone, reviewable, idempotent scripts (template:
`import_whiskey_expansion.py`): dry run by default, `--commit` to write;
validate every row against the live `ingredients` table first; one transaction,
rolled back on error; match on name so a re-run is a no-op; journal/WAL guard.
Check each spec against a named source (Difford's, IBA, Imbibe, PUNCH) and
record the URL.

Prefer existing ingredients: a new checklist row starts **unticked for every
existing user**, so its recipes stay invisible until people update their
Mixers. Justify each one in the script's docstring. Prefer recipes needing ONE
fungible spirit; drinks needing two or three name-matched liqueurs only
inflate one-away (77 deep for Aaron). Catalog size isn't the constraint:
125 -> 171 recipes bought Aaron 5 drinks when three mixer ticks would have
bought 14.

**Split migrations by expected matcher effect.** Copy and enhancement
migrations must move every user's counts by zero (`migrate_copy_2026_11.py`
asserts it); spec fixes may move them. Kept apart, each number checks its own
script.

---

## Templates

`base.html` holds the design system in one `<style>` block ("Espresso & Zest":
`--bg-base` #110d0a, `--zest` #f4c430, sage / terracotta for status, Barlow
Condensed display, Plus Jakarta Sans body). Page styling is inline; anything
used by two templates belongs in `base.html`.

**Buttons ("the pour")** are documented above `.btn` in `base.html`. `.btn` is
the ONE main action per view (solid zest, liquid fill on hover and press,
`.is-pouring` on tap); `.btn-glass` pours full on press and needs `data-label`
matching its text; `.btn-secondary`, `.btn-ghost` and `.btn-danger` are quiet.
`.btn` is `white-space: nowrap` (the glass label's dark copy only lines up on
one line), so long labels overflow. No offset shadows, all-caps, serif
buttons, gradients, glows or 999px radii on buttons (Aaron: "an AI giveaway");
chips and status pills stay rounded.

- **Words:** "Ready" means makeable, "One away" means one ingredient short.
  Tonight's stat line says "almost there" so no word-number follows a digit.
- **No `|safe` anywhere; keep it that way.** It once let a bottle named
  `<img src=x onerror=...>` run (self-XSS). Type `·`, not `&middot;`.
- **No `|title` on names:** it prints `Peychaud'S Bitters`.
- New ingredients render twice on the Mixers checklist (new group plus their
  category); JS in `my_bar.html` keeps each pair in sync.
- Safari draws its own `<summary>` marker: custom-layout summaries use
  `.bare`; the rest keep the triangle as the "this opens" cue.

---

## Backlog

*(Existing IDs preserved so references in earlier session logs stay readable.)*

5. **Rum and sherry sub-types.** Light vs aged vs Jamaican rum are not
   interchangeable, and `sherry` has no type at all: Adonis, Bamboo, and Sherry
   Cobbler sit on `other` and match by the word "sherry", so fino, amontillado,
   and cream sherry are interchangeable to the matcher. Adonis specifically says
   cream sherry will ruin it. *(Old `#12` merged in; "gin / sloe gin" removed
   2026-11-20 because 0 catalog recipes use sloe/Old Tom/Plymouth/Genever and
   scanner prompts already enforce full-strength ~30%+ ABV.)*
17. **Delete the leaked connection string and rotate the Neon password.** The
    Antigravity log `~\.gemini\antigravity\brain\179a4452-...\browser_sandbox\outputs\step_88.json`
    still exists (checked 2026-11-15) and holds the `DATABASE_URL` extracted
    during recovery. Delete it, then reset the `neondb_owner` password in the
    Neon console and update `DATABASE_URL` in Vercel (redeploy) and in local
    `.env` (`DATABASE_URL`, `DATABASE_URL_UNPOOLED`). Aaron's action.
22. **Audit Neon's other tables for constraints `migrate_to_postgres.py` lost.**
    Raised 2026-11-15; only `recipe_enhancements` was checked and fixed to match
    SQLite (2026-11-19). Compare every table's constraints and indexes with
    `database.init_db()`.

---

## Recent sessions

Copies of the newest 2 entries; every entry, oldest first, is in
[`docs/session-log.md`](docs/session-log.md).

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
Committed on a branch, not pushed (a push to `main` deploys).

**Open / next:**
1. Security chore (`#17`): Aaron to delete the `step_88.json` log and rotate the
   Neon password.
2. `#22` Neon constraint audit; `#5` rum and sherry sub-types.
3. Stale code comments left alone in a docs-only session: `verify_routes.py`,
   `migrate_enhancements.py` and `sweep_namematch.py` still call `bomu.db`
   stale, and `app.py`'s `__main__` comment still says production runs gunicorn.
