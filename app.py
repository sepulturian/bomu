import os
import re
import base64
import json
import random
from io import BytesIO
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import anthropic
from PIL import Image
from database import (
    init_db, get_all_bottles, get_bottle, add_bottle, update_bottle,
    delete_bottle, get_all_ingredients, set_all_ingredients_stock,
    get_recipe, set_rating, get_rating, get_all_ratings, get_favorites,
    get_auto_added_ingredients, is_auto_added,
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

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

init_db()

client = anthropic.Anthropic()


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
    if brand and len(brand) <= 20:
        return brand
    if name and len(name) <= 20:
        return name
    if name:
        words = name.split()
        # Try first 2 words; if still too long, first word
        two = " ".join(words[:2])
        if len(two) <= 22:
            return two
        return words[0]
    return brand or "?"


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


app.jinja_env.filters["short_name"] = short_bottle_name
app.jinja_env.filters["clean_instructions"] = clean_instructions
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
def home():
    # Badge on the Mixers button if recipes have introduced new ingredients
    # the user hasn't reviewed yet.
    new_ingredient_count = len(get_auto_added_ingredients(only_unstocked=True))
    return render_template("home.html", new_ingredient_count=new_ingredient_count)


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        name = request.form["name"]
        bottle_type = request.form["type"]
        brand = request.form.get("brand", "")
        add_bottle(name, bottle_type, brand)
        flash(f"Added {name} to your bar!")
        return redirect(url_for("bar"))
    return render_template("add_bottle.html")


@app.route("/scan", methods=["GET", "POST"])
def scan():
    if request.method == "POST":
        if "photo" not in request.files:
            flash("No photo selected.")
            return redirect(url_for("scan"))
        photo = request.files["photo"]
        if photo.filename == "":
            flash("No photo selected.")
            return redirect(url_for("scan"))

        filename = secure_filename(photo.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        photo.save(filepath)

        try:
            result = scan_bottle_image(filepath)
        except Exception as e:
            flash(f"Error scanning photo: {str(e)}")
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
def scan_bulk():
    if request.method == "POST":
        if "photo" not in request.files:
            flash("No photo selected.")
            return redirect(url_for("scan_bulk"))
        photo = request.files["photo"]
        if photo.filename == "":
            flash("No photo selected.")
            return redirect(url_for("scan_bulk"))

        filename = secure_filename(photo.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        photo.save(filepath)

        try:
            results = scan_shelf_image(filepath)
        except Exception as e:
            flash(f"Error scanning photo: {str(e)}")
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
            add_bottle(name, bottle_type, brand)
            added += 1
        i += 1
    flash(f"Added {added} bottle{'s' if added != 1 else ''} to your bar!")
    return redirect(url_for("bar"))


@app.route("/checklist", methods=["GET", "POST"])
def checklist():
    if request.method == "POST":
        checked_ids = [int(x) for x in request.form.getlist("ingredient")]
        set_all_ingredients_stock(checked_ids)
        flash("Checklist saved!")
        return redirect(url_for("bar"))
    ingredients = get_all_ingredients()
    new_ingredients = get_auto_added_ingredients(only_unstocked=True)
    return render_template(
        "checklist.html",
        ingredients=ingredients,
        new_ingredients=new_ingredients,
    )


@app.route("/bar")
def bar():
    bottles = get_all_bottles()
    all_ingredients = get_all_ingredients()
    stocked = [i for i in all_ingredients if i["in_stock"]]
    return render_template("my_bar.html", bottles=bottles, stocked_ingredients=stocked)


@app.route("/recommend")
def recommend():
    grouped = request.args.get("group") == "spirit"
    if grouped:
        recs = get_recommendations_grouped(max_per_group=50)
    else:
        recs = get_recommendations(max_makeable=50, max_one_away=5)
    return render_template("recommend.html", recs=recs, grouped=grouped)


@app.route("/one-away")
def one_away():
    groups = get_one_away_grouped()
    return render_template("one_away.html", groups=groups)


@app.route("/favorites")
def favorites():
    """Drinks you've thumbed up, most recent first."""
    favs = get_favorites()
    return render_template("favorites.html", favorites=favs)


@app.route("/surprise")
def surprise():
    """Pick a random makeable drink and send the user straight to its recipe.
    Light bias toward unrated + thumbs-up drinks (skip thumbs-down) so the
    surprise doesn't keep landing on a drink Aaron already said he disliked."""
    recs = get_recommendations(max_makeable=200, max_one_away=0)
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
def recipe(recipe_id):
    r = get_recipe(recipe_id)
    if not r:
        flash("Recipe not found.")
        return redirect(url_for("home"))
    bottles = get_all_bottles()
    ingredients_db = get_all_ingredients()
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
        rating=get_rating(recipe_id),
    )


@app.route("/rate/<int:recipe_id>", methods=["POST"])
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
    current = get_rating(recipe_id)
    if current == desired:
        set_rating(recipe_id, 0)  # toggle off
    else:
        set_rating(recipe_id, desired)
    return redirect(url_for("recipe", recipe_id=recipe_id))


@app.route("/edit/<int:bottle_id>", methods=["GET", "POST"])
def edit(bottle_id):
    bottle = get_bottle(bottle_id)
    if not bottle:
        flash("Bottle not found.")
        return redirect(url_for("bar"))
    if request.method == "POST":
        name = request.form["name"]
        bottle_type = request.form["type"]
        brand = request.form.get("brand", "")
        update_bottle(bottle_id, name, bottle_type, brand)
        flash(f"Updated {name}!")
        return redirect(url_for("bar"))
    return render_template("edit_bottle.html", bottle=bottle)


@app.route("/delete/<int:bottle_id>", methods=["POST"])
def delete(bottle_id):
    bottle = get_bottle(bottle_id)
    if bottle:
        delete_bottle(bottle_id)
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