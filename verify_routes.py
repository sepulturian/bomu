# -*- coding: utf-8 -*-
"""Render every route against a scratch copy of the database.

WHY THIS EXISTS
---------------
`python3 -m py_compile` passes template bugs. It has to: it never renders
anything. On 2026-07-25 `{{ gap.items }}` compiled clean and would have 500'd
/recommend for every user, because Jinja resolves `.items` to `dict.items()`
before it looks for a key of that name. The only thing that catches that class
of bug is actually rendering the template.

This harness has been written from scratch and thrown away twice now (see
CLAUDE.md, Verification, and backlog #6). This is the committed version.

WHAT IT DOES
------------
1. Copies bomu.db to a scratch file so nothing here can touch real data.
2. Brings the scratch copy up to the multi-user schema, because the local
   bomu.db is stale and pre-multi-user: no user_id on bottles, no rows in
   users. See CLAUDE.md, Gotchas.
3. Seeds one user with a realistic shelf, so the makeable, one-away and
   mixer-gap paths all have something to render rather than falling straight
   through to an empty state. An empty state renders fine and proves nothing.
4. Points database.DB_PATH at the copy BEFORE importing app, which matters:
   app.py reads the path at import time.
5. Walks every route with Flask's test client, GET and POST, logged out and
   logged in, and fails on any non-2xx/3xx or any response containing a
   traceback.

USAGE
-----
    python3 verify_routes.py                  # against bomu.db
    python3 verify_routes.py --db other.db    # against a migrated copy

The --db form matters when shipping a migration: run it once against the
current database to prove the templates still render WITHOUT the new columns
(so the code can deploy before the migration runs without 500ing), then again
against a copy with the migration applied to prove they render WITH them.

Exit code 0 means every route rendered. Non-zero means at least one did not,
and the failing route and status are printed.
"""

import os
import shutil
import sqlite3
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))


def source_db():
    if "--db" in sys.argv:
        return os.path.abspath(sys.argv[sys.argv.index("--db") + 1])
    return os.path.join(HERE, "bomu.db")


# Bottles chosen to exercise the interesting matcher paths rather than to be a
# realistic bar: a fungible spirit, a sub-typed one, both vermouths, and two
# name-matched liqueurs including one that only matches on the notes field.
SEED_BOTTLES = [
    ("Beefeater", "gin", "Beefeater"),
    ("Buffalo Trace", "bourbon", "Buffalo Trace"),
    ("Rittenhouse Rye", "rye", "Rittenhouse"),
    ("Havana Club 3", "rum", "Havana Club"),
    ("Campari", "liqueur", "Campari"),
    ("Cointreau", "liqueur", "Cointreau"),
    ("Martini Rosso", "vermouth_sweet", "Martini"),
    ("Noilly Prat", "vermouth_dry", "Noilly Prat"),
    ("Benedictine DOM", "liqueur", "Benedictine"),
]

SEED_INGREDIENTS = [
    "Lemon juice (fresh)", "Lime juice (fresh)", "Simple syrup",
    "Angostura bitters", "Soda water / club soda", "Oranges", "Limes",
]


def build_scratch_db():
    """Copy the real database and bring the copy up to the current schema."""
    src = source_db()
    fd, path = tempfile.mkstemp(prefix="bomu_verify_", suffix=".db")
    os.close(fd)
    shutil.copy(src, path)
    print(f"Source database: {src}")

    conn = sqlite3.connect(path)
    cols = {r[1] for r in conn.execute("PRAGMA table_info(bottles)")}
    if "user_id" not in cols:
        conn.execute("ALTER TABLE bottles ADD COLUMN user_id INTEGER")

    # These two carry pre-multi-user rows with no user_id. Dropping them lets
    # init_db() rebuild them with the current schema instead of failing on the
    # first per-user write.
    for table in ("ratings", "scan_log"):
        conn.execute(f"DROP TABLE IF EXISTS {table}")

    conn.commit()
    conn.close()
    return path


def seed(path, username="verifyuser", password="verify-pass-123"):
    """Create one user with a shelf. Returns (user_id, username, password)."""
    from werkzeug.security import generate_password_hash

    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row

    conn.execute("DELETE FROM users WHERE username = ?", (username,))
    cur = conn.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        (username, generate_password_hash(password)),
    )
    uid = cur.lastrowid

    bcols = {r[1] for r in conn.execute("PRAGMA table_info(bottles)")}
    for name, btype, brand in SEED_BOTTLES:
        fields = ["name", "type", "user_id"]
        values = [name, btype, uid]
        if "brand" in bcols:
            fields.append("brand")
            values.append(brand)
        conn.execute(
            f"INSERT INTO bottles ({', '.join(fields)}) "
            f"VALUES ({', '.join('?' * len(values))})",
            values,
        )

    for ing_name in SEED_INGREDIENTS:
        row = conn.execute("SELECT id FROM ingredients WHERE name = ?", (ing_name,)).fetchone()
        if row:
            # user_stock has no in_stock column: the presence of the row IS the
            # tick. Writing one is how you stock an ingredient.
            conn.execute(
                "INSERT OR REPLACE INTO user_stock (user_id, ingredient_id) VALUES (?, ?)",
                (uid, row["id"]),
            )

    conn.commit()
    conn.close()
    return uid, username, password


def main():
    scratch = build_scratch_db()
    print(f"Scratch database: {scratch}")

    # Must happen before `import app`: app.py resolves the path at import time.
    sys.path.insert(0, HERE)
    import database
    database.DB_PATH = scratch
    database.init_db()

    uid, username, password = seed(scratch)
    print(f"Seeded user {uid} ({username}) with {len(SEED_BOTTLES)} bottles, "
          f"{len(SEED_INGREDIENTS)} ingredients.\n")

    import app as app_module
    app_module.app.config["TESTING"] = True
    app_module.app.config["WTF_CSRF_ENABLED"] = False

    conn = sqlite3.connect(scratch)
    recipe_ids = [r[0] for r in conn.execute("SELECT id FROM recipes ORDER BY id")]
    bottle_ids = [r[0] for r in conn.execute(
        "SELECT id FROM bottles WHERE user_id = ?", (uid,))]
    conn.close()

    failures = []

    def visit(client, method, path, label=None, **kwargs):
        label = label or f"{method} {path}"
        try:
            resp = getattr(client, method.lower())(path, **kwargs)
        except Exception as exc:
            failures.append((label, f"raised {type(exc).__name__}: {exc}"))
            print(f"  FAIL  {label}  raised {type(exc).__name__}: {exc}")
            return None
        if resp.status_code >= 400:
            failures.append((label, f"HTTP {resp.status_code}"))
            print(f"  FAIL  {label}  HTTP {resp.status_code}")
            return resp
        body = resp.get_data(as_text=True)
        if "Traceback (most recent call last)" in body:
            failures.append((label, "traceback in body"))
            print(f"  FAIL  {label}  traceback in response body")
            return resp
        print(f"  ok    {label}  HTTP {resp.status_code}")
        return resp

    print("Logged out:")
    with app_module.app.test_client() as c:
        for path in ("/login", "/signup", "/sw.js"):
            visit(c, "GET", path)
        # Public catalog browsing: /explore and /recipe/<id> render 200 without
        # personal bar data, while private routes redirect to /login.
        r_pub_exp = visit(c, "GET", "/explore", label="GET /explore (logged out)")
        if r_pub_exp:
            exp_body = r_pub_exp.get_data(as_text=True)
            if "Match my bar" not in exp_body or "Ready (" in exp_body or "cocktails" not in exp_body:
                failures.append(("public /explore", "missing public callout or leaked Ready chip"))
                print("  FAIL  public /explore assertions failed")
        if recipe_ids:
            r_pub_rec = visit(c, "GET", f"/recipe/{recipe_ids[0]}", label=f"GET /recipe/{recipe_ids[0]} (logged out)")
            if r_pub_rec:
                rec_body = r_pub_rec.get_data(as_text=True)
                if ('property="og:title"' not in rec_body
                        or 'property="og:image"' not in rec_body
                        or "Match my bar" not in rec_body
                        or "Missing from bar" in rec_body
                        or 'action="/rate/' in rec_body):
                    failures.append(("public /recipe", "missing OG tags/CTA or leaked personal bar state"))
                    print("  FAIL  public /recipe assertions failed")
        for priv in ("/recommend", "/one-away", "/bar"):
            r_priv = c.get(priv, follow_redirects=False)
            if not (r_priv.status_code == 302 and "/login" in r_priv.headers.get("Location", "")):
                failures.append((f"logged-out {priv}", f"expected 302 -> /login, got {r_priv.status_code}"))
                print(f"  FAIL  GET {priv} (logged out)")
            else:
                print(f"  ok    GET {priv} (logged out) -> /login")

        # Honeypot blocks spam signup without creating a user.
        visit(c, "POST", "/signup", label="POST /signup (honeypot ignored)",
              data={"username": "spam_bot_user", "password": "password123",
                    "confirm": "password123", "website": "https://spam.example"},
              follow_redirects=True)

        # Open signup works with no invite code and lands on 2-step onboarding.
        resp = visit(c, "POST", "/signup", label="POST /signup (open)",
                     data={"username": "verify_open_user",
                           "password": "password123",
                           "confirm": "password123"},
                     follow_redirects=True)
        if resp and "onboard-step-1" not in resp.get_data(as_text=True):
            failures.append(("open signup onboarding", "missing onboard-step-1 on /"))
            print("  FAIL  open signup missing onboard-step-1")

        # Quick-setup adds bottles + mixers and unlocks ready drinks.
        conn_q = sqlite3.connect(scratch)
        ing_rows = conn_q.execute(
            "SELECT id, name FROM ingredients WHERE name IN ('Lemon juice (fresh)', 'Simple syrup')"
        ).fetchall()
        conn_q.close()
        resp = visit(c, "POST", "/quick-setup", label="POST /quick-setup",
                     data={"bottle": ["gin", "bourbon"],
                           "ingredient": [str(r[0]) for r in ing_rows]},
                     follow_redirects=True)
        if resp and "ready" not in resp.get_data(as_text=True).lower():
            failures.append(("quick-setup", "ready state not shown after /quick-setup"))
            print("  FAIL  quick-setup did not render ready state")

    # Bottles-only user (0 mixers) sees Quick Kitchen Check on Tonight.
    with app_module.app.test_client() as c:
        resp = visit(c, "POST", "/signup", label="POST /signup (bottles-only user)",
                     data={"username": "verify_kitchen_user",
                           "password": "password123",
                           "confirm": "password123"},
                     follow_redirects=True)
        conn_k = sqlite3.connect(scratch)
        k_uid = conn_k.execute(
            "SELECT id FROM users WHERE username = 'verify_kitchen_user'"
        ).fetchone()[0]
        conn_k.executemany(
            "INSERT INTO bottles (user_id, name, type, brand) VALUES (?, ?, ?, '')",
            [(k_uid, "Beefeater", "gin"), (k_uid, "Laphroaig 10", "scotch"), (k_uid, "Havana Club 3", "rum")],
        )
        conn_k.commit()
        conn_k.close()
        resp = visit(c, "GET", "/", label="GET / (0-ready Quick Kitchen Check)")
        if resp and "Quick kitchen check" not in resp.get_data(as_text=True):
            failures.append(("kitchen check", "missing Quick kitchen check card for 0-ready user"))
            print("  FAIL  missing Quick kitchen check card")

        # Manual POST /add on 0-mixer user stays on /bar; from_scan=1 goes to /.
        r_manual = c.post("/add", data={"name": "Manual Gin", "type": "gin"}, follow_redirects=False)
        if not (r_manual.status_code == 302 and "/bar" in r_manual.headers.get("Location", "")):
            failures.append(("manual add redirect", f"expected 302 -> /bar, got {r_manual.status_code} -> {r_manual.headers.get('Location')}"))
            print("  FAIL  manual /add redirect on 0-mixer user")
        else:
            print("  ok    manual POST /add (0-mixer user) -> /bar")

        r_scan = c.post("/add", data={"name": "Scanned Gin", "type": "gin", "from_scan": "1"}, follow_redirects=False)
        if not (r_scan.status_code == 302 and r_scan.headers.get("Location", "").endswith("/")):
            failures.append(("scan add redirect", f"expected 302 -> /, got {r_scan.status_code} -> {r_scan.headers.get('Location')}"))
            print("  FAIL  from_scan=1 /add redirect on 0-mixer user")
        else:
            print("  ok    POST /add (from_scan=1, 0-mixer user) -> /")

    print("\nLogged in:")
    with app_module.app.test_client() as c:
        visit(c, "POST", "/login", label="POST /login",
              data={"username": username, "password": password},
              follow_redirects=True)

        # Legacy cookie with user_id but no username still renders account topbar (#19).
        with c.session_transaction() as sess:
            sess.clear()
            sess["user_id"] = uid
        resp = visit(c, "GET", "/", label="GET / (legacy cookie without username)")
        if resp and username not in resp.get_data(as_text=True):
            failures.append(("legacy cookie username", "username missing from topbar"))
            print("  FAIL  legacy cookie missing username in topbar")

        for path in ("/", "/add", "/scan", "/scan-bulk", "/checklist", "/bar",
                     "/recommend", "/one-away", "/favorites", "/surprise"):
            visit(c, "GET", path, follow_redirects=True)

        # Search and grouping variants on /bar, which is where the raw type
        # slugs leaked and where orphaned headings showed up.
        for qs in ("?q=gin", "?q=zzzznothing", "?group=spirit", "?group=spirit&q=camp"):
            visit(c, "GET", "/bar" + qs, follow_redirects=True)

        resp_mix = visit(c, "GET", "/bar?tab=mixers", label="GET /bar?tab=mixers (apostrophe casing)")
        if resp_mix and "Peychaud'S Bitters" in resp_mix.get_data(as_text=True):
            failures.append(("mixer casing", "found Peychaud'S Bitters in /bar?tab=mixers"))
            print("  FAIL  found Peychaud'S Bitters in /bar?tab=mixers")

        resp_oa = visit(c, "GET", "/one-away", label="GET /one-away (one-tap actions)")
        if resp_oa:
            oa_html = resp_oa.get_data(as_text=True)
            if "I have this" not in oa_html and "Add to my bar" not in oa_html:
                failures.append(("one-away actions", "missing one-tap action on /one-away"))
                print("  FAIL  missing one-tap action on /one-away")

        import matching
        oa_groups = matching.get_one_away_grouped(uid)
        if oa_groups:
            miss_rid = oa_groups[0]["recipes"][0]["recipe"]["id"]
            r_miss = visit(c, "GET", f"/recipe/{miss_rid}", label=f"GET /recipe/{miss_rid} (missing action)")
            if r_miss:
                miss_html = r_miss.get_data(as_text=True)
                if "I have this" not in miss_html and "Add to my bar" not in miss_html:
                    failures.append(("recipe missing action", f"missing one-tap action on /recipe/{miss_rid}"))
                    print(f"  FAIL  missing one-tap action on /recipe/{miss_rid}")

        # Warm catalog cache once, then assert GET / opens at most 1 raw DB connection.
        c.get("/")
        orig_open = database._open_raw_db
        open_calls = []

        def _counting_open():
            open_calls.append(1)
            return orig_open()

        database._open_raw_db = _counting_open
        try:
            r_warm = visit(c, "GET", "/", label="GET / (warm cache, <=1 DB connection)")
            if r_warm and len(open_calls) > 1:
                failures.append(("request DB connection reuse", f"opened {len(open_calls)} connections on GET /"))
                print(f"  FAIL  GET / opened {len(open_calls)} connections (expected <= 1)")
            else:
                print(f"  ok    GET / warm DB connections opened = {len(open_calls)}")
        finally:
            database._open_raw_db = orig_open

        print(f"\n  Rendering all {len(recipe_ids)} recipe pages:")
        bad = 0
        for rid in recipe_ids:
            resp = None
            try:
                resp = c.get(f"/recipe/{rid}", follow_redirects=True)
            except Exception as exc:
                failures.append((f"GET /recipe/{rid}", f"raised {exc}"))
                bad += 1
                continue
            body = resp.get_data(as_text=True)
            if resp.status_code >= 400 or "Traceback (most recent call last)" in body:
                failures.append((f"GET /recipe/{rid}", f"HTTP {resp.status_code}"))
                print(f"    FAIL  /recipe/{rid}  HTTP {resp.status_code}")
                bad += 1
        print(f"    {len(recipe_ids) - bad} ok, {bad} failed")

        print("\n  POST paths:")
        if recipe_ids:
            rid = recipe_ids[0]
            visit(c, "POST", f"/rate/{rid}", label=f"POST /rate/{rid} (up)",
                  data={"thumb": "1"}, follow_redirects=True)
            visit(c, "POST", f"/rate/{rid}", label=f"POST /rate/{rid} (clear)",
                  data={"thumb": "1"}, follow_redirects=True)

        r_chk_fetch = c.post(
            "/checklist",
            data={"ingredient": []},
            headers={"X-Requested-With": "fetch"},
            follow_redirects=False,
        )
        if r_chk_fetch.status_code != 200 or not r_chk_fetch.is_json or not r_chk_fetch.get_json().get("ok"):
            failures.append(("checklist fetch JSON", f"got status={r_chk_fetch.status_code}, json={r_chk_fetch.get_data(as_text=True)}"))
            print("  FAIL  POST /checklist (X-Requested-With: fetch)")
        else:
            print("  ok    POST /checklist (X-Requested-With: fetch) HTTP 200 JSON")

        visit(c, "POST", "/checklist", data={"ingredient": []}, follow_redirects=True)
        visit(c, "POST", "/stock-add", data={"ingredient": []}, follow_redirects=True)

        r_sa_oa = c.post("/stock-add", data={"ingredient": [], "next": "/one-away"}, follow_redirects=False)
        if not (r_sa_oa.status_code == 302 and r_sa_oa.headers.get("Location", "").endswith("/one-away")):
            failures.append(("stock-add next=/one-away", f"got {r_sa_oa.status_code} -> {r_sa_oa.headers.get('Location')}"))
            print("  FAIL  POST /stock-add next=/one-away")
        else:
            print("  ok    POST /stock-add (next=/one-away) -> /one-away")

        r_sa_evil = c.post("/stock-add", data={"ingredient": [], "next": "https://evil.com"}, follow_redirects=False)
        loc_evil = r_sa_evil.headers.get("Location", "")
        if not (r_sa_evil.status_code == 302 and "evil.com" not in loc_evil and loc_evil.endswith("/")):
            failures.append(("stock-add open redirect", f"got {r_sa_evil.status_code} -> {loc_evil}"))
            print("  FAIL  POST /stock-add open redirect guard")
        else:
            print("  ok    POST /stock-add blocks external next URL")

        # A bottle type that is not in BOTTLE_TYPE_CHOICES must be coerced to
        # 'other' rather than accepted. This is the confirm_bulk failure that
        # silently tagged unknown bottles as Gin.
        visit(c, "POST", "/add", label="POST /add (junk type coerced)",
              data={"name": "Verify Junk Bottle", "type": "not-a-real-type"},
              follow_redirects=True)

        if bottle_ids:
            visit(c, "GET", f"/edit/{bottle_ids[0]}", follow_redirects=True)

        visit(c, "POST", "/logout", follow_redirects=True)

    database.log_scan(uid)
    if database.scans_today_global() < 1:
        failures.append(("scans_today_global", "expected >= 1 after log_scan"))
        print("\n  FAIL  scans_today_global() < 1 after log_scan")
    else:
        print(f"\n  ok    scans_today_global() = {database.scans_today_global()}")

    conn = sqlite3.connect(scratch)
    conn.row_factory = sqlite3.Row
    raw_row = conn.execute("SELECT * FROM recipes WHERE image_url IS NOT NULL AND image_url != '' LIMIT 1").fetchone()
    with app_module.app.test_request_context("/"):
        if not raw_row or not app_module.recipe_image_url(raw_row):
            failures.append(("recipe_image_url sqlite3.Row", "returned None for sqlite3.Row"))
            print("\n  FAIL  recipe_image_url(sqlite3.Row) returned None")
        else:
            print("\n  ok    recipe_image_url(sqlite3.Row) works")

        # Verify daily-rotating Featured Pour picks multiple drinks across days and avoids consecutive repeats.
        import matching as _m
        makeable_list = _m.get_recommendations(uid, max_makeable=200)["makeable"]
        ratings_map = _m.get_recommendations(uid, max_makeable=200)["ratings"]
        picks = [
            app_module.pick_featured_pour(makeable_list, ratings_map, uid, day_seed=739000 + d)["recipe"]["id"]
            for d in range(14)
        ]
        consecutive = any(picks[i] == picks[i + 1] for i in range(len(picks) - 1))
        if len(set(picks)) < 2 or consecutive:
            failures.append(("pick_featured_pour rotation", f"picks={picks}"))
            print("  FAIL  pick_featured_pour did not rotate cleanly")
        else:
            print(f"  ok    pick_featured_pour rotated ({len(set(picks))} distinct over 14 days)")

    # Verify catalog cache isolation against caller dict mutation.
    cached_1 = database.get_all_recipes()
    cached_1[0]["your_bottles"] = ["LEAK_TEST"]
    cached_2 = database.get_all_recipes()
    if "your_bottles" in cached_2[0]:
        failures.append(("catalog cache mutation isolation", "your_bottles leaked across calls"))
        print("  FAIL  catalog cache leaked mutation")
    else:
        print("  ok    catalog cache isolates outer dict mutations")
    junk = conn.execute(
        "SELECT type FROM bottles WHERE name = 'Verify Junk Bottle'").fetchone()
    spam = conn.execute(
        "SELECT id FROM users WHERE username = 'spam_bot_user'").fetchone()
    conn.close()
    if spam:
        failures.append(("honeypot", "spam_bot_user was created despite honeypot"))
        print("\n  FAIL  honeypot user was created")
    else:
        print("  ok    honeypot blocked spam user creation")
    if junk and junk[0] != "other":
        failures.append(("safe_bottle_type", f"junk type stored as {junk[0]!r}, expected 'other'"))
        print(f"\n  FAIL  junk bottle type stored as {junk[0]!r}, expected 'other'")
    elif junk:
        print("\n  ok    junk bottle type coerced to 'other'")

    os.unlink(scratch)

    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES:")
        for label, why in failures:
            print(f"  {label}: {why}")
        sys.exit(1)
    print("All routes rendered.")


if __name__ == "__main__":
    main()
