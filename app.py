import os
import re
import base64
import json
import random
import uuid
from functools import wraps
from io import BytesIO
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import anthropic
from PIL import Image
from database import (
    init_db, get_all_bottles, get_bottle, add_bottle, update_bottle,
    delete_bottle, get_all_ingredients, set_all_ingredients_stock,
    get_recipe, set_rating, get_rating, get_all_ratings, get_favorites,
    get_auto_added_ingredients, is_auto_added,
    create_user, get_user_by_username, get_user,
    log_scan, scans_today,
)
from matching import (
    get_recommendations, get_recommendations_grouped, get_one_away_grouped,
    matching_user_bottles, missing_ingredient_ids,
)
from suggestions import get_suggestions

load_dotenv()

app = Flask(__name__)
# Secret key signs the session cookie (flash messages, and later: logins).
# On a public host this MUST be a real secret from an env var; the fallback
# is only for local dev on the laptop.
app.secret_key = os.environ.get("SECRET_KEY", "bomu-dev-key")

# Cookie hardening. SameSite=Lax means the login cookie isn't sent on
# cross-site form posts (a decent chunk of CSRF protection for free).
# SESSION_COOKIE_SECURE makes the cookie HTTPS-only, which would break
# local dev over http://192.168.x.x, so it's opt-in via env: the server's
# .env sets SECURE_COOKIES=1, the laptop doesn't.
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = os.environ.get("SECURE_COOKIES", "0") == "1"

# Per-user daily photo-scan cap: friends' scans bill Aaron's API key.
SCAN_DAILY_LIMIT = int(os.environ.get("SCAN_DAILY_LIMIT", "15"))

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

init_db()

client = anthropic.Anthropic()


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
    return {"current_username": session.get("username")}


def _safe_next(target):
    """Only allow same-site relative redirect targets like '/recommend' --
    blocks open-redirect tricks like ?next=https://evil.com."""
    return target if target and target.startswith("/") and not target.startswith("//") else None


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if session.get("user_id"):
        return redirect(url_for("home"))
    if request.method == "POST":
        invite = request.form.get("invite", "").strip()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm", "")

        expected_invite = os.environ.get("INVITE_CODE", "")
        if not expected_invite:
            flash("Signups are disabled right now (no invite code configured).")
            return render_template("signup.html")
        if invite.lower() != expected_invite.lower():
            flash("That invite code isn't right. Ask Aaron for the code!")
            return render_template("signup.html", username=username)
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
        flash(f"Welcome to Bomu, {username}! Add some bottles to get started.")
        return redirect(url_for("home"))
    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("home"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
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


def instruction_steps(text):
    """Split instruction prose into a list of steps for numbered display.
    Prefers explicit line breaks; falls back to sentence boundaries. A recipe
    that's genuinely one sentence comes back as a single step and the
    template renders it as plain prose."""
    text = clean_instructions(text)
    if not text:
        return []
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if len(lines) > 1:
        return lines
    parts = re.split(r"(?<=[.!?])\s+", lines[0])
    return [p.strip() for p in parts if p.strip()]


app.jinja_env.filters["short_name"] = short_bottle_name
app.jinja_env.filters["clean_instructions"] = clean_instructions
app.jinja_env.filters["steps"] = instruction_steps
app.jinja_env.filters["clean_notes"] = clean_notes
app.jinja_env.filters["suggestions"] = get_suggestions
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
                    "text": """Look at this image of a bottle. Identify the bottle and return ONLY a JSON object with these fields:
- "name": the full product name (e.g. "Hendrick's Gin")
- "type": one of: gin, vodka, rum, tequila, mezcal, whiskey, bourbon, scotch, brandy, cognac, vermouth, amaro, liqueur, other
- "brand": the brand name (e.g. "Hendrick's")

If you cannot identify the bottle, return: {"name": "", "type": "", "brand": "", "error": "Could not identify this bottle"}

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
                    "text": """Look at this image showing multiple bottles. Identify as many bottles as you can and return ONLY a JSON array of objects, each with:
- "name": the full product name
- "type": one of: gin, vodka, rum, tequila, mezcal, whiskey, bourbon, scotch, brandy, cognac, vermouth, amaro, liqueur, other
- "brand": the brand name
- "confidence": "high" if you can clearly read the label, "low" if you're guessing

If you cannot identify any bottles, return: [{"name": "", "type": "", "brand": "", "confidence": "low", "error": "Could not identify bottles"}]

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


@app.route("/")
@login_required
def home():
    # Status line doubles as onboarding: "0 bottles" tells a new friend
    # exactly what their first step is.
    bottle_count = len(get_all_bottles(uid()))
    makeable_count = get_recommendations(uid(), max_makeable=0, max_one_away=0)["total_makeable"]
    return render_template(
        "home.html",
        bottle_count=bottle_count,
        makeable_count=makeable_count,
    )


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST":
        name = request.form["name"]
        bottle_type = request.form["type"]
        brand = request.form.get("brand", "")
        add_bottle(uid(), name, bottle_type, brand)
        flash(f"Added {name} to your bar!")
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
    """Enforce the per-user daily scan cap. Returns None if allowed, or a
    friendly message if the user is out of scans for today."""
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
            log_scan(uid())
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
            log_scan(uid())
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
            bottle_type = request.form.get(f"type_{i}", "other")
            brand = request.form.get(f"brand_{i}", "")
            add_bottle(uid(), name, bottle_type, brand)
            added += 1
        i += 1
    flash(f"Added {added} bottle{'s' if added != 1 else ''} to your bar!")
    return redirect(url_for("bar"))


def ingredient_slug(name):
    """'Angostura bitters' -> 'angostura_bitters'. Used to match photo files."""
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def get_ingredient_images():
    """Map ingredient slug -> static URL for any photo tile that exists on
    disk. Ingredients without a photo fall back to plain checkbox rows, so
    photos can be added incrementally without touching code."""
    img_dir = os.path.join(app.static_folder, "ingredients")
    images = {}
    if os.path.isdir(img_dir):
        for fname in os.listdir(img_dir):
            stem, ext = os.path.splitext(fname)
            if ext.lower() in (".jpg", ".jpeg", ".png", ".webp"):
                images[stem] = url_for("static", filename=f"ingredients/{fname}")
    return images


@app.route("/checklist", methods=["GET", "POST"])
@login_required
def checklist():
    if request.method == "POST":
        checked_ids = [int(x) for x in request.form.getlist("ingredient")]
        set_all_ingredients_stock(uid(), checked_ids)
        flash("Checklist saved!")
        return redirect(url_for("bar"))
    ingredients = get_all_ingredients(uid())
    new_ingredients = get_auto_added_ingredients(uid(), only_unstocked=True)
    return render_template(
        "checklist.html",
        ingredients=ingredients,
        new_ingredients=new_ingredients,
        ingredient_images=get_ingredient_images(),
        ingredient_slug=ingredient_slug,
    )


@app.route("/bar")
@login_required
def bar():
    bottles = get_all_bottles(uid())
    all_ingredients = get_all_ingredients(uid())
    stocked = [i for i in all_ingredients if i["in_stock"]]
    # Badge on the Mixers button if recipes have introduced new ingredients
    # the user hasn't reviewed yet. (Moved here from home when the manage
    # buttons moved to this page.)
    new_ingredient_count = len(get_auto_added_ingredients(uid(), only_unstocked=True))
    return render_template(
        "my_bar.html",
        bottles=bottles,
        stocked_ingredients=stocked,
        new_ingredient_count=new_ingredient_count,
    )


@app.route("/recommend")
@login_required
def recommend():
    grouped = request.args.get("group") == "spirit"
    if grouped:
        recs = get_recommendations_grouped(uid(), max_per_group=50)
    else:
        recs = get_recommendations(uid(), max_makeable=50, max_one_away=5)
    return render_template("recommend.html", recs=recs, grouped=grouped)


@app.route("/one-away")
@login_required
def one_away():
    groups = get_one_away_grouped(uid())
    return render_template("one_away.html", groups=groups)


@app.route("/favorites")
@login_required
def favorites():
    """Drinks you've thumbed up, most recent first."""
    favs = get_favorites(uid())
    return render_template("favorites.html", favorites=favs)


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
        # Fall back to thumbs-down too if nothing else is makeable
        pool = recs["makeable"]
    if not pool:
        flash("Nothing makeable yet. Add some bottles or check off mixers.")
        return redirect(url_for("recommend"))
    pick = random.choice(pool)
    return redirect(url_for("recipe", recipe_id=pick["recipe"]["id"]))


@app.route("/recipe/<int:recipe_id>")
@login_required
def recipe(recipe_id):
    r = get_recipe(recipe_id)
    if not r:
        flash("Recipe not found.")
        return redirect(url_for("home"))
    bottles = get_all_bottles(uid())
    ingredients_db = get_all_ingredients(uid())
    stocked = {i["name"].lower() for i in ingredients_db if i["in_stock"]}

    # For each ingredient, figure out which (if any) of the user's bottles satisfies it
    bottle_hints = {}
    for ing in r["ingredients"]:
        matches = matching_user_bottles(ing, bottles)
        if matches:
            bottle_hints[ing["id"]] = matches

    # For ingredient-type rows (bitters, mixers, etc.), surface a "you have
    # this in your stock" hint when the checklist item is in_stock.
    ingredient_have = {}
    for ing in r["ingredients"]:
        if ing["requirement_type"] == "ingredient" and ing["ingredient_name"]:
            if ing["ingredient_name"].lower() in stocked:
                ingredient_have[ing["id"]] = ing["ingredient_name"]

    # Which ingredients can't be fulfilled by the user's current bar?
    missing_ids = missing_ingredient_ids(r, bottles, stocked)

    return render_template(
        "recipe.html",
        recipe=r["recipe"],
        ingredients=r["ingredients"],
        bottle_hints=bottle_hints,
        ingredient_have=ingredient_have,
        missing_ids=missing_ids,
        rating=get_rating(uid(), recipe_id),
    )


@app.route("/rate/<int:recipe_id>", methods=["POST"])
@login_required
def rate(recipe_id):
    """Toggle thumb up or down for a recipe.
    Click the same thumb you already gave -> it clears (back to unrated)."""
    try:
        desired = int(request.form.get("thumb", 0))
    except ValueError:
        desired = 0
    if desired not in (1, -1):
        flash("Invalid rating.")
        return redirect(url_for("recipe", recipe_id=recipe_id))
    current = get_rating(uid(), recipe_id)
    if current == desired:
        set_rating(uid(), recipe_id, 0)  # toggle off
    else:
        set_rating(uid(), recipe_id, desired)
    return redirect(url_for("recipe", recipe_id=recipe_id))


@app.route("/edit/<int:bottle_id>", methods=["GET", "POST"])
@login_required
def edit(bottle_id):
    bottle = get_bottle(bottle_id, uid())
    if not bottle:
        flash("Bottle not found.")
        return redirect(url_for("bar"))
    if request.method == "POST":
        name = request.form["name"]
        bottle_type = request.form["type"]
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