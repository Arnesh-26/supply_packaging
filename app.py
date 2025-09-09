from flask import Flask, request, jsonify
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# Knowledge base text corpus
corpus = [
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
    "TiO₂ nanoparticles provide UV protection.",
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
    "Compostability means breaking down into CO₂, water, and biomass.",
    "Barrier properties include resistance to O₂, CO₂, moisture, and UV light.",
    "Mechanical properties include tensile strength and elongation.",
    "Thermal stability refers to melting point and glass transition temperature.",
    "Migration is the movement of additives into food.",
    "Antimicrobial activity is inhibition of bacteria and fungi.",
    "Active packaging releases or absorbs substances to extend shelf life.",
    "Intelligent packaging monitors food quality with sensors.",
    "Sustainability includes recyclability and renewable resources."
]

# Vectorizer for semantic similarity
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(corpus)

def get_answer(user_input):
    user_vec = vectorizer.transform([user_input])
    similarity = cosine_similarity(user_vec, X).flatten()
    best_idx = similarity.argmax()
    best_score = similarity[best_idx]

    if best_score < 0.2:
        return "Sorry, I don’t know the answer. Try rephrasing your question."
    return corpus[best_idx]

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")
    answer = get_answer(user_message)
    return jsonify({"reply": answer})

if __name__ == "__main__":
    app.run(debug=True)