from flask import Flask, request, jsonify
from flask_cors import CORS
from sentence_transformers import SentenceTransformer, util
import pandas as pd
import joblib
import torch
import re
import difflib

# --------------------------
# INIT
# --------------------------
app = Flask(__name__)
CORS(app)

# --------------------------
# CHATBOT SETUP (Semantic Search)
# --------------------------
corpus = [
    "polymer is a large molecule, or macromolecule, made of many smaller, repeating molecular units called monomers",
    "Polylactic Acid (PLA) is a biopolymer used in packaging.",
    "Polyhydroxyalkanoates (PHA) are biodegradable polymers for packaging.",
    "Starch-based polymers are renewable and biodegradable.",
    "Cellulose derivatives like carboxymethyl cellulose and nanocellulose are used in packaging.",
    "Chitosan is a natural polymer with antimicrobial properties.",
    "Gelatin is protein-based and used in edible films.",
    "Alginate is derived from seaweed and used for coatings.",
    "Pectin is a plant-derived polymer used in packaging.",
    "Soy protein isolate and whey protein are used in bio-based films.",
    "Polycaprolactone (PCL) is a biodegradable polyester.",
    "Polybutylene succinate (PBS) is a compostable polymer.",
    "Polyethylene (PE) exists as LDPE and HDPE in conventional packaging.",
    "Polypropylene (PP) is widely used in food containers.",
    "Polyethylene terephthalate (PET) is used in bottles and films.",
    "Polystyrene (PS) is used in foams and rigid packaging.",
    "Polyvinyl chloride (PVC) is used in shrink wraps.",
    "Nylon (Polyamide, PA) provides strong barrier properties.",
    "EVOH (Ethylene vinyl alcohol copolymer) offers high gas barrier.",
    "Metallized films (Aluminum foil laminates) provide UV and gas barrier.",
    "Multilayer composites combine polymers for enhanced performance.",
    "Plasticizers like glycerol, sorbitol, and PEG improve flexibility.",
    "Nanoparticles and fillers are added to improve barrier and strength.",
    "Nanoclay enhances mechanical properties.",
    "TiO2 nanoparticles provide UV protection.",
    "ZnO nanoparticles have antimicrobial effects.",
    "Carbon quantum dots (CQDs) add active properties.",
    "Graphene oxide improves strength and barrier.",
    "Neem oil and lemon oil are natural extracts with antimicrobial effects.",
    "Essential oils like thyme, oregano, cinnamon, clove act as antimicrobials.",
    "Plant polyphenols like tannins and catechins act as antioxidants.",
    "Vitamin E (tocopherol) and Vitamin C (ascorbic acid) are antioxidants.",
    "Cross-linking agents include citric acid, glutaraldehyde, genipin.",
    "Natural dyes, anthocyanins, carotenoids act as colorants and UV blockers.",
    "Biodegradability is the ability of material to decompose by microorganisms.",
    "Compostability means breaking down into CO2, water, and biomass.",
    "Barrier properties include resistance to O2, CO2, moisture, and UV light.",
    "Mechanical properties include tensile strength and elongation.",
    "Thermal stability refers to melting point and glass transition temperature.",
    "Migration is the movement of additives into food.",
    "Antimicrobial activity is inhibition of bacteria and fungi.",
    "Active packaging releases or absorbs substances to extend shelf life.",
    "Intelligent packaging monitors food quality with sensors.",
    "Sustainability includes recyclability and renewable resources."
]

# ---------- configuration ----------
DEBUG = False                 # set True temporarily to print scores to console
TOP_K = 3                     # how many semantic candidates to fetch
CONF_THRESH = 0.50            # confidence threshold for a direct answer
LOWER_CONF_THRESH = 0.35      # if between LOWER and CONF, show suggestions
FUZZY_CUTOFF = 0.60           # difflib ratio cutoff for fuzzy match fallback
# -----------------------------------

# Load the sentence transformer (ensure model is available locally or internet)
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# Precompute embeddings
corpus_embeddings = embedder.encode(corpus, convert_to_tensor=True)

# normalized corpus for fuzzy matching and alias detection
def normalize_text(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9\s]", " ", s)      # remove punctuation
    s = re.sub(r"\s+", " ", s).strip()
    return s

corpus_norm = [normalize_text(c) for c in corpus]

# alias map: quick direct mapping for common acronyms/keywords
# we populate alias_map by checking for presence in the normalized corpus
common_aliases = {
    "pla": "pla",
    "polylactic": "polylactic",
    "pha": "pha",
    "polymer": "polymer",
    "pla": "pla",
    "pha": "pha",
    "pe": "polyethylene",
    "polyhydroxyalkanoates": "polyhydroxyalkanoates",
    "pe": "polyethylene",
    "polyethylene": "polyethylene",
    "pp": "polypropylene",
    "polypropylene": "polypropylene",
    "pet": "polyethylene terephthalate",
    "pcl": "polycaprolactone",
    "pbs": "polybutylene succinate",
    "ps": "polystyrene",
    "pvc": "polyvinyl chloride",
    "chitosan": "chitosan",
    "gelatin": "gelatin",
    "alginate": "alginate",
    "evoh": "evoh",
    "nanoclay": "nanoclay",
    "tio2": "tio2",
    "zno": "zno",
}

alias_to_idx = {}
for alias, key in common_aliases.items():
    for i, c in enumerate(corpus_norm):
        if key in c:
            alias_to_idx[alias] = i
            break

def get_answer(user_input: str):
    if not user_input or user_input.strip() == "":
        return {"reply": "Please send a question."}

    user_norm = normalize_text(user_input)

    # Quick alias/keyword shortcut: if user mentions 'pla' or 'pet' etc.
    for token in user_norm.split():
        if token in alias_to_idx:
            idx = alias_to_idx[token]
            if DEBUG:
                print(f"ALIAS MATCH: token={token} -> idx={idx}")
            return {"reply": corpus[idx], "method": "alias", "score": 1.0}

    # Semantic search
    user_embedding = embedder.encode(user_input, convert_to_tensor=True)
    hits = util.semantic_search(user_embedding, corpus_embeddings, top_k=TOP_K)[0]
    # hits is a list of dicts: {'corpus_id': int, 'score': float}, sorted by score desc

    if DEBUG:
        print("Semantic hits:", hits)

    best_hit = hits[0]
    best_idx = int(best_hit["corpus_id"])
    best_score = float(best_hit["score"])

    # If confident return direct answer
    if best_score >= CONF_THRESH:
        return {"reply": corpus[best_idx], "method": "semantic", "score": round(best_score, 4)}

    # If moderately confident, return suggestions (top_k)
    if best_score >= LOWER_CONF_THRESH:
        candidates = []
        for h in hits:
            candidates.append({
                "text": corpus[int(h["corpus_id"])],
                "score": round(float(h["score"]), 4)
            })
        return {
            "reply": "I found a few possibilities — please choose/rephrase if needed.",
            "method": "suggestions",
            "candidates": candidates
        }

    # Fuzzy fallback (difflib) - works well when user misspells or uses similar short phrases
    best_ratio = 0.0
    best_idx_fuzzy = None
    for i, c in enumerate(corpus_norm):
        ratio = difflib.SequenceMatcher(None, user_norm, c).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_idx_fuzzy = i

    if DEBUG:
        print(f"Fuzzy best_ratio={best_ratio}, idx={best_idx_fuzzy}")

    if best_ratio >= FUZZY_CUTOFF and best_idx_fuzzy is not None:
        return {"reply": corpus[best_idx_fuzzy], "method": "fuzzy", "score": round(best_ratio, 4)}

    # Nothing confident: return polite fallback + top candidates to help user
    candidates = []
    for h in hits:
        candidates.append({
            "text": corpus[int(h["corpus_id"])],
            "score": round(float(h["score"]), 4)
        })
    # include fuzzy top too
    if best_idx_fuzzy is not None:
        candidates.append({
            "text": corpus[best_idx_fuzzy],
            "score": round(best_ratio, 4),
            "method": "fuzzy"
        })

    return {
        "reply": "Sorry, I don’t know the answer. Try rephrasing or pick from the suggestions.",
        "method": "none_confident",
        "candidates": candidates
    }


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")
    result = get_answer(user_message)

    # Keep compatibility with existing front-end which expects a 'reply' string
    # and also expose candidates/scores when available.
    response = {"reply": result.get("reply", "")}
    # add optional debugging info for front-end or logging
    if "candidates" in result:
        response["candidates"] = result["candidates"]
    if "score" in result:
        response["score"] = result["score"]
    if "method" in result:
        response["method"] = result["method"]

    return jsonify(response)

# --------------------------
# PREDICTION SETUP (unchanged)
# --------------------------
loaded_model = joblib.load("supply_packaging_model.pkl")

def make_features_from_data(data):
    date = pd.to_datetime(data.get("date"), errors="coerce")
    if pd.isna(date):
        raise ValueError("Invalid date format. Use YYYY-MM-DD.")

    feats = {
        "temperature": data.get("temperature"),
        "humidity": data.get("humidity"),
        "transportation_time": data.get("transportation_time"),
        "month": date.month,
        "dayofweek": date.dayofweek,
        "dayofyear": date.dayofyear,
        "is_month_start": int(date.is_month_start),
        "is_month_end": int(date.is_month_end)
    }
    return pd.DataFrame([feats])

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()
        features = make_features_from_data(data)

        prediction = loaded_model.predict(features)[0]
        if prediction == "Metal":
            prediction = "Plastic"
        classes = list(loaded_model.named_steps['clf'].classes_)

        if "Plastic" in classes:
            prob_plastic = loaded_model.predict_proba(features)[:, classes.index("Plastic")][0]
        else:
            prob_plastic = None

        return jsonify({
            "prediction": prediction,
            "probability_plastic": round(float(prob_plastic), 4) if prob_plastic is not None else "N/A",
            "features": features.to_dict(orient="records")[0]
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400

# --------------------------
# RUN SERVER
# --------------------------
if __name__ == "__main__":
    app.run(debug=True)
