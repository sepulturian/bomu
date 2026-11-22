import sqlite3
import os
import re
import time

DEFAULT_DB_PATH = os.path.join(os.path.dirname(__file__), "bomu.db")
DB_PATH = DEFAULT_DB_PATH

_CATALOG_TTL_SECONDS = 300
_catalog_cache = {}


def _pg_url():
    if os.path.abspath(DB_PATH) != os.path.abspath(DEFAULT_DB_PATH):
        return None  # verify_routes.py overrides DB_PATH to a scratch SQLite file
    if os.environ.get("FORCE_SQLITE") == "1":
        return None
    raw = os.environ.get("DATABASE_URL") or os.environ.get("POSTGRES_URL")
    if not raw:
        return None
    url = raw.strip().strip("'\"")
    url = re.sub(r"(^|[?&])channel_binding=[^&]*&?", r"\1", url)
    url = url.replace("?&", "?").rstrip("?&")
    return url


def _is_postgres():
    return bool(_pg_url())


def _integrity_errors():
    if _is_postgres():
        import psycopg2
        return (sqlite3.IntegrityError, psycopg2.IntegrityError)
    return (sqlite3.IntegrityError,)


def _operational_errors():
    if _is_postgres():
        import psycopg2
        return (sqlite3.OperationalError, psycopg2.Error)
    return (sqlite3.OperationalError,)


class _PgRow(dict):
    """Row mapping supporting dict key lookup (`row['col']`), positional
    indexing (`row[0]`), and `dict(row)` conversions like sqlite3.Row."""

    def __init__(self, mapping):
        super().__init__(mapping)
        self._values = list(mapping.values())

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._values[key]
        return super().__getitem__(key)


class _PgCursor:
    """Thin wrapper over psycopg2 RealDictCursor that wraps rows in _PgRow
    and translates SQLite `?` placeholders into `%s`."""

    def __init__(self, cur):
        self._cur = cur

    def execute(self, sql, params=None):
        pg_sql = sql.replace("?", "%s")
        if params is None:
            self._cur.execute(pg_sql)
        else:
            self._cur.execute(pg_sql, params)
        return self

    def executemany(self, sql, seq_of_params):
        pg_sql = sql.replace("?", "%s")
        self._cur.executemany(pg_sql, seq_of_params)
        return self

    def fetchone(self):
        row = self._cur.fetchone()
        return _PgRow(row) if row is not None else None

    def fetchall(self):
        return [_PgRow(r) for r in self._cur.fetchall()]

    @property
    def rowcount(self):
        return self._cur.rowcount

    def close(self):
        self._cur.close()


class _PgConn:
    """Minimal sqlite3.Connection-compatible wrapper around a psycopg2 connection."""

    def __init__(self, raw_conn, real_dict_cursor):
        self._conn = raw_conn
        self._cursor_factory = real_dict_cursor

    def cursor(self):
        return _PgCursor(self._conn.cursor(cursor_factory=self._cursor_factory))

    def execute(self, sql, params=None):
        return self.cursor().execute(sql, params)

    def executemany(self, sql, seq_of_params):
        return self.cursor().executemany(sql, seq_of_params)

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        self._conn.close()


class _RequestConnProxy:
    """Proxy for a request-scoped connection where .close() is a no-op until
    Flask tears down the app context."""

    def __init__(self, conn):
        self._conn = conn

    def cursor(self):
        return self._conn.cursor()

    def execute(self, sql, *args):
        return self._conn.execute(sql, *args)

    def executemany(self, sql, *args):
        return self._conn.executemany(sql, *args)

    def commit(self):
        return self._conn.commit()

    def rollback(self):
        return self._conn.rollback()

    def close(self):
        pass

    def __getattr__(self, name):
        return getattr(self._conn, name)


def _in_flask_app_context():
    try:
        from flask import has_app_context
        return has_app_context()
    except ImportError:
        return False


def _db_target_key():
    return _pg_url() or os.path.abspath(DB_PATH)


def _open_raw_db():
    """Open a fresh connection to Neon Postgres (when configured) or SQLite."""
    pg_url = _pg_url()
    if pg_url:
        import psycopg2
        import psycopg2.extras
        raw = psycopg2.connect(pg_url)
        return _PgConn(raw, psycopg2.extras.RealDictCursor)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # lets us access columns by name
    return conn


def get_db():
    """Return a request-scoped DB connection inside Flask app contexts, or a
    standalone connection for CLI scripts and migrations."""
    if _in_flask_app_context():
        from flask import g
        target = _db_target_key()
        entry = getattr(g, "_bomu_db", None)
        if entry is not None:
            cached_target, cached_conn = entry
            if cached_target == target:
                return _RequestConnProxy(cached_conn)
            try:
                cached_conn.close()
            except Exception:
                pass
        conn = _open_raw_db()
        g._bomu_db = (target, conn)
        return _RequestConnProxy(conn)
    return _open_raw_db()


def close_request_db(exc=None):
    """Close any request-scoped DB connection at the end of a Flask request."""
    if not _in_flask_app_context():
        return
    from flask import g
    entry = g.pop("_bomu_db", None)
    if entry is None:
        return
    _target, conn = entry
    try:
        if exc is not None:
            try:
                conn.rollback()
            except Exception:
                pass
    finally:
        conn.close()


def _cache_scope_key():
    pg_url = _pg_url()
    if pg_url:
        return ("pg", pg_url)
    path = os.path.abspath(DB_PATH)
    try:
        mtime = os.path.getmtime(path)
    except OSError:
        mtime = 0
    return ("sqlite", path, mtime)


def invalidate_catalog_cache():
    """Clear the read-only recipe/ingredient catalog cache."""
    _catalog_cache.clear()


# Single-use sign-in links (2026-11-21), made by make_login_link.py and spent
# by GET/POST /signin/<token>. Only a SHA-256 of the token is stored, so a
# copy of this table can't sign anyone in. Timestamps are naive UTC written by
# login_links.py, never by the database clock. Shared by init_db() and
# migrate_login_links_2026_11.py so the two can't drift.
LOGIN_LINKS_DDL_POSTGRES = """CREATE TABLE IF NOT EXISTS login_links (
    token_hash TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    used_at TIMESTAMP
)"""
LOGIN_LINKS_DDL_SQLITE = """CREATE TABLE IF NOT EXISTS login_links (
    token_hash TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    used_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
)"""
LOGIN_LINKS_INDEX_DDL = (
    "CREATE INDEX IF NOT EXISTS idx_login_links_user ON login_links (user_id)"
)


def init_db(force=False, seed=True):
    """Create tables and seed ingredient data if they don't exist yet."""
    if _is_postgres():
        if not force:
            return
        conn = get_db()
        c = conn.cursor()
        ddl_statements = [
            """CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_users_username_lower ON users (LOWER(username))",
            """CREATE TABLE IF NOT EXISTS bottles (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                brand TEXT,
                added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS ingredients (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                in_stock INTEGER DEFAULT 0
            )""",
            """CREATE TABLE IF NOT EXISTS user_stock (
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                ingredient_id INTEGER NOT NULL REFERENCES ingredients(id) ON DELETE CASCADE,
                PRIMARY KEY (user_id, ingredient_id)
            )""",
            """CREATE TABLE IF NOT EXISTS recipes (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                glass TEXT,
                instructions TEXT NOT NULL,
                image_url TEXT,
                cocktaildb_id TEXT,
                source TEXT DEFAULT 'thecocktaildb',
                added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                about TEXT,
                tip TEXT
            )""",
            """CREATE TABLE IF NOT EXISTS recipe_ingredients (
                id SERIAL PRIMARY KEY,
                recipe_id INTEGER NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
                raw_name TEXT NOT NULL,
                raw_measure TEXT,
                requirement_type TEXT NOT NULL,
                bottle_type TEXT,
                ingredient_name TEXT,
                notes TEXT,
                sort_order INTEGER DEFAULT 0
            )""",
            """CREATE TABLE IF NOT EXISTS ratings (
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                recipe_id INTEGER NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
                thumb INTEGER NOT NULL,
                rated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, recipe_id)
            )""",
            """CREATE TABLE IF NOT EXISTS scan_log (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS recipe_enhancements (
                id SERIAL PRIMARY KEY,
                recipe_id INTEGER NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
                name TEXT NOT NULL,
                ingredient_name TEXT,
                measure TEXT,
                note TEXT,
                source TEXT NOT NULL,
                sort_order INTEGER NOT NULL DEFAULT 0,
                UNIQUE (recipe_id, name)
            )""",
            "CREATE INDEX IF NOT EXISTS idx_recipe_enhancements_recipe ON recipe_enhancements (recipe_id)",
            LOGIN_LINKS_DDL_POSTGRES,
            LOGIN_LINKS_INDEX_DDL,
        ]
        for stmt in ddl_statements:
            c.execute(stmt)
        if seed:
            c.execute("SELECT COUNT(*) FROM ingredients")
            if c.fetchone()[0] == 0:
                seed_ingredients(c)
        conn.commit()
        conn.close()
        invalidate_catalog_cache()
        return

    conn = get_db()
    c = conn.cursor()

    # Users -- one row per person. Everything personal (bottles, ratings,
    # checklist stock) hangs off users.id. Recipes stay shared.
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE COLLATE NOCASE,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Bottles table -- for spirits the user adds manually or via photo
    c.execute("""
        CREATE TABLE IF NOT EXISTS bottles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            brand TEXT,
            added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # Ingredients table -- shared catalog of mixers, bitters, garnishes, etc.
    # NOTE: the in_stock column is legacy from single-user days; per-user
    # stock now lives in user_stock. Kept so old DBs load without a rebuild.
    c.execute("""
        CREATE TABLE IF NOT EXISTS ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            in_stock INTEGER DEFAULT 0
        )
    """)

    # Per-user checklist state: a row here means "this user has this
    # ingredient ticked". No row = not in stock for that user.
    c.execute("""
        CREATE TABLE IF NOT EXISTS user_stock (
            user_id INTEGER NOT NULL,
            ingredient_id INTEGER NOT NULL,
            PRIMARY KEY (user_id, ingredient_id),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE CASCADE
        )
    """)

    # Recipes table -- one row per cocktail
    c.execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            glass TEXT,
            instructions TEXT NOT NULL,
            image_url TEXT,
            cocktaildb_id TEXT,
            source TEXT DEFAULT 'thecocktaildb',
            added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Recipe ingredients -- child table, one row per ingredient in a recipe
    # requirement_type: 'bottle_type' | 'ingredient' | 'optional'
    # - bottle_type: matches bottles.type (e.g. "gin", "vermouth")
    # - ingredient: matches ingredients.name (e.g. "Lime juice (fresh)")
    # - optional: garnishes and 'to taste' stuff -- doesn't block makeability
    c.execute("""
        CREATE TABLE IF NOT EXISTS recipe_ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER NOT NULL,
            raw_name TEXT NOT NULL,
            raw_measure TEXT,
            requirement_type TEXT NOT NULL,
            bottle_type TEXT,
            ingredient_name TEXT,
            notes TEXT,
            sort_order INTEGER DEFAULT 0,
            FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
        )
    """)

    # Ratings -- thumbs up/down per user per recipe.
    # thumb: 1 = up, -1 = down, 0 = unset (we delete the row instead of storing 0).
    c.execute("""
        CREATE TABLE IF NOT EXISTS ratings (
            user_id INTEGER NOT NULL,
            recipe_id INTEGER NOT NULL,
            thumb INTEGER NOT NULL,
            rated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, recipe_id),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
        )
    """)

    # Scan log -- one row per photo scan, used to enforce the per-user
    # daily cap (every scan costs real API money on Aaron's key).
    c.execute("""
        CREATE TABLE IF NOT EXISTS scan_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # Single-use sign-in links: see LOGIN_LINKS_DDL_SQLITE above.
    c.execute(LOGIN_LINKS_DDL_SQLITE)
    c.execute(LOGIN_LINKS_INDEX_DDL)

    # Only seed if the table is empty (first run)
    if seed:
        c.execute("SELECT COUNT(*) FROM ingredients")
        if c.fetchone()[0] == 0:
            seed_ingredients(c)

    conn.commit()
    conn.close()
    invalidate_catalog_cache()


SEED_INGREDIENTS = [
    # Mixers
    ("Tonic water", "mixer"),
    ("Soda water / club soda", "mixer"),
    ("Ginger beer", "mixer"),
    ("Ginger ale", "mixer"),
    ("Cola", "mixer"),
    ("Lemon juice (fresh)", "mixer"),
    ("Lime juice (fresh)", "mixer"),
    ("Orange juice", "mixer"),
    ("Cranberry juice", "mixer"),
    ("Pineapple juice", "mixer"),
    ("Grapefruit juice", "mixer"),
    ("Tomato juice", "mixer"),
    ("Cream of coconut", "auto"),
    ("Heavy cream", "pantry"),
    ("Simple syrup", "mixer"),
    ("Grenadine", "mixer"),

    # Bitters
    ("Angostura bitters", "bitter"),
    ("Orange bitters", "bitter"),
    ("Peychaud's bitters", "bitter"),

    # Garnishes
    ("Lemons", "garnish"),
    ("Limes", "garnish"),
    ("Oranges", "garnish"),
    ("Maraschino cherries", "garnish"),
    ("Olives", "garnish"),
    ("Fresh mint", "garnish"),
    ("Cocktail onions", "garnish"),

    # Pantry staples
    ("Sugar (white)", "pantry"),
    ("Salt", "pantry"),
    ("Pepper", "pantry"),
    ("Tabasco / hot sauce", "pantry"),
    ("Worcestershire sauce", "pantry"),
    ("Honey", "pantry"),
    ("Egg whites", "pantry"),
]

# Used by get_auto_added_ingredients() to detect ingredients added by import
# scripts (vs. shipped in the original seed).
SEED_INGREDIENT_NAMES = {name for name, _category in SEED_INGREDIENTS}


def seed_ingredients(cursor):
    """Pre-load common mixers, bitters, garnishes, and pantry staples."""
    cursor.executemany(
        "INSERT INTO ingredients (name, category) VALUES (?, ?)",
        SEED_INGREDIENTS,
    )


# --- User helpers ---

def create_user(username, password_hash):
    """Insert a new user. Returns the new user id, or None if the username
    is already taken (case-insensitive)."""
    conn = get_db()
    try:
        if _is_postgres():
            cur = conn.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?) RETURNING id",
                (username, password_hash),
            )
            user_id = cur.fetchone()[0]
        else:
            cur = conn.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, password_hash),
            )
            user_id = cur.lastrowid
        conn.commit()
        return user_id
    except _integrity_errors():
        conn.rollback()
        return None
    finally:
        conn.close()


def get_user_by_username(username):
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM users WHERE LOWER(username) = LOWER(?)", (username,)
    ).fetchone()
    conn.close()
    return row


def get_user(user_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return row


def set_user_password(user_id, password_hash):
    """Replace a user's password hash (from /account/password). Returns True
    if a row was updated."""
    conn = get_db()
    cur = conn.execute(
        "UPDATE users SET password_hash = ? WHERE id = ?", (password_hash, user_id)
    )
    updated = cur.rowcount == 1
    conn.commit()
    conn.close()
    return updated


# --- Scan-cap helpers ---

def log_scan(user_id):
    conn = get_db()
    conn.execute("INSERT INTO scan_log (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()


def scans_today(user_id):
    """How many scans this user has done since midnight UTC (matches the
    CURRENT_TIMESTAMP default, which is UTC)."""
    conn = get_db()
    sql = (
        "SELECT COUNT(*) FROM scan_log WHERE user_id = ? AND scanned_at >= CURRENT_DATE"
        if _is_postgres()
        else "SELECT COUNT(*) FROM scan_log WHERE user_id = ? AND scanned_at >= date('now')"
    )
    n = conn.execute(sql, (user_id,)).fetchone()[0]
    conn.close()
    return n


def scans_today_global():
    """Total scans across all users since midnight UTC."""
    conn = get_db()
    sql = (
        "SELECT COUNT(*) FROM scan_log WHERE scanned_at >= CURRENT_DATE"
        if _is_postgres()
        else "SELECT COUNT(*) FROM scan_log WHERE scanned_at >= date('now')"
    )
    n = conn.execute(sql).fetchone()[0]
    conn.close()
    return n


# --- Bottle helpers (all scoped to a user) ---

def get_all_bottles(user_id):
    conn = get_db()
    bottles = conn.execute(
        "SELECT * FROM bottles WHERE user_id = ? ORDER BY name", (user_id,)
    ).fetchall()
    conn.close()
    return bottles


def get_bottle(bottle_id, user_id):
    """Fetch one bottle, but only if it belongs to this user -- stops one
    user editing/deleting another user's bottles by guessing ids."""
    conn = get_db()
    bottle = conn.execute(
        "SELECT * FROM bottles WHERE id = ? AND user_id = ?",
        (bottle_id, user_id),
    ).fetchone()
    conn.close()
    return bottle


def add_bottle(user_id, name, bottle_type, brand):
    conn = get_db()
    conn.execute(
        "INSERT INTO bottles (user_id, name, type, brand) VALUES (?, ?, ?, ?)",
        (user_id, name, bottle_type, brand)
    )
    conn.commit()
    conn.close()


def update_bottle(bottle_id, user_id, name, bottle_type, brand):
    conn = get_db()
    conn.execute(
        "UPDATE bottles SET name = ?, type = ?, brand = ? WHERE id = ? AND user_id = ?",
        (name, bottle_type, brand, bottle_id, user_id)
    )
    conn.commit()
    conn.close()


def delete_bottle(bottle_id, user_id):
    conn = get_db()
    conn.execute(
        "DELETE FROM bottles WHERE id = ? AND user_id = ?", (bottle_id, user_id)
    )
    conn.commit()
    conn.close()


# --- Ingredient / checklist helpers ---

def _get_ingredient_catalog():
    """Return cached shared ingredient catalog rows as plain dicts."""
    scope = _cache_scope_key()
    now = time.monotonic()
    entry = _catalog_cache.get("ingredients")
    if entry and entry["scope"] == scope and (now - entry["ts"]) < _CATALOG_TTL_SECONDS:
        return entry["data"]
    conn = get_db()
    rows = conn.execute("SELECT * FROM ingredients ORDER BY category, name").fetchall()
    conn.close()
    data = [dict(r) for r in rows]
    _catalog_cache["ingredients"] = {"scope": scope, "ts": now, "data": data}
    return data


def get_all_ingredients(user_id=None):
    """Return the shared ingredient catalog. If user_id is given, each row is
    a dict whose in_stock reflects THAT user's checklist (from user_stock),
    so templates keep working exactly as before multi-user."""
    base = _get_ingredient_catalog()
    if user_id is None:
        return [dict(ing) for ing in base]
    conn = get_db()
    stocked = {
        r["ingredient_id"] for r in conn.execute(
            "SELECT ingredient_id FROM user_stock WHERE user_id = ?", (user_id,)
        ).fetchall()
    }
    conn.close()
    out = []
    for ing in base:
        d = dict(ing)
        d["in_stock"] = 1 if ing["id"] in stocked else 0
        out.append(d)
    return out


def get_auto_added_ingredients(user_id, only_unstocked=True, ingredients=None):
    """Return ingredients that were NOT in the original seed list -- i.e. they
    were inserted later by an import script (Coffee liqueur, Champagne, etc.).
    Defaults to only those this user hasn't ticked yet so the checklist can
    highlight items they haven't reviewed."""
    all_ings = ingredients if ingredients is not None else get_all_ingredients(user_id)
    out = []
    for ing in all_ings:
        if ing["name"] in SEED_INGREDIENT_NAMES:
            continue
        if only_unstocked and ing["in_stock"]:
            continue
        out.append(ing)
    return out


def is_auto_added(ingredient_name):
    """Helper for templates: True if this ingredient was added post-seed."""
    return ingredient_name not in SEED_INGREDIENT_NAMES


def add_ingredients_to_stock(user_id, ingredient_ids):
    """Tick specific ingredients WITHOUT touching the rest of the checklist.

    Deliberately not set_all_ingredients_stock, which deletes every row for the
    user first. The quick-add nudge on the Make page submits three ids, and
    reusing the replace-everything version there would wipe the other 15 things
    the user had already ticked."""
    if not ingredient_ids:
        return
    conn = get_db()
    conn.executemany(
        "INSERT INTO user_stock (user_id, ingredient_id) VALUES (?, ?) ON CONFLICT (user_id, ingredient_id) DO NOTHING",
        [(user_id, int(i)) for i in ingredient_ids],
    )
    conn.commit()
    conn.close()


def set_ingredient_stock(user_id, ingredient_id, in_stock):
    """Tick or untick ONE checklist row; returns the user's new tick count.

    The Mixers page autosaves through this, one change per request. It used to
    post the whole page to set_all_ingredients_stock(), which made whatever the
    page showed the truth: a Mixers page opened before an "I have this" tap
    elsewhere silently unticked that item the next time anything was ticked."""
    conn = get_db()
    if in_stock:
        conn.execute(
            "INSERT INTO user_stock (user_id, ingredient_id) VALUES (?, ?) ON CONFLICT (user_id, ingredient_id) DO NOTHING",
            (user_id, int(ingredient_id)),
        )
    else:
        conn.execute(
            "DELETE FROM user_stock WHERE user_id = ? AND ingredient_id = ?",
            (user_id, int(ingredient_id)),
        )
    conn.commit()
    count = conn.execute(
        "SELECT COUNT(*) FROM user_stock WHERE user_id = ?", (user_id,)
    ).fetchone()[0]
    conn.close()
    return count


def set_all_ingredients_stock(user_id, checked_ids):
    """Replace this user's checklist state: checked ones in stock, rest not.

    Only for the no-JavaScript "Save mixers" submit. Anything that can run
    from a page that may be out of date should use set_ingredient_stock() or
    add_ingredients_to_stock(), which never touch rows they weren't given."""
    conn = get_db()
    conn.execute("DELETE FROM user_stock WHERE user_id = ?", (user_id,))
    if checked_ids:
        conn.executemany(
            "INSERT INTO user_stock (user_id, ingredient_id) VALUES (?, ?) ON CONFLICT (user_id, ingredient_id) DO NOTHING",
            [(user_id, i) for i in checked_ids],
        )
    conn.commit()
    conn.close()


# --- Recipe helpers ---

def add_recipe(name, glass, instructions, image_url, cocktaildb_id, ingredients):
    """Insert a recipe and its ingredients in one transaction.
    `ingredients` is a list of dicts with keys:
      raw_name, raw_measure, requirement_type, bottle_type, ingredient_name, notes
    Returns the new recipe id, or None if name already exists."""
    conn = get_db()
    try:
        if _is_postgres():
            cur = conn.execute(
                """INSERT INTO recipes (name, glass, instructions, image_url, cocktaildb_id)
                   VALUES (?, ?, ?, ?, ?) RETURNING id""",
                (name, glass, instructions, image_url, cocktaildb_id),
            )
            recipe_id = cur.fetchone()[0]
        else:
            cur = conn.execute(
                """INSERT INTO recipes (name, glass, instructions, image_url, cocktaildb_id)
                   VALUES (?, ?, ?, ?, ?)""",
                (name, glass, instructions, image_url, cocktaildb_id),
            )
            recipe_id = cur.lastrowid
        for i, ing in enumerate(ingredients):
            conn.execute(
                """INSERT INTO recipe_ingredients
                   (recipe_id, raw_name, raw_measure, requirement_type,
                    bottle_type, ingredient_name, notes, sort_order)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    recipe_id,
                    ing.get("raw_name", ""),
                    ing.get("raw_measure"),
                    ing.get("requirement_type", "optional"),
                    ing.get("bottle_type"),
                    ing.get("ingredient_name"),
                    ing.get("notes"),
                    i,
                ),
            )
        conn.commit()
        invalidate_catalog_cache()
        return recipe_id
    except _integrity_errors():
        # Recipe name already exists
        conn.rollback()
        return None
    finally:
        conn.close()


def _get_recipe_catalog():
    """Return cached (ordered_recipes, recipes_by_id) with ingredients and
    optional recipe_enhancements preloaded."""
    scope = _cache_scope_key()
    now = time.monotonic()
    entry = _catalog_cache.get("recipes")
    if entry and entry["scope"] == scope and (now - entry["ts"]) < _CATALOG_TTL_SECONDS:
        return entry["data"]

    conn = get_db()
    recipes = conn.execute("SELECT * FROM recipes ORDER BY name").fetchall()
    all_ings = conn.execute(
        "SELECT * FROM recipe_ingredients ORDER BY recipe_id, sort_order"
    ).fetchall()
    enh_by_recipe = {}
    try:
        all_enhs = conn.execute(
            "SELECT * FROM recipe_enhancements ORDER BY recipe_id, sort_order"
        ).fetchall()
        for enh in all_enhs:
            enh_by_recipe.setdefault(enh["recipe_id"], []).append(dict(enh))
    except _operational_errors():
        conn.rollback()
    conn.close()

    ings_by_recipe = {}
    for ing in all_ings:
        ings_by_recipe.setdefault(ing["recipe_id"], []).append(dict(ing))

    ordered = []
    by_id = {}
    for r in recipes:
        r_dict = dict(r)
        rid = r_dict["id"]
        item = {
            "recipe": r_dict,
            "ingredients": ings_by_recipe.get(rid, []),
            "enhancements": enh_by_recipe.get(rid, []),
        }
        ordered.append(item)
        by_id[rid] = item

    data = (ordered, by_id)
    _catalog_cache["recipes"] = {"scope": scope, "ts": now, "data": data}
    return data


def get_all_recipes():
    """Return every recipe with its ingredients, used by the matcher.
    Returns fresh outer dicts so callers can attach per-user fields like
    'your_bottles' without polluting the shared catalog cache."""
    ordered, _by_id = _get_recipe_catalog()
    return [
        {"recipe": item["recipe"], "ingredients": item["ingredients"]}
        for item in ordered
    ]


def get_recipe(recipe_id):
    """Return a single recipe with ingredients and enhancements, for detail view."""
    _ordered, by_id = _get_recipe_catalog()
    item = by_id.get(recipe_id)
    if not item:
        return None
    return {
        "recipe": item["recipe"],
        "ingredients": item["ingredients"],
        "enhancements": item["enhancements"],
    }


def get_recipe_enhancements(conn, recipe_id):
    """Documented optional additions for a recipe -- the "Make it your own"
    block. Deliberately a separate table from recipe_ingredients:

    - The matcher never reads it, so nothing here can change what a user can
      make. That is the whole point. An enhancement is a suggestion, not part
      of the spec, and the 2026-07-26 session spent an afternoon separating
      those two ideas after twelve orphaned bitters rows blurred them.
    - Every row carries a `source`, because the standing rule in about_text.py
      is that nothing is invented. A suggestion with no citation does not ship.

    Returns [] if the table does not exist yet, so the code can be deployed
    before the migration is run -- the same order the About columns shipped in.
    """
    try:
        rows = conn.execute(
            "SELECT * FROM recipe_enhancements WHERE recipe_id = ? ORDER BY sort_order",
            (recipe_id,),
        ).fetchall()
    except _operational_errors():
        conn.rollback()
        return []
    return [dict(r) for r in rows]


def recipe_count():
    conn = get_db()
    n = conn.execute("SELECT COUNT(*) FROM recipes").fetchone()[0]
    conn.close()
    return n


# --- Rating helpers (all scoped to a user) ---

def set_rating(user_id, recipe_id, thumb):
    """Set thumb up (1), down (-1), or clear (0) the rating for a recipe.
    A thumb value of 0 deletes the row instead of storing it -- keeps the
    ratings table clean so 'unset' really means 'not in the table'."""
    conn = get_db()
    if thumb == 0:
        conn.execute(
            "DELETE FROM ratings WHERE user_id = ? AND recipe_id = ?",
            (user_id, recipe_id),
        )
    else:
        # SQLite UPSERT: insert if missing, otherwise overwrite thumb + timestamp
        conn.execute(
            """INSERT INTO ratings (user_id, recipe_id, thumb, rated_at)
               VALUES (?, ?, ?, CURRENT_TIMESTAMP)
               ON CONFLICT(user_id, recipe_id) DO UPDATE SET
                   thumb = excluded.thumb,
                   rated_at = CURRENT_TIMESTAMP""",
            (user_id, recipe_id, thumb),
        )
    conn.commit()
    conn.close()


def get_rating(user_id, recipe_id):
    """Return 1, -1, or 0 (no rating)."""
    conn = get_db()
    row = conn.execute(
        "SELECT thumb FROM ratings WHERE user_id = ? AND recipe_id = ?",
        (user_id, recipe_id),
    ).fetchone()
    conn.close()
    return row["thumb"] if row else 0


def get_all_ratings(user_id):
    """Return a dict {recipe_id: thumb} for fast lookup when ranking lists."""
    conn = get_db()
    rows = conn.execute(
        "SELECT recipe_id, thumb FROM ratings WHERE user_id = ?", (user_id,)
    ).fetchall()
    conn.close()
    return {r["recipe_id"]: r["thumb"] for r in rows}


def get_favorites(user_id):
    """Return this user's thumbs-up recipes, most recently rated first."""
    conn = get_db()
    rows = conn.execute(
        """SELECT r.*, ra.rated_at
           FROM recipes r
           JOIN ratings ra ON ra.recipe_id = r.id
           WHERE ra.thumb = 1 AND ra.user_id = ?
           ORDER BY ra.rated_at DESC""",
        (user_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
