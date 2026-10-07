from langsmith import Client

from evals.config import DATASET_NAME


QUESTIONS = [
    # ── WATER ─────────────────────────────────────────────────────────────
    {
        "question": "How much water does maize need per growing season?",
        "answer": "Maize typically requires 500–800 mm of water per growing season, depending on climate, soil type, and variety. Peak demand occurs during tasseling and grain filling.",
    },
    {
        "question": "What is the water requirement for tomatoes during flowering?",
        "answer": "Tomatoes need 25–35 mm of water per week during flowering, applied consistently. Irregular watering at this stage causes blossom-end rot.",
    },
    {
        "question": "How can I reduce irrigation while keeping corn yield stable?",
        "answer": "Use deficit irrigation timed to avoid stress during tasseling and grain fill, mulching to reduce evaporation, and drought-tolerant hybrids. Soil moisture sensors help optimize scheduling.",
    },
    {
        "question": "What is the water consumption of wheat compared to barley?",
        "answer": "Wheat typically consumes 450–650 mm per season, while barley uses 350–500 mm. Barley is generally more drought-tolerant and suited to drier regions.",
    },
    {
        "question": "How often should I irrigate vegetable crops in sandy soil?",
        "answer": "Sandy soils drain quickly and require more frequent, lighter irrigations — often every 2–3 days. Drip irrigation with daily small doses works best.",
    },

    # ── SOIL ──────────────────────────────────────────────────────────────
    {
        "question": "Which nutrients are deficient in sandy soil?",
        "answer": "Sandy soils are commonly deficient in nitrogen, potassium, and organic matter. They leach nutrients quickly and have low cation exchange capacity.",
    },
    {
        "question": "How does soil pH affect nutrient uptake in barley?",
        "answer": "Barley prefers pH 6.0–7.5. Outside this range, phosphorus and micronutrients like zinc and manganese become less available, reducing uptake and yield.",
    },
    {
        "question": "What is the ideal soil type for growing tomatoes?",
        "answer": "Tomatoes grow best in well-drained loamy soil with pH 6.0–6.8, rich in organic matter and with good water-holding capacity.",
    },
    {
        "question": "How can I improve clay soil for vegetable production?",
        "answer": "Add organic matter (compost, manure), use raised beds, avoid working wet soil, and consider gypsum for sodic clays. Cover crops help break compaction.",
    },
    {
        "question": "What are the signs of nitrogen deficiency in crops?",
        "answer": "Nitrogen deficiency shows as pale green to yellow older leaves, stunted growth, and reduced tillering. It moves upward, so older leaves show symptoms first.",
    },

    # ── DISEASES ──────────────────────────────────────────────────────────
    {
        "question": "What are the symptoms of early blight in tomato?",
        "answer": "Early blight causes dark brown spots with concentric rings on lower leaves, yellowing around lesions, and progressive defoliation. It is caused by Alternaria solani.",
    },
    {
        "question": "What treatments exist for powdery mildew on cucurbits?",
        "answer": "Powdery mildew on cucurbits is treated with sulfur-based fungicides, potassium bicarbonate, neem oil, or resistant varieties. Good airflow and avoiding overhead irrigation help prevent it.",
    },
    {
        "question": "What causes yellow leaves in pepper plants?",
        "answer": "Yellow leaves in peppers can be caused by nitrogen deficiency, overwatering, magnesium deficiency, or viral infections like mosaic virus. Diagnosis requires checking leaf pattern and soil conditions.",
    },
    {
        "question": "How do I prevent late blight in potatoes?",
        "answer": "Use certified seed, resistant varieties, proper spacing for airflow, avoid overhead irrigation, and apply preventive copper or chlorothalonil fungicides during cool, wet weather.",
    },
    {
        "question": "What are the common fungal diseases of wheat?",
        "answer": "Common wheat fungal diseases include rust (yellow, leaf, stem), powdery mildew, Septoria leaf blotch, and Fusarium head blight. Rotating crops and using resistant varieties reduces risk.",
    },
    {
        "question": "How can I control aphids on vegetable crops?",
        "answer": "Aphids are controlled with neem oil, insecticidal soap, ladybugs, and reflective mulches. Avoid excess nitrogen, which attracts them. Row covers help early in the season.",
    },

    # ── YIELD ─────────────────────────────────────────────────────────────
    {
        "question": "What is the expected yield of wheat under normal rainfall?",
        "answer": "Rainfed wheat yields typically range from 2 to 4 tonnes per hectare under normal rainfall, depending on variety, soil fertility, and management practices.",
    },
    {
        "question": "Which crops yield best in semi-arid climates?",
        "answer": "Sorghum, millet, drought-tolerant wheat varieties, chickpeas, and certain barley cultivars perform well in semi-arid climates due to their low water requirements.",
    },
    {
        "question": "What factors most affect maize yield?",
        "answer": "Maize yield is driven by water availability (especially at tasseling and grain fill), nitrogen supply, plant density, hybrid choice, and pest/disease pressure.",
    },
    {
        "question": "How can I increase tomato yield per plant?",
        "answer": "Use stakes or cages, prune suckers, ensure consistent watering, apply balanced fertilizer with calcium, and control pests early. Mulching stabilizes soil moisture.",
    },
    {
        "question": "What is the average yield of wheat under full irrigation?",
        "answer": "Fully irrigated wheat typically yields 5–8 tonnes per hectare in temperate regions, and 4–6 tonnes per hectare in Mediterranean climates, depending on variety and management.",
    },
]

def get_or_create_dataset(client: Client):
    """Create the dataset if it doesn't exist; return it either way."""
    try:
        return client.read_dataset(dataset_name=DATASET_NAME)
    except Exception:
        pass

    dataset = client.create_dataset(
        dataset_name=DATASET_NAME,
        description="Agriculture RAG evaluation set covering water, soil, disease, and yield.",
    )

    client.create_examples(
        inputs=[{"question": q["question"]} for q in QUESTIONS],
        outputs=[{"answer": q["answer"]} for q in QUESTIONS],
        dataset_id=dataset.id,
    )

    print(f"✅ Created dataset '{DATASET_NAME}' with {len(QUESTIONS)} examples")
    return dataset