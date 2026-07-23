"""Brand suggestions for missing cocktail ingredients.
Used on the /one-away page to give the user concrete shopping options
when an ingredient is missing.

Keys are matched case-insensitively on word boundaries against the missing
ingredient's name, longest key first. So 'Maraschino Liqueur' matches the
'maraschino' key, but 'gin' does not match 'ginger beer'.
"""

import re

# Most specific keys first (longer phrases). Lookup walks the dict in order
# and returns the first match.
SUGGESTIONS = {
    # --- Liqueurs ---
    "maraschino": ["Luxardo Maraschino", "Maraska Maraschino"],
    "cherry heering": ["Cherry Heering", "Luxardo Sangue Morlacco"],
    "coffee liqueur": ["Kahlúa", "Tia Maria", "Mr. Black"],
    "irish cream": ["Baileys", "Carolans"],
    "triple sec": ["Cointreau", "Combier", "Grand Marnier"],
    "cointreau": ["Cointreau (or any premium triple sec)"],
    "grand marnier": ["Grand Marnier"],
    "campari": ["Campari"],
    "aperol": ["Aperol"],
    "amaro nonino": ["Amaro Nonino", "Amaro Lucano (substitute)"],
    "amaro": ["Amaro Nonino", "Averna", "Montenegro"],
    "creme de cacao": ["Tempus Fugit", "Marie Brizard"],
    "crème de cacao": ["Tempus Fugit", "Marie Brizard"],
    "creme de menthe": ["Tempus Fugit", "Branca Menta"],
    "crème de menthe": ["Tempus Fugit", "Branca Menta"],
    "chartreuse": ["Green Chartreuse (Last Word, etc.)"],
    "benedictine": ["Bénédictine D.O.M."],
    "bénédictine": ["Bénédictine D.O.M."],
    "drambuie": ["Drambuie"],
    "kahlua": ["Kahlúa", "Tia Maria"],
    "kahlúa": ["Kahlúa", "Tia Maria"],
    "baileys": ["Baileys", "Carolans"],
    "galliano": ["Galliano"],
    "midori": ["Midori"],
    "frangelico": ["Frangelico"],

    # --- Aromatised wines / aperitifs ---
    "sweet vermouth": ["Carpano Antica", "Cinzano Rosso", "Martini & Rossi Rosso"],
    "dry vermouth": ["Dolin Dry", "Noilly Prat", "Martini Extra Dry"],
    "vermouth": ["Sweet: Carpano Antica", "Dry: Dolin Dry"],
    "lillet blanc": ["Lillet Blanc", "Cocchi Americano (substitute)"],
    "lillet": ["Lillet Blanc"],

    # --- Anise / specialty ---
    "absinthe": ["Pernod Absinthe", "St. George Absinthe", "Vieux Pontarlier"],
    "pernod": ["Pernod", "Ricard pastis"],

    # --- Specialty spirits ---
    "cachaca": ["Leblon", "Avuá", "Novo Fogo"],
    "cachaça": ["Leblon", "Avuá", "Novo Fogo"],
    "pisco": ["Pisco Capel", "Macchu Pisco", "Barsol"],
    "calvados": ["Calvados Boulard"],
    "armagnac": ["Tariquet", "Delord"],

    # --- Spirits (when type is missing) ---
    "bourbon": ["Buffalo Trace", "Maker's Mark", "Bulleit Bourbon"],
    "rye": ["Rittenhouse Rye", "Sazerac Rye", "Bulleit Rye"],
    "scotch": ["Famous Grouse (blended)", "Monkey Shoulder (blended)", "Talisker (single malt)"],
    "blended scotch": ["Famous Grouse", "Monkey Shoulder", "Chivas"],
    "mezcal": ["Del Maguey Vida", "Mezcal Union", "Bozal"],
    "tequila": ["Espolòn Blanco", "El Tesoro", "Casamigos"],
    "gin": ["Bombay Sapphire", "Tanqueray", "Hendrick's"],
    "vodka": ["Tito's", "Ketel One", "Grey Goose"],
    "rum": ["Bacardi (light)", "Mount Gay (gold)", "Diplomático (dark)"],
    "cognac": ["Hennessy V.S.", "Pierre Ferrand 1840"],
    "brandy": ["E&J", "Pierre Ferrand 1840"],
    "whiskey": ["Buffalo Trace (bourbon)", "Jameson (Irish)", "Famous Grouse (scotch)"],

    # --- Wines / bubbles ---
    "champagne": ["any dry brut", "Cava (cheaper)", "Prosecco (cheaper)"],
    "prosecco": ["any Prosecco DOC"],
    "sparkling wine": ["Cava", "Prosecco", "Crémant"],

    # --- Mixers ---
    "tomato juice": ["any unsalted tomato juice", "Clamato (for Bloody Maria)"],
    "ginger beer": ["Fever-Tree", "Bundaberg", "Old Jamaica"],
    "ginger ale": ["Canada Dry", "Fever-Tree"],
    "tonic water": ["Fever-Tree", "Schweppes", "Q Tonic"],
    "soda water": ["any plain soda water"],
    "club soda": ["any club soda"],
    "cranberry juice": ["Ocean Spray", "any 100% cranberry"],
    "pineapple juice": ["Dole", "fresh-squeezed if you can"],
    "grapefruit juice": ["fresh ruby red", "Ocean Spray"],
    "orange juice": ["fresh-squeezed", "Tropicana"],
    "coconut cream": ["Coco López", "Coco Real"],

    # --- Pantry / DIY ---
    "honey syrup": ["DIY: 1:1 honey + warm water, stir to dissolve"],
    "ginger syrup": ["DIY: simmer 1 cup sliced ginger + 1 cup sugar + 1 cup water, strain"],
    "simple syrup": ["DIY: 1:1 sugar + water, dissolved"],
    "honey": ["any liquid honey"],
    "egg whites": ["fresh egg whites", "pasteurized whites in a carton (safer)"],

    # --- Bitters ---
    "angostura": ["Angostura Aromatic Bitters"],
    "orange bitters": ["Regan's #6", "Angostura Orange"],
    "peychaud": ["Peychaud's Bitters"],
}


def get_suggestions(missing_name):
    """Case-insensitive lookup. Returns list of suggestions or empty list.

    Longest keys are tried first and keys only match on whole words, so
    'ginger beer' wins over 'ginger' and 'gin' never matches inside
    'ginger'. (That substring bug used to recommend gin brands when you
    were missing ginger beer.)"""
    if not missing_name:
        return []
    lower = missing_name.lower()
    for key, suggestions in sorted(SUGGESTIONS.items(), key=lambda kv: -len(kv[0])):
        if re.search(r"\b" + re.escape(key) + r"\b", lower):
            return suggestions
    return []
