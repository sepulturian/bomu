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
        # Anything behind auth should redirect, not explode.
        visit(c, "GET", "/recommend", label="GET /recommend (logged out)")

    print("\nLogged in:")
    with app_module.app.test_client() as c:
        visit(c, "POST", "/login", label="POST /login",
              data={"username": username, "password": password},
              follow_redirects=True)

        for path in ("/", "/add", "/scan", "/scan-bulk", "/checklist", "/bar",
                     "/recommend", "/one-away", "/favorites", "/surprise"):
            visit(c, "GET", path, follow_redirects=True)

        # Search and grouping variants on /bar, which is where the raw type
        # slugs leaked and where orphaned headings showed up.
        for qs in ("?q=gin", "?q=zzzznothing", "?group=spirit", "?group=spirit&q=camp"):
            visit(c, "GET", "/bar" + qs, follow_redirects=True)

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

        visit(c, "POST", "/checklist", data={"ingredient": []}, follow_redirects=True)
        visit(c, "POST", "/stock-add", data={"ingredient": []}, follow_redirects=True)

        # A bottle type that is not in BOTTLE_TYPE_CHOICES must be coerced to
        # 'other' rather than accepted. This is the confirm_bulk failure that
        # silently tagged unknown bottles as Gin.
        visit(c, "POST", "/add", label="POST /add (junk type coerced)",
              data={"name": "Verify Junk Bottle", "type": "not-a-real-type"},
              follow_redirects=True)

        if bottle_ids:
            visit(c, "GET", f"/edit/{bottle_ids[0]}", follow_redirects=True)

        visit(c, "POST", "/logout", follow_redirects=True)

    conn = sqlite3.connect(scratch)
    junk = conn.execute(
        "SELECT type FROM bottles WHERE name = 'Verify Junk Bottle'").fetchone()
    conn.close()
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
