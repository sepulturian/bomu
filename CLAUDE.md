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

Live and healthy as of 2026-07-25. 171 recipes, 51 ingredients, 5 users, 35
bottles logged.

| id | user | bottles | mixers ticked | makeable | ratings |
|---|---|---|---|---|---|
| 1 | aaron | 18 | 15 / 51 | 17 | 4 |
| 2 | Avishka | 0 | 0 | 0 | 0 |
| 3 | Rajapaksha | 0 | 0 | 0 | 0 |
| 4 | lenasheh (Shehan) | 16 | 4 | 0 | 0 |
| 5 | Maho | 1 | 12 | 1 | 0 |

Just landed: the Grape Soda rename, a bug sweep (stored XSS on /recommend, the
bulk scanner silently tagging unknown bottles as Gin, raw type slugs still
leaking into My Bar), and photography on login/signup. Deployed and verified
server-side: 17 makeable / 67 one-away, unchanged, which is the point — none of
it was meant to move the numbers.

Nothing is half-finished. Next session can start clean on the backlog below.

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
things that 500 on render — that's how `gap.items` nearly shipped. The reliable
check is a scratch copy of the database plus Flask's test client walking every
route. The 2026-07-25 harness lived in the agent's scratch space and is gone;
rebuilding it took about ten minutes and caught nothing that session only because
it had already caught things during development. Worth committing as
`verify_routes.py` next time it gets written (backlog #6).

The shape that works: copy `bomu.db` to `/tmp`, add the multi-user columns the
local copy lacks, `DROP` the pre-multi-user `ratings`/`scan_log` so `init_db()`
rebuilds them, point `database.DB_PATH` at the copy **before** importing `app`,
then `test_client()` every route including the POST paths.

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
6. **Commit a `verify_routes.py`.** The render harness gets rewritten from
   scratch every session and thrown away. See the Verification section for the
   shape that works. Cheap, and it's the only thing that catches render-time
   template bugs.
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
