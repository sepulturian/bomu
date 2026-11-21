import os
import re
import base64
import hashlib
import json
import random
import tempfile
import time
import uuid
from datetime import date
from functools import wraps
from io import BytesIO
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import anthropic
from PIL import Image
from database import (
    init_db, close_request_db, get_all_bottles, get_bottle, add_bottle, update_bottle,
    delete_bottle, get_all_ingredients, set_all_ingredients_stock,
    add_ingredients_to_stock,
    get_recipe, get_all_recipes, set_rating, get_rating, get_all_ratings, get_favorites,
    get_auto_added_ingredients, is_auto_added,
    create_user, get_user_by_username, get_user,
    log_scan, scans_today, scans_today_global,
)
from matching import (
    get_recommendations, get_recommendations_grouped, get_one_away_grouped,
    matching_user_bottles, missing_ingredient_ids,
    classify_base_spirit, match_recipe, used_user_bottles,
    ONBOARD_BOTTLES, build_onboarding_data, is_name_matched,
)
from suggestions import get_suggestions

load_dotenv()

app = Flask(__name__)
# Secret key signs the session cookie (flash messages and logins).
# On Vercel this MUST be set explicitly; the fallback is only for local dev.
_secret = os.environ.get("SECRET_KEY")
if os.environ.get("VERCEL") and not _secret:
    raise RuntimeError("SECRET_KEY environment variable must be set on Vercel")
app.secret_key = _secret or "bomu-dev-key"

# Cap photo uploads at 10 MB so oversized uploads fail fast cleanly.
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

# Cookie hardening. SameSite=Lax means the login cookie isn't sent on
# cross-site form posts (a decent chunk of CSRF protection for free).
# SESSION_COOKIE_SECURE makes the cookie HTTPS-only, which would break
# local dev over http://192.168.x.x, so it's opt-in via env: the server's
# .env sets SECURE_COOKIES=1, the laptop doesn't.
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = os.environ.get("SECURE_COOKIES", "0") == "1"

# Per-user and global daily photo-scan caps: friends' scans bill Aaron's API key.
SCAN_DAILY_LIMIT = int(os.environ.get("SCAN_DAILY_LIMIT", "15"))
SCAN_GLOBAL_DAILY_LIMIT = int(os.environ.get("SCAN_GLOBAL_DAILY_LIMIT", "60"))

UPLOAD_FOLDER = (
    os.path.join(tempfile.gettempdir(), "bomu_uploads")
    if os.environ.get("VERCEL")
    else os.path.join(os.path.dirname(__file__), "uploads")
)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

init_db()


@app.teardown_appcontext
def _teardown_db(exc):
    close_request_db(exc)


@app.errorhandler(413)
def _file_too_large(_err):
    flash("That photo is too large (max 10 MB). Try a smaller photo.")
    target = request.path if request.path in ("/scan", "/scan-bulk") else url_for("bar")
    return redirect(target)


_auth_attempts = {}


def _client_ip():
    fwd = request.headers.get("X-Forwarded-For", "")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.remote_addr or "unknown"


def _check_rate_limit(bucket, limit, window_seconds=600):
    """Simple per-worker sliding-window IP rate limit for login/signup POSTs."""
    if app.config.get("TESTING"):
        return True
    now = time.monotonic()
    key = (bucket, _client_ip())
    recent = [t for t in _auth_attempts.get(key, ()) if now - t < window_seconds]
    if len(recent) >= limit:
        _auth_attempts[key] = recent
        return False
    recent.append(now)
    _auth_attempts[key] = recent
    return True


client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY") or "missing-key")


# --- Auth ---
#
# Session-cookie based. session["user_id"] is set on login/signup and cleared
# on logout. Every data route is wrapped in @login_required; logged-out
# visitors get bounced to /login.

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


def uid():
    """Current logged-in user's id. Only call inside @login_required views."""
    return session["user_id"]


@app.context_processor
def inject_current_user():
    """Make current_username available to every template (for the nav)."""
    username = session.get("username")
    if not username and session.get("user_id"):
        user = get_user(session["user_id"])
        if user:
            username = user["username"]
            session["username"] = username
    return {"current_username": username}


def _safe_next(target):
    """Only allow same-site relative redirect targets like '/recommend' --
    blocks open-redirect tricks like ?next=https://evil.com."""
    return target if target and target.startswith("/") and not target.startswith("//") else None


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if session.get("user_id"):
        return redirect(url_for("home"))
    if request.method == "POST":
        if not _check_rate_limit("signup", limit=8, window_seconds=600):
            flash("Too many signup attempts. Try again in a few minutes.")
            return render_template("signup.html", username=request.form.get("username", "").strip()), 429
        if request.form.get("website", "").strip():
            return redirect(url_for("login"))

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm", "")

        if not re.fullmatch(r"[A-Za-z0-9_.-]{2,30}", username):
            flash("Username should be 2-30 characters: letters, numbers, . _ -")
            return render_template("signup.html", username=username)
        if len(password) < 8:
            flash("Password needs at least 8 characters.")
            return render_template("signup.html", username=username)
        if password != confirm:
            flash("Passwords don't match.")
            return render_template("signup.html", username=username)

        user_id = create_user(username, generate_password_hash(password))
        if user_id is None:
            flash("That username is taken.")
            return render_template("signup.html", username=username)

        session["user_id"] = user_id
        session["username"] = username
        session.permanent = True
        flash(f"Welcome to Bomu, {username}!")
        return redirect(url_for("home"))
    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("home"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        if not _check_rate_limit("login", limit=15, window_seconds=600):
            flash("Too many login attempts. Try again in a few minutes.")
            return render_template("login.html", username=username), 429
        password = request.form.get("password", "")
        user = get_user_by_username(username)
        if user is None or not check_password_hash(user["password_hash"], password):
            flash("Wrong username or password.")
            return render_template("login.html", username=username)
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        session.permanent = True
        return redirect(_safe_next(request.args.get("next")) or url_for("home"))
    return render_template("login.html")


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("Logged out. See you at happy hour.")
    return redirect(url_for("login"))


def imperial_to_metric(measure, ingredient_name=""):
    """Convert a cocktail-style imperial measure to metric.
    Returns a clean ml string, or the original measure if it isn't convertible
    (e.g. 'dash', 'to taste', '1 cube') or if the ingredient is dry (sugar,
    salt, mint leaves) where ml conversion is misleading."""
    if not measure:
        return ""
    m = measure.strip().lower()
    # Things we don't convert -- already universal
    skip_keywords = (
        "dash", "drop", "splash", "pinch", "twist", "sprig", "leaf", "leaves",
        "cube", "taste", "garnish", "top", "fill", "rinse", "wedge", "slice",
        "peel", "zest", "rim",
    )
    if any(kw in m for kw in skip_keywords):
        return measure
    # Dry ingredients: don't convert tsp/tbsp to ml (misleading for solids)
    if ingredient_name:
        dry_keywords = (
            "sugar", "salt", "pepper", "mint leaves", "powder", "cinnamon",
            "nutmeg", "ginger ", "ground",
        )
        ing_lower = ingredient_name.lower()
        if any(d in ing_lower for d in dry_keywords):
            return measure
    # Match: optional whole, optional fraction, then unit
    match = re.match(r"^(\d+)?\s*(\d+/\d+)?\s*(oz|ounces?|tsp|tbsp|cups?)\b", m)
    if not match:
        return measure
    whole = int(match.group(1)) if match.group(1) else 0
    if match.group(2):
        num, den = match.group(2).split("/")
        whole += int(num) / int(den)
    unit = match.group(3)
    if unit.startswith("oz") or unit.startswith("ounce"):
        ml = whole * 30  # bartender rounding (true value 29.57)
    elif unit == "tsp":
        ml = whole * 5
    elif unit == "tbsp":
        ml = whole * 15
    elif unit.startswith("cup"):
        ml = whole * 240
    else:
        return measure
    if ml < 10:
        return f"{ml:.1f} ml"
    return f"{int(round(ml))} ml"


app.jinja_env.filters["metric"] = imperial_to_metric


def short_bottle_name(bottle):
    """Display-friendly version of a bottle name. Prefers brand if set,
    otherwise trims the full name to its first 1-2 words. Aims for <= 20 chars."""
    if bottle is None:
        return ""
    if hasattr(bottle, "keys"):
        # sqlite Row or dict
        try:
            brand = (bottle["brand"] if "brand" in bottle.keys() else "") or ""
            name = (bottle["name"] if "name" in bottle.keys() else "") or ""
        except (KeyError, TypeError):
            return str(bottle)
    else:
        return str(bottle)
    brand = brand.strip()
    name = name.strip()
    if brand and len(brand) <= 24:
        # "Martini" on its own looks like a cocktail name rather than vermouth
        if brand.lower() == "martini" and name and len(name) <= 24:
            return name
        return brand
    if name and len(name) <= 24:
        return name
    source = name or brand
    if source:
        # Build up whole words until we hit the cap, then drop any dangling
        # connector so we never emit stubs like "Valley of".
        words = source.split()
        kept = []
        for w in words:
            if len(" ".join(kept + [w])) > 22:
                break
            kept.append(w)
        connectors = {"of", "the", "and", "with", "de", "du", "la", "le", "no."}
        while kept and kept[-1].lower() in connectors:
            kept.pop()
        return " ".join(kept) if kept else words[0]
    return "?"


def clean_instructions(text):
    """Strip the rewrite marker tag if present."""
    if not text:
        return ""
    return text.replace("[BOMU_REWRITTEN_v1]", "").strip()


# Dev/internal tags that should never show on user-facing pages.
NOTE_DEV_TAGS = (
    "added by bitters audit",
    "rebuilt after DB corruption",
)

def clean_notes(notes):
    """Strip internal dev/audit tags from a note. If the only content was a
    dev tag, returns an empty string."""
    if not notes:
        return ""
    cleaned = notes
    for tag in NOTE_DEV_TAGS:
        cleaned = cleaned.replace(tag, "")
    return cleaned.strip().strip(",;").strip()


# Leading enumerator on a stored instruction line: "1. ", "2) ", "3 - ".
# The stored text carries these because the source recipes were written as
# numbered lists, and recipe.html then wraps the result in an <ol>, so every
# step rendered as "1. 1. Fill an old-fashioned glass with ice." Stripping here
# rather than in the data keeps the fix in one place and makes it apply to any
# future import that arrives pre-numbered.
#
# Deliberately requires a separator (. ) - ) after the digits AND whitespace
# after that, so a step legitimately opening with a measure ("2 oz gin into the
# shaker") is left alone. "1/2 lemon, muddled" is safe for the same reason.
_LEADING_ENUM = re.compile(r"^\s*\d{1,2}\s*[.)\-]\s+")


def instruction_steps(text):
    """Split instruction prose into a list of steps for numbered display.
    Prefers explicit line breaks; falls back to sentence boundaries. A recipe
    that's genuinely one sentence comes back as a single step and the
    template renders it as plain prose.

    Any leading "1." / "2)" the stored text carries is stripped, because the
    template numbers the steps itself."""
    text = clean_instructions(text)
    if not text:
        return []
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if len(lines) > 1:
        return [_LEADING_ENUM.sub("", l).strip() for l in lines]
    parts = re.split(r"(?<=[.!?])\s+", lines[0])
    return [_LEADING_ENUM.sub("", p).strip() for p in parts if p.strip()]


# Bottle types offered in the UI, as (stored value, label shown to the user).
# Sub-types matter to the matcher: sweet and dry vermouth are not
# interchangeable, and a rye drink should not accept a peaty Scotch. The
# "not sure" vermouth option is deliberate — matching.py treats the generic
# type as permissive, so picking it keeps today's looser behaviour rather than
# forcing a guess that could hide a drink the user can actually make.
BOTTLE_TYPE_CHOICES = [
    ("gin", "Gin"),
    ("vodka", "Vodka"),
    ("rum", "Rum"),
    ("tequila", "Tequila"),
    ("mezcal", "Mezcal"),
    ("whiskey", "Whiskey (other / blended)"),
    ("bourbon", "Bourbon"),
    ("scotch", "Scotch"),
    ("rye", "Rye"),
    ("irish", "Irish Whiskey"),
    ("brandy", "Brandy"),
    ("cognac", "Cognac"),
    ("vermouth_sweet", "Vermouth (sweet / rosso)"),
    ("vermouth_dry", "Vermouth (dry)"),
    ("vermouth", "Vermouth (not sure)"),
    ("amaro", "Amaro"),
    ("liqueur", "Liqueur"),
    ("other", "Other"),
]

BOTTLE_TYPE_LABELS = dict(BOTTLE_TYPE_CHOICES)
VALID_BOTTLE_TYPES = {value for value, _label in BOTTLE_TYPE_CHOICES}


def safe_bottle_type(value):
    """Coerce a submitted bottle type to something the matcher understands.

    Anything unrecognised becomes 'other', which is name-matched and therefore
    never fungibly satisfies a category requirement. The failure mode this
    prevents is the bulk-scan form defaulting an unreadable bottle to the first
    option in the dropdown -- Gin -- and the app then offering Martinis on a
    bottle nobody could identify. 'other' is the honest answer for "we don't
    know what this is"."""
    value = (value or "").strip()
    return value if value in VALID_BOTTLE_TYPES else "other"


def bottle_type_label(value):
    """Human-readable name for a stored bottle type.

    Also used on the one-away lists, where the value might not be a category at
    all — name-matched requirements report a raw ingredient name like
    "Cointreau" or "Amaro Averna". Those are already human-readable, so they're
    passed through untouched; only slug-looking values get tidied. Capitalising
    unconditionally would turn "Amaro Averna" into "Amaro averna"."""
    if not value:
        return ""
    if value in BOTTLE_TYPE_LABELS:
        return BOTTLE_TYPE_LABELS[value]
    if "_" in value:
        return value.replace("_", " ").capitalize()
    return value


def recipe_slug(name):
    """'Bee's Knees' -> 'bees_knees'. Used to match curated studio recipe images."""
    s = re.sub(r"['\u2018\u2019]", "", (name or "").lower())
    return re.sub(r"[^a-z0-9]+", "_", s).strip("_")


_RECIPE_IMAGE_MAP = None


def _recipe_image_map():
    """Cache local recipe image paths once per process so template rendering
    doesn't stat the filesystem four times per cocktail."""
    global _RECIPE_IMAGE_MAP
    if _RECIPE_IMAGE_MAP is not None:
        return _RECIPE_IMAGE_MAP
    recipes_dir = os.path.join(app.static_folder, "recipes")
    mapping = {}
    if os.path.isdir(recipes_dir):
        ext_rank = {".webp": 0, ".jpg": 1, ".jpeg": 2, ".png": 3}
        best = {}
        for fname in os.listdir(recipes_dir):
            stem, ext = os.path.splitext(fname)
            ext_lower = ext.lower()
            if ext_lower not in ext_rank:
                continue
            rank = ext_rank[ext_lower]
            if stem not in best or rank < best[stem][0]:
                best[stem] = (rank, f"recipes/{fname}")
        mapping = {stem: rel for stem, (_rank, rel) in best.items()}
    _RECIPE_IMAGE_MAP = mapping
    return mapping


def recipe_image_url(recipe):
    """Prefer curated studio recipe assets in static/recipes/ when present,
    falling back to recipe.image_url, then None."""
    keys = recipe.keys() if recipe and hasattr(recipe, "keys") else ()
    name = recipe["name"] if "name" in keys else ""
    slug = recipe_slug(name)
    rel = _recipe_image_map().get(slug) if slug else None
    if rel:
        return url_for("static", filename=rel)
    img_url = recipe["image_url"] if "image_url" in keys else None
    return img_url or None


def glass_kind(glass):
    """Normalize recipe.glass into one of five silhouette keys:
    coupe, rocks, highball, flute, hurricane."""
    g = (glass or "").lower()
    if any(k in g for k in ("coupe", "martini", "cocktail", "nick", "margarita")):
        return "coupe"
    if any(k in g for k in ("highball", "collins", "pint", "mason", "copper mug", "mule", "pilsner", "parfait")):
        return "highball"
    if any(k in g for k in ("flute", "champagne", "wine")):
        return "flute"
    if any(k in g for k in ("hurricane", "tiki", "goblet", "snifter", "pitcher", "punch")):
        return "hurricane"
    return "rocks"


def format_glass_label(glass):
    """Normalize inconsistent glassware strings for tidy display."""
    if not glass:
        return "Cocktail glass"
    g = glass.strip()
    gl = g.lower()
    mapping = {
        "old-fashioned glass": "Rocks glass",
        "old fashioned": "Rocks glass",
        "rocks glass": "Rocks glass",
        "martini glass": "Cocktail glass",
        "cocktail glass": "Cocktail glass",
        "coupe": "Coupe glass",
        "coupe glass": "Coupe glass",
        "highball glass": "Highball glass",
        "collins glass": "Collins glass",
        "champagne flute": "Champagne flute",
        "nick and nora glass": "Nick & Nora",
    }
    if gl in mapping:
        return mapping[gl]
    return g[0].upper() + g[1:]


def explore_base_spirit(recipe_data):
    """Identify the primary spirit bucket for Explore, prioritizing distilled
    base spirits over modifiers like sweet/dry vermouth so Boulevardier/Manhattan
    sit under Whiskey rather than Vermouth."""
    primary_map = {
        "gin": "Gin",
        "vodka": "Vodka",
        "rum": "Rum",
        "tequila": "Tequila & Mezcal",
        "mezcal": "Tequila & Mezcal",
        "whiskey": "Whiskey",
        "bourbon": "Whiskey",
        "scotch": "Whiskey",
        "rye": "Whiskey",
        "irish": "Whiskey",
        "brandy": "Brandy & Cognac",
        "cognac": "Brandy & Cognac",
    }
    for ing in recipe_data.get("ingredients", []):
        if ing.get("requirement_type") != "bottle_type":
            continue
        bt = (ing.get("bottle_type") or "").lower()
        if bt in primary_map:
            return primary_map[bt]
    return classify_base_spirit(recipe_data)


def classify_drink_style(recipe_data):
    """Derive a drink style bucket dynamically from ingredients and glassware."""
    ing_names = " ".join(
        (i.get("raw_name") or "").lower()
        for i in recipe_data.get("ingredients", [])
    )
    glass = (recipe_data.get("recipe", {}).get("glass") or "").lower()
    if any(k in ing_names for k in (
        "heavy cream", "light cream", "coconut", "vanilla ice cream", "ice cream",
        "milk", "half-and-half", "coffee", "espresso", "baileys", "irish cream", "kahlua",
    )):
        return "Rich & Creamy"
    if any(k in ing_names for k in ("champagne", "prosecco", "sparkling wine", "cava")) or "flute" in glass:
        return "Bubbly & Spritz"
    if any(k in ing_names for k in (
        "tonic", "soda water", "club soda", "ginger beer", "ginger ale",
        "cola", "grapefruit soda", "tomato juice", "root beer",
    )) or any(k in glass for k in ("highball", "collins", "copper mug")):
        return "Highball & Tall"
    if any(k in ing_names for k in (
        "lemon juice", "lime juice", "grapefruit juice", "pineapple juice",
        "orange juice", "cranberry juice", "sour mix", "sweet and sour",
    )):
        return "Sour & Citrus"
    return "Spirit-Forward"


app.jinja_env.globals["BOTTLE_TYPE_CHOICES"] = BOTTLE_TYPE_CHOICES
app.jinja_env.filters["type_label"] = bottle_type_label
app.jinja_env.filters["short_name"] = short_bottle_name
app.jinja_env.filters["clean_instructions"] = clean_instructions
app.jinja_env.filters["steps"] = instruction_steps
app.jinja_env.filters["clean_notes"] = clean_notes
app.jinja_env.filters["suggestions"] = get_suggestions
app.jinja_env.filters["recipe_slug"] = recipe_slug
app.jinja_env.filters["recipe_image"] = recipe_image_url
app.jinja_env.filters["glass_kind"] = glass_kind
app.jinja_env.filters["glass_label"] = format_glass_label


# ---------------------------------------------------------------------------
# "One ingredient away" spotlight on Tonight
# ---------------------------------------------------------------------------

# Headline copy. Each line is a list of segments; the string "{drink}" is
# replaced with "a Mojito" / "an Aviation", "{Drink}" with the same at sentence
# start, and "{name}" with the bare drink name. Built as segments, not HTML,
# so nothing here ever needs |safe. {unit} is "ingredient" or "bottle".
#
# The ingredient itself is deliberately NOT in the headline: it sits in a pill
# on the next line, so its casing ("Fresh mint", "Angostura bitters") never has
# to survive the middle of a sentence.
SPOTLIGHT_LINES = [
    "One {unit} stands between you and {drink}.",
    "{Drink} is closer than you think.",
    "So close to {drink} you can almost taste it.",
    "Your {name} is waiting on one thing.",
]

# Friendlier names for fungible bottle categories in a sentence-ish context.
# Everything else falls back to type_label, and name-matched bottles already
# carry a product name ("Cointreau").
_SPOTLIGHT_BOTTLE_NAMES = {
    "vermouth_dry": "Dry vermouth",
    "vermouth_sweet": "Sweet vermouth",
    "vermouth": "Vermouth",
    "whiskey": "Whiskey",
    "irish": "Irish whiskey",
}


def _with_article(name):
    if name.lower().startswith("the "):
        return name
    return ("an " if name[:1].lower() in "aeiou" else "a ") + name


def spotlight_headline(spot, day_number):
    """Pick today's headline for the spotlight as [(text, is_drink), ...].

    Rotates by date so it stays put through an evening but doesn't go stale."""
    drink = spot["headline_drink"]["name"]
    line = SPOTLIGHT_LINES[day_number % len(SPOTLIGHT_LINES)]
    unit = "ingredient" if spot["kind"] == "ingredient" else "bottle"
    article = _with_article(drink)
    drink_phrase = {
        "{drink}": article,
        "{Drink}": article[:1].upper() + article[1:],
        "{name}": drink,
    }
    segments = []
    for part in re.split(r"(\{drink\}|\{Drink\}|\{name\})", line.replace("{unit}", unit)):
        if part in drink_phrase:
            # Keep the article as plain text so only the drink name is styled.
            text = drink_phrase[part]
            prefix = text[: len(text) - len(drink)]
            if prefix:
                segments.append((prefix, False))
            segments.append((drink, True))
        elif part:
            segments.append((part, False))
    return segments


def spotlight_label(spot):
    if spot["kind"] == "ingredient" or spot["name_matched"]:
        return spot["name"]
    return _SPOTLIGHT_BOTTLE_NAMES.get(spot["name"]) or bottle_type_label(spot["name"])


def spotlight_add_url(spot):
    """Where 'Add to my bar' goes for a bottle: the My Bar add sheet, with the
    type preselected and, for name-matched bottles, the name prefilled. The
    name matters there: a name-matched requirement only matches a bottle whose
    NAME contains the key, so 'Cointreau' typed as the name is what makes the
    drinks appear."""
    args = {"sheet": "add", "type": safe_bottle_type(spot["bottle_type"])}
    if spot["name_matched"]:
        args["name"] = spot["name"]
    return url_for("bar", **args)
app.jinja_env.filters["drink_style"] = classify_drink_style
app.jinja_env.tests["auto_added"] = is_auto_added


def prepare_image(image_path, max_dim=1568, max_bytes=4_500_000):
    """Resize and re-encode an image so it fits under Claude's 5 MB vision limit.
    Returns (base64_data, media_type)."""
    img = Image.open(image_path)
    # JPEG can't handle alpha channels or palette modes, so flatten those
    if img.mode in ("RGBA", "P", "LA"):
        img = img.convert("RGB")
    elif img.mode != "RGB":
        img = img.convert("RGB")
    # Shrink so longest side <= max_dim (preserves aspect ratio)
    if max(img.size) > max_dim:
        img.thumbnail((max_dim, max_dim))
    # Save to JPEG, drop quality if still too big
    quality = 90
    while True:
        buf = BytesIO()
        img.save(buf, format="JPEG", quality=quality, optimize=True)
        data = buf.getvalue()
        if len(data) <= max_bytes or quality <= 50:
            break
        quality -= 10
    return base64.b64encode(data).decode("utf-8"), "image/jpeg"


SCANNER_CLASSIFICATION_RULES = """IMPORTANT - only use a base spirit type (gin, vodka, rum, tequila, mezcal,
whiskey, bourbon, scotch, brandy, cognac) for a full-strength bottle of that
spirit, typically 30% alcohol or higher.

Use "other" for anything that merely contains or is flavoured with a spirit:
- Ready-to-drink (RTD) products, premixed cans, hard seltzers, alcopops and
  coolers (e.g. "Vodka Cruiser", "Smirnoff Ice", "Jack Daniel's & Cola")
- Beer, cider, wine, prosecco, champagne, sake, mead
- Cream liqueurs and low-alcohol flavoured products

A pineapple vodka cooler is NOT vodka. Tagging it as vodka makes the app tell
someone they can make a Martini out of an alcopop.

WHISKEY SUB-TYPES - be specific when the label is clear:
- "rye" if the label says rye
- "irish" if the label says Irish, or it is a known Irish brand (Jameson,
  Redbreast, Bushmills, Tullamore, Powers, Green Spot)
- "bourbon" if the label says bourbon
- "scotch" if it is Scotch whisky
- "whiskey" for anything else, including Japanese, Canadian and blends you
  cannot place. Do not guess: "whiskey" is the safe answer.

VERMOUTH - sweet and dry are different products, not a spectrum:
- "vermouth_sweet" for rosso, rossa, rojo, rouge, red or sweet, and for
  Carpano Antica and Punt e Mes
- "vermouth_dry" for dry or extra dry
- "vermouth" only if you genuinely cannot tell from the label"""


def scan_bottle_image(image_path):
    """Send a bottle image to Claude vision and get back bottle details."""
    image_data, media_type = prepare_image(image_path)

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {"type": "base64", "media_type": media_type, "data": image_data}
                },
                {
                    "type": "text",
                    "text": f"""Look at this image of a bottle. Identify the bottle and return ONLY a JSON object with these fields:
- "name": the full product name (e.g. "Hendrick's Gin")
- "type": one of: gin, vodka, rum, tequila, mezcal, whiskey, bourbon, scotch, rye, irish, brandy, cognac, vermouth_sweet, vermouth_dry, vermouth, amaro, liqueur, other
- "brand": the brand name (e.g. "Hendrick's")

{SCANNER_CLASSIFICATION_RULES}

If you cannot identify the bottle, return: {{"name": "", "type": "", "brand": "", "error": "Could not identify this bottle"}}

Return ONLY the JSON, no other text."""
                }
            ]
        }]
    )

    try:
        result = json.loads(message.content[0].text)
    except json.JSONDecodeError:
        text = message.content[0].text
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            result = json.loads(text[start:end])
        else:
            result = {"name": "", "type": "", "brand": "", "error": "Could not parse response"}
    return result


def scan_shelf_image(image_path):
    """Send a shelf/group image to Claude vision and identify multiple bottles."""
    image_data, media_type = prepare_image(image_path)

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {"type": "base64", "media_type": media_type, "data": image_data}
                },
                {
                    "type": "text",
                    "text": f"""Look at this image showing multiple bottles. Identify as many bottles as you can and return ONLY a JSON array of objects, each with:
- "name": the full product name
- "type": one of: gin, vodka, rum, tequila, mezcal, whiskey, bourbon, scotch, rye, irish, brandy, cognac, vermouth_sweet, vermouth_dry, vermouth, amaro, liqueur, other
- "brand": the brand name
- "confidence": "high" if you can clearly read the label, "low" if you're guessing

{SCANNER_CLASSIFICATION_RULES}

If you cannot identify any bottles, return: [{{"name": "", "type": "", "brand": "", "confidence": "low", "error": "Could not identify bottles"}}]

Return ONLY the JSON array, no other text."""
                }
            ]
        }]
    )

    try:
        result = json.loads(message.content[0].text)
    except json.JSONDecodeError:
        text = message.content[0].text
        start = text.find("[")
        end = text.rfind("]") + 1
        if start != -1 and end > start:
            result = json.loads(text[start:end])
        else:
            result = []
    return result


@app.route("/sw.js")
def service_worker():
    """Serve the service worker from the site root.
    A service worker's scope is limited to the path it's served from, so
    /static/sw.js could only control /static/* pages. Serving it at /sw.js
    gives it scope over the whole app."""
    return send_from_directory(app.static_folder, "sw.js", mimetype="application/javascript")


def pick_featured_pour(makeable, ratings, user_id, day_seed=None):
    """Pick a daily-rotating Featured Pour from makeable drinks, skipping
    disliked drinks when alternatives exist and avoiding consecutive-day repeats."""
    pool = [r for r in makeable if ratings.get(r["recipe"]["id"], 0) != -1] or list(makeable)
    if not pool:
        return None
    img_pool = [r for r in pool if recipe_image_url(r["recipe"])] or pool
    n = len(img_pool)
    if n == 1:
        return img_pool[0]
    if day_seed is None:
        day_seed = date.today().toordinal()
    if n == 2:
        pair = sorted(img_pool, key=lambda r: r["recipe"]["id"])
        return pair[day_seed % 2]

    cycle = day_seed // n
    pos = day_seed % n

    def raw_order(c):
        return sorted(
            img_pool,
            key=lambda r: hashlib.md5(f"{c}:{user_id}:{r['recipe']['id']}".encode()).hexdigest(),
        )

    order = raw_order(cycle)
    prev_last = raw_order(cycle - 1)[-1]
    if order[0]["recipe"]["id"] == prev_last["recipe"]["id"]:
        order[0], order[1] = order[1], order[0]
    return order[pos]


@app.route("/")
@login_required
def home():
    user_id = uid()
    grouped = request.args.get("group") == "spirit"
    if grouped:
        recs = get_recommendations_grouped(user_id, max_per_group=50)
    else:
        recs = get_recommendations(user_id, max_makeable=200, max_one_away=12)
    bottles = recs["bottles"]
    all_ingredients = recs["ingredients"]
    stocked_count = sum(1 for i in all_ingredients if i["in_stock"])
    onboard_data = (
        build_onboarding_data(all_ingredients, get_all_recipes())
        if len(bottles) == 0
        else None
    )

    featured = pick_featured_pour(recs["makeable"], recs["ratings"], user_id)

    spot = recs.get("spotlight")
    spot_view = None
    if spot:
        spot_view = {
            "headline": spotlight_headline(spot, date.today().toordinal()),
            "label": spotlight_label(spot),
            "add_url": spotlight_add_url(spot) if spot["kind"] == "bottle" else None,
        }

    return render_template(
        "tonight.html",
        recs=recs,
        grouped=grouped,
        featured=featured,
        spot=spot,
        spot_view=spot_view,
        kitchen_check=recs.get("kitchen_check"),
        onboard_data=onboard_data,
        bottle_count=len(bottles),
        stocked_count=stocked_count,
    )


@app.route("/quick-setup", methods=["POST"])
@login_required
def quick_setup():
    """Save starter bottles + kitchen mixers from Tonight's empty-bar setup."""
    user_id = uid()
    by_key = {b["key"]: b for b in ONBOARD_BOTTLES}
    existing = {
        ((b["name"] or "").lower(), b["type"])
        for b in get_all_bottles(user_id)
    }

    added_bottles = 0
    for key in request.form.getlist("bottle"):
        spec = by_key.get(key)
        if not spec:
            continue
        sig = (spec["name"].lower(), spec["type"])
        if sig in existing:
            continue
        add_bottle(user_id, spec["name"], spec["type"], "")
        existing.add(sig)
        added_bottles += 1

    valid_ing_ids = {i["id"] for i in get_all_ingredients(user_id)}
    ing_ids = []
    for raw_id in request.form.getlist("ingredient"):
        try:
            iid = int(raw_id)
        except ValueError:
            continue
        if iid in valid_ing_ids and iid not in ing_ids:
            ing_ids.append(iid)
    if ing_ids:
        add_ingredients_to_stock(user_id, ing_ids)

    if added_bottles and ing_ids:
        flash("Your bar is set up!")
    elif added_bottles:
        flash(f"Added {added_bottles} bottle{'s' if added_bottles != 1 else ''} to your bar!")
    elif ing_ids:
        flash("Saved your kitchen mixers!")
    return redirect(url_for("home"))


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST":
        name = request.form["name"]
        bottle_type = safe_bottle_type(request.form.get("type"))
        brand = request.form.get("brand", "")
        add_bottle(uid(), name, bottle_type, brand)
        flash(f"Added {name} to your bar!")
        if request.form.get("from_scan") == "1" and not any(i["in_stock"] for i in get_all_ingredients(uid())):
            return redirect(url_for("home"))
        return redirect(url_for("bar"))
    return render_template("add_bottle.html")


def _save_upload(photo):
    """Save an uploaded photo under a unique name so two users uploading
    'image.jpg' at the same moment can't clobber each other's file."""
    filename = f"{uuid.uuid4().hex}-{secure_filename(photo.filename)}"
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    photo.save(filepath)
    return filepath


def _scan_allowed():
    """Enforce per-user and global daily scan caps. Returns None if allowed,
    or a friendly message if either limit is reached."""
    if scans_today_global() >= SCAN_GLOBAL_DAILY_LIMIT:
        return ("Our bottle scanner has hit today's shared limit -- "
                "add bottles manually for now, or try scanning again tomorrow.")
    used = scans_today(uid())
    if used >= SCAN_DAILY_LIMIT:
        return (f"You've used all {SCAN_DAILY_LIMIT} scans for today -- "
                "the robot bartender needs a nap. Try again tomorrow, "
                "or add bottles manually.")
    return None


@app.route("/scan", methods=["GET", "POST"])
@login_required
def scan():
    if request.method == "POST":
        if "photo" not in request.files:
            flash("No photo selected.")
            return redirect(url_for("scan"))
        photo = request.files["photo"]
        if photo.filename == "":
            flash("No photo selected.")
            return redirect(url_for("scan"))

        capped = _scan_allowed()
        if capped:
            flash(capped)
            return redirect(url_for("scan"))

        filepath = _save_upload(photo)
        try:
            result = scan_bottle_image(filepath)
        except Exception:
            # Full details go to the server log; the user gets a clean message
            # (raw exception text can contain internal details like API errors).
            app.logger.exception("Bottle scan failed")
            flash("Couldn't scan that photo. Give it another try in a minute.")
            return redirect(url_for("scan"))
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)

        if result.get("error"):
            flash(result["error"])
            return redirect(url_for("scan"))

        log_scan(uid())
        return render_template("confirm_bottle.html", bottle=result)

    return render_template("scan.html")


@app.route("/scan-bulk", methods=["GET", "POST"])
@login_required
def scan_bulk():
    if request.method == "POST":
        if "photo" not in request.files:
            flash("No photo selected.")
            return redirect(url_for("scan_bulk"))
        photo = request.files["photo"]
        if photo.filename == "":
            flash("No photo selected.")
            return redirect(url_for("scan_bulk"))

        capped = _scan_allowed()
        if capped:
            flash(capped)
            return redirect(url_for("scan_bulk"))

        filepath = _save_upload(photo)
        try:
            results = scan_shelf_image(filepath)
        except Exception:
            app.logger.exception("Shelf scan failed")
            flash("Couldn't scan that photo. Give it another try in a minute.")
            return redirect(url_for("scan_bulk"))
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)

        if not results:
            flash("Could not identify any bottles in the photo.")
            return redirect(url_for("scan_bulk"))

        log_scan(uid())
        return render_template("confirm_bulk.html", bottles=results)

    return render_template("scan_bulk.html")


@app.route("/confirm-bulk", methods=["POST"])
@login_required
def confirm_bulk():
    added = 0
    i = 0
    while True:
        name = request.form.get(f"name_{i}")
        if name is None:
            break
        if request.form.get(f"add_{i}"):
            bottle_type = safe_bottle_type(request.form.get(f"type_{i}"))
            brand = request.form.get(f"brand_{i}", "")
            add_bottle(uid(), name, bottle_type, brand)
            added += 1
        i += 1
    flash(f"Added {added} bottle{'s' if added != 1 else ''} to your bar!")
    if added and not any(i["in_stock"] for i in get_all_ingredients(uid())):
        return redirect(url_for("home"))
    return redirect(url_for("bar"))


@app.route("/checklist", methods=["GET", "POST"])
@login_required
def checklist():
    if request.method == "POST":
        checked_ids = list(dict.fromkeys(int(x) for x in request.form.getlist("ingredient")))
        set_all_ingredients_stock(uid(), checked_ids)
        if request.headers.get("X-Requested-With") == "fetch":
            return {"ok": True, "stocked_count": len(checked_ids)}, 200
        flash("Mixers saved!")
        return redirect(url_for("bar", tab="mixers"))
    return redirect(url_for("bar", tab="mixers"))


@app.route("/bar")
@login_required
def bar():
    user_id = uid()
    active_tab = request.args.get("tab", "bottles")
    if active_tab not in ("bottles", "mixers"):
        active_tab = "bottles"
    sheet_open = request.args.get("sheet") == "add"
    q = request.args.get("q", "").strip()
    grouped = request.args.get("group") == "spirit"

    all_bottles = get_all_bottles(user_id)
    if q:
        ql = q.lower()
        bottles = [
            b for b in all_bottles
            if ql in (b["name"] or "").lower()
            or ql in (b["brand"] or "").lower()
            or ql in bottle_type_label(b["type"]).lower()
        ]
    else:
        bottles = list(all_bottles)

    grouped_bottles = []
    if grouped and bottles:
        buckets = {}
        for b in bottles:
            lbl = bottle_type_label(b["type"]) or "Other"
            buckets.setdefault(lbl, []).append(b)
        grouped_bottles = sorted(buckets.items(), key=lambda kv: kv[0].lower())

    ingredients = get_all_ingredients(user_id)
    stocked = [i for i in ingredients if i["in_stock"]]
    new_ingredients = get_auto_added_ingredients(user_id, only_unstocked=True, ingredients=ingredients)

    return render_template(
        "my_bar.html",
        active_tab=active_tab,
        sheet_open=sheet_open,
        # From the Tonight spotlight: preselect a type / prefill a name. Type is
        # only passed through if valid, so a junk query string selects nothing.
        prefill_type=(request.args.get("type") if request.args.get("type") in VALID_BOTTLE_TYPES else ""),
        prefill_name=request.args.get("name", "")[:120],
        q=q,
        grouped=grouped,
        bottles=bottles,
        grouped_bottles=grouped_bottles,
        total_count=len(all_bottles),
        filtered_count=len(bottles),
        ingredients=ingredients,
        stocked_ingredients=stocked,
        stocked_count=len(stocked),
        total_ingredients=len(ingredients),
        new_ingredients=new_ingredients,
        new_ingredient_count=len(new_ingredients),
    )


@app.route("/recommend")
@login_required
def recommend():
    return redirect(url_for("home", **request.args))


@app.route("/explore")
def explore():
    user_id = session.get("user_id")
    logged_in = bool(user_id)
    if logged_in:
        bottles = get_all_bottles(user_id)
        stocked = {i["name"].lower() for i in get_all_ingredients(user_id) if i["in_stock"]}
        ratings = get_all_ratings(user_id)
    else:
        bottles = []
        stocked = set()
        ratings = {}
    all_recipes = get_all_recipes()

    entries = []
    spirits_seen = set()
    styles_seen = set()
    makeable_total = 0
    one_away_total = 0

    for r in all_recipes:
        if logged_in:
            status, missing = match_recipe(r, bottles, stocked)
            if status == "makeable":
                makeable_total += 1
                your_bottles = [short_bottle_name(b) for b in used_user_bottles(r, bottles)]
            else:
                if status == "one_away":
                    one_away_total += 1
                your_bottles = []
        else:
            status, missing, your_bottles = "public", [], []
        spirit_group = explore_base_spirit(r)
        style_group = classify_drink_style(r)
        spirits_seen.add(spirit_group)
        styles_seen.add(style_group)
        ing_text = " ".join(
            f"{i.get('raw_name') or ''} {i.get('ingredient_name') or ''}".lower()
            for i in r["ingredients"]
        )
        entries.append({
            "recipe": r["recipe"],
            "status": status,
            "missing": [bottle_type_label(m["name"]) for m in missing],
            "spirit_group": spirit_group,
            "style_group": style_group,
            "your_bottles": your_bottles,
            "thumb": ratings.get(r["recipe"]["id"], 0),
            "search_text": f"{r['recipe']['name'].lower()} {ing_text} {spirit_group.lower()} {style_group.lower()}",
        })

    if logged_in:
        order_map = {"makeable": 0, "one_away": 1, "not_close": 2}
        entries.sort(key=lambda e: (order_map.get(e["status"], 9), e["recipe"]["name"].lower()))
    else:
        entries.sort(key=lambda e: e["recipe"]["name"].lower())

    preferred_spirits = [
        "Gin", "Whiskey", "Rum", "Tequila & Mezcal", "Vodka",
        "Brandy & Cognac", "Liqueur-led", "Specialty", "Vermouth", "Other",
    ]
    spirit_filters = [s for s in preferred_spirits if s in spirits_seen]
    preferred_styles = [
        "Sour & Citrus", "Spirit-Forward", "Highball & Tall",
        "Bubbly & Spritz", "Rich & Creamy",
    ]
    style_filters = [s for s in preferred_styles if s in styles_seen]

    return render_template(
        "explore.html",
        logged_in=logged_in,
        entries=entries,
        total_count=len(entries),
        makeable_total=makeable_total,
        one_away_total=one_away_total,
        spirit_filters=spirit_filters,
        style_filters=style_filters,
    )


@app.route("/stock-add", methods=["POST"])
@login_required
def stock_add():
    """Quick-add for the mixer nudge and one-tap stocking. Adds only, never
    clears, so it can't undo whatever the user already ticked on Mixers."""
    next_url = _safe_next(request.form.get("next"))
    try:
        ids = [int(x) for x in request.form.getlist("ingredient")]
    except ValueError:
        ids = []
    if ids:
        user_id = uid()
        by_id = {i["id"]: i["name"] for i in get_all_ingredients(user_id)}
        valid_ids = [i for i in dict.fromkeys(ids) if i in by_id]
        if valid_ids:
            add_ingredients_to_stock(user_id, valid_ids)
            flash("Added to your bar: " + ", ".join(by_id[i] for i in valid_ids))
    return redirect(next_url or url_for("home"))


@app.route("/one-away")
@login_required
def one_away():
    groups = get_one_away_grouped(uid())
    for g in groups:
        if g["missing"].get("type") == "bottle_type" and g.get("bottle_type"):
            args = {"sheet": "add", "type": safe_bottle_type(g["bottle_type"])}
            if g.get("name_matched"):
                args["name"] = g["missing"]["name"]
            g["add_url"] = url_for("bar", **args)
        else:
            g["add_url"] = None
    return render_template("one_away.html", groups=groups)


@app.route("/saved")
@login_required
def saved():
    user_id = uid()
    bottles = get_all_bottles(user_id)
    stocked = {i["name"].lower() for i in get_all_ingredients(user_id) if i["in_stock"]}
    ratings = get_all_ratings(user_id)
    fav_rows = get_favorites(user_id)
    fav_ids = {f["id"] for f in fav_rows}

    all_by_id = {r["recipe"]["id"]: r for r in get_all_recipes()}

    favorites_enriched = []
    for f in fav_rows:
        rdata = all_by_id.get(f["id"])
        if rdata:
            status, missing = match_recipe(rdata, bottles, stocked)
            your_bottles = [short_bottle_name(b) for b in used_user_bottles(rdata, bottles)] if status == "makeable" else []
            favorites_enriched.append({
                "recipe": rdata["recipe"],
                "status": status,
                "missing": [bottle_type_label(m["name"]) for m in missing],
                "your_bottles": your_bottles,
                "rated_at": f.get("rated_at"),
            })

    disliked_enriched = []
    for rid, thumb in ratings.items():
        if thumb == -1 and rid not in fav_ids:
            rdata = all_by_id.get(rid)
            if rdata:
                status, missing = match_recipe(rdata, bottles, stocked)
                disliked_enriched.append({
                    "recipe": rdata["recipe"],
                    "status": status,
                    "missing": [bottle_type_label(m["name"]) for m in missing],
                })
    disliked_enriched.sort(key=lambda d: d["recipe"]["name"].lower())

    return render_template(
        "saved.html",
        favorites=favorites_enriched,
        disliked=disliked_enriched,
    )


@app.route("/favorites")
@login_required
def favorites():
    return redirect(url_for("saved"))


@app.route("/surprise")
@login_required
def surprise():
    """Pick a random makeable drink and send the user straight to its recipe.
    Light bias toward unrated + thumbs-up drinks (skip thumbs-down) so the
    surprise doesn't keep landing on a drink Aaron already said he disliked."""
    recs = get_recommendations(uid(), max_makeable=200, max_one_away=0)
    pool = [r for r in recs["makeable"]
            if recs["ratings"].get(r["recipe"]["id"], 0) != -1]
    if not pool:
        pool = recs["makeable"]
    if not pool:
        flash("Nothing makeable yet. Add some bottles or check off mixers.")
        return redirect(url_for("home"))
    pick = random.choice(pool)
    return redirect(url_for("recipe", recipe_id=pick["recipe"]["id"]))


@app.route("/recipe/<int:recipe_id>")
def recipe(recipe_id):
    user_id = session.get("user_id")
    logged_in = bool(user_id)
    r = get_recipe(recipe_id)
    if not r:
        flash("Recipe not found.")
        return redirect(url_for("home") if logged_in else url_for("explore"))

    if logged_in:
        bottles = get_all_bottles(user_id)
        ingredients_db = get_all_ingredients(user_id)
        stocked = {i["name"].lower() for i in ingredients_db if i["in_stock"]}
        ids_by_name = {i["name"].lower(): i["id"] for i in ingredients_db}

        # For each ingredient, figure out which (if any) of the user's bottles satisfies it
        bottle_hints = {}
        for ing in r["ingredients"]:
            matches = matching_user_bottles(ing, bottles)
            if matches:
                bottle_hints[ing["id"]] = matches

        # Which ingredients can't be fulfilled by the user's current bar?
        missing_ids = missing_ingredient_ids(r, bottles, stocked)

        missing_actions = {}
        for ing in r["ingredients"]:
            if ing["id"] not in missing_ids:
                continue
            if ing["requirement_type"] == "ingredient" and ing["ingredient_name"]:
                iid = ids_by_name.get(ing["ingredient_name"].lower())
                if iid is not None:
                    missing_actions[ing["id"]] = {"kind": "ingredient", "ingredient_id": iid}
            elif ing["requirement_type"] == "bottle_type" and ing["bottle_type"]:
                args = {"sheet": "add", "type": safe_bottle_type(ing["bottle_type"])}
                if is_name_matched(ing) and ing.get("raw_name"):
                    args["name"] = ing["raw_name"]
                missing_actions[ing["id"]] = {"kind": "bottle", "add_url": url_for("bar", **args)}

        enhancements = r.get("enhancements", [])
        enhancement_have = {
            e["id"]
            for e in enhancements
            if e["ingredient_name"] and e["ingredient_name"].lower() in stocked
        }
        rating = get_rating(user_id, recipe_id)
    else:
        bottle_hints = {}
        missing_ids = set()
        missing_actions = {}
        enhancements = r.get("enhancements", [])
        enhancement_have = set()
        rating = 0

    return render_template(
        "recipe.html",
        logged_in=logged_in,
        recipe=r["recipe"],
        ingredients=r["ingredients"],
        bottle_hints=bottle_hints,
        missing_ids=missing_ids,
        missing_actions=missing_actions,
        enhancements=enhancements,
        enhancement_have=enhancement_have,
        rating=rating,
    )


@app.route("/rate/<int:recipe_id>", methods=["POST"])
@login_required
def rate(recipe_id):
    """Toggle thumb up or down for a recipe.
    Click the same thumb you already gave -> it clears (back to unrated)."""
    next_url = _safe_next(request.form.get("next"))
    try:
        desired = int(request.form.get("thumb", 0))
    except ValueError:
        desired = 0
    if desired not in (1, -1):
        flash("Invalid rating.")
        return redirect(next_url or url_for("recipe", recipe_id=recipe_id))
    current = get_rating(uid(), recipe_id)
    if current == desired:
        set_rating(uid(), recipe_id, 0)  # toggle off
    else:
        set_rating(uid(), recipe_id, desired)
    return redirect(next_url or url_for("recipe", recipe_id=recipe_id))


@app.route("/edit/<int:bottle_id>", methods=["GET", "POST"])
@login_required
def edit(bottle_id):
    bottle = get_bottle(bottle_id, uid())
    if not bottle:
        flash("Bottle not found.")
        return redirect(url_for("bar"))
    if request.method == "POST":
        name = request.form["name"]
        bottle_type = safe_bottle_type(request.form.get("type"))
        brand = request.form.get("brand", "")
        update_bottle(bottle_id, uid(), name, bottle_type, brand)
        flash(f"Updated {name}!")
        return redirect(url_for("bar"))
    return render_template("edit_bottle.html", bottle=bottle)


@app.route("/delete/<int:bottle_id>", methods=["POST"])
@login_required
def delete(bottle_id):
    bottle = get_bottle(bottle_id, uid())
    if bottle:
        delete_bottle(bottle_id, uid())
        flash(f"Deleted {bottle['name']}.")
    return redirect(url_for("bar"))


if __name__ == "__main__":
    # This block only runs for local dev (`python app.py` on the laptop).
    # Production hosts run the app through gunicorn instead, which imports
    # `app` directly and never executes this block, so debug stays local-only.
    # FLASK_DEBUG=0 lets you test prod-like behavior locally if ever needed.
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    port = int(os.environ.get("PORT", "5000"))
    app.run(debug=debug, host="0.0.0.0", port=port)