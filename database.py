import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "bomu.db")


def get_db():
    """Open a connection to the database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # lets us access columns by name
    return conn


def init_db():
    """Create tables and seed ingredient data if they don't exist yet."""
    conn = get_db()
    c = conn.cursor()

    # Bottles table -- for spirits the user adds manually or via photo
    c.execute("""
        CREATE TABLE IF NOT EXISTS bottles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            brand TEXT,
            added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Ingredients table -- pre-seeded mixers, bitters, garnishes, etc.
    c.execute("""
        CREATE TABLE IF NOT EXISTS ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            in_stock INTEGER DEFAULT 0
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

    # Ratings -- thumbs up/down per recipe. One row per rated recipe.
    # thumb: 1 = up, -1 = down, 0 = unset (we delete the row instead of storing 0).
    c.execute("""
        CREATE TABLE IF NOT EXISTS ratings (
            recipe_id INTEGER PRIMARY KEY,
            thumb INTEGER NOT NULL,
            rated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
        )
    """)

    # Only seed if the table is empty (first run)
    c.execute("SELECT COUNT(*) FROM ingredients")
    if c.fetchone()[0] == 0:
        seed_ingredients(c)

    conn.commit()
    conn.close()


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
    ("Coconut cream", "mixer"),
    ("Heavy cream", "mixer"),
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


# --- Helper functions for the app ---

def get_all_bottles():
    conn = get_db()
    bottles = conn.execute("SELECT * FROM bottles ORDER BY name").fetchall()
    conn.close()
    return bottles


def get_bottle(bottle_id):
    conn = get_db()
    bottle = conn.execute("SELECT * FROM bottles WHERE id = ?", (bottle_id,)).fetchone()
    conn.close()
    return bottle


def add_bottle(name, bottle_type, brand):
    conn = get_db()
    conn.execute(
        "INSERT INTO bottles (name, type, brand) VALUES (?, ?, ?)",
        (name, bottle_type, brand)
    )
    conn.commit()
    conn.close()


def update_bottle(bottle_id, name, bottle_type, brand):
    conn = get_db()
    conn.execute(
        "UPDATE bottles SET name = ?, type = ?, brand = ? WHERE id = ?",
        (name, bottle_type, brand, bottle_id)
    )
    conn.commit()
    conn.close()


def delete_bottle(bottle_id):
    conn = get_db()
    conn.execute("DELETE FROM bottles WHERE id = ?", (bottle_id,))
    conn.commit()
    conn.close()


def get_all_ingredients():
    conn = get_db()
    ingredients = conn.execute(
        "SELECT * FROM ingredients ORDER BY category, name"
    ).fetchall()
    conn.close()
    return ingredients


def get_auto_added_ingredients(only_unstocked=True):
    """Return ingredients that were NOT in the original seed list -- i.e. they
    were inserted later by an import script (Coffee liqueur, Champagne, etc.).
    Defaults to only those still not in_stock so the checklist can highlight
    items the user hasn't reviewed yet."""
    all_ings = get_all_ingredients()
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


def update_ingredient_stock(ingredient_id, in_stock):
    conn = get_db()
    conn.execute(
        "UPDATE ingredients SET in_stock = ? WHERE id = ?",
        (in_stock, ingredient_id)
    )
    conn.commit()
    conn.close()


def set_all_ingredients_stock(checked_ids):
    """Update all ingredients: checked ones are in stock, rest are not."""
    conn = get_db()
    # First, set everything to out of stock
    conn.execute("UPDATE ingredients SET in_stock = 0")
    # Then mark the checked ones as in stock
    if checked_ids:
        placeholders = ",".join("?" * len(checked_ids))
        conn.execute(
            f"UPDATE ingredients SET in_stock = 1 WHERE id IN ({placeholders})",
            checked_ids
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
        return recipe_id
    except sqlite3.IntegrityError:
        # Recipe name already exists
        conn.rollback()
        return None
    finally:
        conn.close()


def get_all_recipes():
    """Return every recipe with its ingredients, used by the matcher."""
    conn = get_db()
    recipes = conn.execute("SELECT * FROM recipes ORDER BY name").fetchall()
    result = []
    for r in recipes:
        ings = conn.execute(
            "SELECT * FROM recipe_ingredients WHERE recipe_id = ? ORDER BY sort_order",
            (r["id"],),
        ).fetchall()
        result.append({"recipe": dict(r), "ingredients": [dict(i) for i in ings]})
    conn.close()
    return result


def get_recipe(recipe_id):
    """Return a single recipe with ingredients, for the detail view."""
    conn = get_db()
    recipe = conn.execute("SELECT * FROM recipes WHERE id = ?", (recipe_id,)).fetchone()
    if not recipe:
        conn.close()
        return None
    ings = conn.execute(
        "SELECT * FROM recipe_ingredients WHERE recipe_id = ? ORDER BY sort_order",
        (recipe_id,),
    ).fetchall()
    conn.close()
    return {"recipe": dict(recipe), "ingredients": [dict(i) for i in ings]}


def recipe_count():
    conn = get_db()
    n = conn.execute("SELECT COUNT(*) FROM recipes").fetchone()[0]
    conn.close()
    return n


# --- Rating helpers ---

def set_rating(recipe_id, thumb):
    """Set thumb up (1), down (-1), or clear (0) the rating for a recipe.
    A thumb value of 0 deletes the row instead of storing it -- keeps the
    ratings table clean so 'unset' really means 'not in the table'."""
    conn = get_db()
    if thumb == 0:
        conn.execute("DELETE FROM ratings WHERE recipe_id = ?", (recipe_id,))
    else:
        # SQLite UPSERT: insert if missing, otherwise overwrite thumb + timestamp
        conn.execute(
            """INSERT INTO ratings (recipe_id, thumb, rated_at)
               VALUES (?, ?, CURRENT_TIMESTAMP)
               ON CONFLICT(recipe_id) DO UPDATE SET
                   thumb = excluded.thumb,
                   rated_at = CURRENT_TIMESTAMP""",
            (recipe_id, thumb),
        )
    conn.commit()
    conn.close()


def get_rating(recipe_id):
    """Return 1, -1, or 0 (no rating)."""
    conn = get_db()
    row = conn.execute(
        "SELECT thumb FROM ratings WHERE recipe_id = ?", (recipe_id,)
    ).fetchone()
    conn.close()
    return row["thumb"] if row else 0


def get_all_ratings():
    """Return a dict {recipe_id: thumb} for fast lookup when ranking lists."""
    conn = get_db()
    rows = conn.execute("SELECT recipe_id, thumb FROM ratings").fetchall()
    conn.close()
    return {r["recipe_id"]: r["thumb"] for r in rows}


def get_favorites():
    """Return all thumbs-up recipes, most recently rated first."""
    conn = get_db()
    rows = conn.execute(
        """SELECT r.*, ra.rated_at
           FROM recipes r
           JOIN ratings ra ON ra.recipe_id = r.id
           WHERE ra.thumb = 1
           ORDER BY ra.rated_at DESC""",
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
