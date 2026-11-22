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
users on 0. **Nobody but Aaron has added, scanned or rated anything since
2026-07-24**, and nobody has signed up since signup opened (2026-11-19).
Visits aren't recorded (#23). **Read user counts from Neon:** `bomu.db` matches its catalog, not
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
- **Vercel rejects request bodies over 4.5 MB** with its own bare 413 page,
  before Flask runs. Any upload path must shrink files in the browser first
  (see Scanner).
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
`add_ingredients_to_stock()`, which only adds. The Mixers page autosaves one
tick per request through `POST /checklist/item` (`set_ingredient_stock()`),
answers JSON with the real count, and puts the box back with an error if the
save fails. `set_all_ingredients_stock()` wipes the user's checklist first and
is only for the no-JavaScript `/checklist` submit: never send a whole page's
checklist from code that can run on a stale page (it used to, and unticked
items added elsewhere). Signed-out requests sent with
`X-Requested-With: fetch` get a 401 JSON answer, not a login redirect.

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
prompts, and `FUNGIBLE_TYPES` if fungible.

Every scan Claude answers counts against the caps (`log_scan()`), identified
or not, because it was billed; one that raises (unreadable file, API down)
doesn't. Replies go through `_parse_scan_json()`, which never raises.

**Photos are shrunk in the browser** (`components/photo_upload.html`, 1568 px
JPEG to match `prepare_image()`, EXIF rotation applied) because Vercel refuses
uploads over 4.5 MB and phone photos are often bigger. `MAX_CONTENT_LENGTH` is
4 MB, so anything that skips the shrink (no JavaScript) gets the app's own
message. `verify_routes.py` `check_scanner()` covers all of this with a fake
Claude client.

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
23. **Record when users last open the app.** Only writes are recorded, so
    there's no telling whether friends use Bomu. `last_seen_at` on `users`,
    written at most once a day per user by a fail-safe `before_request` hook
    (code may deploy before the Neon migration), plus a read-only report script.
24. **Check before deploying.** Every push to `main` goes to production
    unchecked; `verify_routes.py` takes ~3 s. A tracked pre-push hook
    (`core.hooksPath`) or a GitHub Action.
25. **Small findings from the 2026-11-21 review.** Recipe rows repeat the name
    in the note line ("Campari / Campari"); My Bar's tab reads "Mixers ( 15/49 )"
    with stray spaces; "Surprise me", "Add to my bar" and "out" are 36-40 px
    tall; TheCocktailDB images load at 700 px for ~150 px tiles; a scanned
    Prosecco or wine bottle is an `other` bottle and never satisfies the
    Prosecco/Champagne/wine checklist rows (affects no one today); login and
    signup rate limits live in process memory, so they're per Vercel instance.

---

## Recent sessions

Copies of the newest 2 entries; every entry, oldest first, is in
[`docs/session-log.md`](docs/session-log.md).

### 2026-11-21 (third session) — App review, then the scanner fixed for phone photos (Claude Code)

Asked for an objective review with a grade and 3 improvements. Graded **B−
(about 80/100)**: matcher and catalog A, design A−, code B, security and
reliability B−, "is it working for the friends" D.

**Evidence (live Neon, read only):** nobody but Aaron has added a bottle,
scanned or rated since 2026-07-24; all 4 ratings are Aaron's, from April; no
signups since signup opened on 2026-11-19; Avishka and Rajapaksha have never
added anything. Visits aren't recorded, so whether friends open the app is
unknowable. Shehan ticking 6 basics (lemon, lime, simple syrup, soda water,
sugar, Angostura) would take him from 0 to 9 ready.

**Improvements:** (1) scanner with phone photos, done below; (2) get the
friends back and record visits: last-seen tracking proposed as its own task,
not started (backlog #23); (3) slim `CLAUDE.md`, done in the second session.

**Bug found:** Vercel rejects request bodies over 4.5 MB before Flask runs. On
live, a 5.2 MB logged-out POST to `/scan` got Vercel's bare
`FUNCTION_PAYLOAD_TOO_LARGE` page; 3 MB reached Flask. The scan forms send the
camera's full-size photo and `MAX_CONTENT_LENGTH` was 10 MB, so the friendly
413 message could never fire. Broken since the move to Vercel; unnoticed
because nobody has scanned since July.

**Changed (`842942b`):**
- `templates/components/photo_upload.html` (used by `scan.html` and
  `scan_bulk.html`) shrinks the photo in the browser to a 1568 px JPEG, the
  size `prepare_image()` uses, with EXIF rotation applied. A file over 4 MB it
  can't shrink gets an inline message instead of an upload.
- `MAX_CONTENT_LENGTH` 10 MB -> 4 MB.
- `log_scan()` runs for every scan Claude answers, identified or not; one that
  raises (nothing billed) doesn't count. An unreadable photo now uses one of a
  user's 15 daily scans; before, junk photos could run up the API bill under
  the caps.
- Replies parsed without raising (`_parse_scan_json()`). A shelf scan that
  found nothing rendered "Found 1 bottle" above an empty card; it now says
  nothing was found.
- `verify_routes.py` `check_scanner()`: both scan routes with a fake Claude
  client (no API calls). 5 of its checks fail against the old `app.py`.

**Verified:** `verify_routes.py` on `bomu.db` and `--db bomu_live.db`. In the
in-app browser (Chromium) on a scratch copy with a fake client: an 11.8 MB
EXIF-rotated photo arrived as 785 KB, 1176x1568 and upright; a 5 MB file the
browser can't decode showed the inline message and uploaded nothing. Pushed to
`main` with the `CLAUDE.md` split. **Not verified:** a real phone on live.

**Open / next:**
1. Scan once from a real phone on www.bomu.lol (iPhone Safari matters most).
2. `#17` rotate the Neon password, open since 2026-11-15.
3. `#23` last-seen tracking, then nudge each friend with their own unlock.
4. `#24` pre-push check; `#25` small findings from the review.

### 2026-11-21 (fourth session) — Second review, then Mixers autosave fixed (Claude Code)

Second review: still **B−, about 81/100** (code up to B+; security and
reliability still B−; "working for the friends" still D, no friend activity
since 2026-07-24). New improvements: (1) one-tap sign-in links and a password
change page, since there is no account recovery at all (running as its own
session on branch `claude/distracted-spence-fcfce8`, not merged); (2) Mixers
saving, fixed below; (3) error alerts such as Sentry (needs Aaron's account).
Also noted: no backup of Neon (snapshot with a Neon branch before migrations),
the `?` to `%s` rewrite in `database.py`, `/robots.txt` 404.

**Bugs found (reproduced on a scratch copy):** the Mixers page autosaved by
posting its whole checklist to `/checklist`, which replaced the user's ticks.
A page opened before an "I have this" tap elsewhere unticked that item on its
next save (Grenadine). Signed out, a tick showed "Saved · 17 stocked" and stored
nothing, because `fetch()` followed the login redirect to a 200 page; a dropped
connection failed silently. Enter in the filter box would submit the whole form.

**Changed:**
- `POST /checklist/item` + `set_ingredient_stock()`: one tick per request,
  JSON with the real count; unknown ids get a 400.
- `login_required`: signed-out `X-Requested-With: fetch` requests get a 401
  JSON answer instead of a redirect.
- `my_bar.html`: saves queue one at a time; a failed save puts the box back
  with "Not saved: you've been signed out." or "Not saved. Check your
  connection."; Enter in the filter no longer submits; Back reloads the page.
- `/checklist` (no-JS submit) drops junk ids instead of 500ing.
- `verify_routes.py` `check_mixers_save()`: 9 checks.

**Verified:** `verify_routes.py` on `bomu.db` and `--db bomu_live.db`; both
repros, a simulated dropped connection and Enter in the filter, in the in-app
browser at phone width; Neon's `user_stock` has the primary key
`ON CONFLICT` needs (read-only check). Pushed to `main`.

**Open / next:**
1. Merge the sign-in links branch when its session finishes (needs a Neon
   migration first, with Aaron's OK).
2. Error alerts (needs a Sentry account); `#23` last-seen tracking.
3. `#17` rotate the Neon password; scan once from a real phone.
