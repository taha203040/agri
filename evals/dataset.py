from langsmith import Client

from evals.config import DATASET_NAME

QUESTIONS = [
    # ── WATER ──────────────────────────────────────────────
    {
        "question": "How much water does maize need per growing season?",
        "answer": (
            "Maize typically requires 500-800 mm of water per growing "
            "season. Peak demand occurs during tasseling and grain filling."
        ),
        "topic": "water",
    },
    {
        "question": "How much water do maize and tomato need per day and per growing season?",
        "answer": (
            "Maize requires approximately 500-800 mm per growing season, "
            "with peak demand during tasseling and grain filling. Tomato "
            "typically uses 2.5-7.5 mm per day and requires approximately "
            "400-800 mm per growing season. Actual requirements depend "
            "on climate, soil, variety, and growth stage."
        ),
        "topic": "water",
    },
    {
        "question": "How much water does potato need per day and per growing season?",
        "answer": (
            "Potato typically uses 2-6 mm of water per day and requires "
            "approximately 500-700 mm per growing season."
        ),
        "topic": "water",
    },
    {
        "question": "How much water does onion need per day and per growing season?",
        "answer": (
            "Onion typically uses 1-5 mm of water per day and requires "
            "approximately 350-550 mm per growing season."
        ),
        "topic": "water",
    },
    {
        "question": "How much water does cabbage need per day and per growing season?",
        "answer": (
            "Cabbage typically uses 2-5.5 mm of water per day and requires "
            "approximately 350-500 mm per growing season."
        ),
        "topic": "water",
    },
    {
        "question": "How much water does cucumber need per day and per growing season?",
        "answer": (
            "Cucumber typically uses 2-6 mm of water per day. Its "
            "approximate seasonal requirement is 400-700 mm."
        ),
        "topic": "water",
    },
    {
        "question": "How much water does watermelon need per day and per growing season?",
        "answer": (
            "Watermelon typically uses 2-6 mm of water per day. Its "
            "approximate seasonal requirement is 400-600 mm."
        ),
        "topic": "water",
    },
    {
        "question": "How much water does lettuce need per day and per growing season?",
        "answer": (
            "Lettuce typically uses 1.5-5 mm of water per day. Its "
            "approximate seasonal requirement is 250-500 mm."
        ),
        "topic": "water",
    },
    {
        "question": "How much water does citrus need per day and per season?",
        "answer": (
            "Citrus typically uses 2-6 mm of water per day. Its "
            "approximate seasonal requirement is 900-1200 mm, depending "
            "on climate, tree size, and orchard management."
        ),
        "topic": "water",
    },
    {
        "question": "How much water does banana need per day and per growing season?",
        "answer": (
            "Banana typically uses 3-8 mm of water per day and requires "
            "approximately 1200-2200 mm per growing season."
        ),
        "topic": "water",
    },
    {
        "question": "How much water does olive need per day and per season?",
        "answer": (
            "Olive typically uses approximately 1.5-5 mm of water per "
            "day. Seasonal requirements vary with rainfall, climate, "
            "and orchard management."
        ),
        "topic": "water",
    },
    {
        "question": "How do I convert millimeters of water into cubic meters per hectare?",
        "answer": (
            "One millimeter of water over one hectare equals 10 cubic "
            "meters. Multiply the water depth in millimeters by 10 to "
            "calculate cubic meters per hectare. For example, 500 mm "
            "equals 5000 cubic meters per hectare."
        ),
        "topic": "water",
    },
    {
        "question": "Is crop water use the same as irrigation water applied?",
        "answer": (
            "No. Crop water use mainly represents evapotranspiration. "
            "Irrigation applied must also account for effective rainfall, "
            "soil-water storage, and irrigation-system efficiency."
        ),
        "topic": "water",
    },

    # ── SOIL ───────────────────────────────────────────────
    {
        "question": "What are the signs of nitrogen deficiency in crops?",
        "answer": (
            "Nitrogen deficiency commonly causes pale green or yellow "
            "older leaves, stunted growth, reduced leaf area, and "
            "reduced tillering in cereals. Symptoms often begin on "
            "older leaves because nitrogen is mobile within the plant."
        ),
        "topic": "soil",
    },
    {
        "question": "Which leaves turn yellow first when a crop lacks nitrogen?",
        "answer": (
            "Nitrogen deficiency usually causes yellowing first in older, "
            "lower leaves because nitrogen can move from older tissues "
            "to younger growing tissues."
        ),
        "topic": "soil",
    },
    {
        "question": "What are the symptoms of phosphorus deficiency in plants?",
        "answer": (
            "Phosphorus deficiency can cause stunted growth, poor root "
            "development, delayed maturity, and dark green or purplish "
            "leaves in some crops. Symptoms vary with crop species and "
            "growing conditions."
        ),
        "topic": "soil",
    },
    {
        "question": "What are the symptoms of potassium deficiency in plants?",
        "answer": (
            "Potassium deficiency commonly causes yellowing followed "
            "by browning or scorching along leaf margins, often on "
            "older leaves. Severe deficiency can reduce growth and "
            "crop quality."
        ),
        "topic": "soil",
    },
    {
        "question": "What are the symptoms of iron deficiency in crops?",
        "answer": (
            "Iron deficiency commonly causes interveinal chlorosis "
            "in young leaves. The tissue between the veins turns yellow "
            "while the veins may remain green. It is common in susceptible "
            "crops growing in high-pH or calcareous soils."
        ),
        "topic": "soil",
    },
    {
        "question": "What are the symptoms of magnesium deficiency in crops?",
        "answer": (
            "Magnesium deficiency commonly causes interveinal chlorosis "
            "in older leaves, with yellow tissue between green veins. "
            "Severe deficiency may cause leaf necrosis and premature "
            "leaf drop."
        ),
        "topic": "soil",
    },
    {
        "question": "How does soil type affect water and nutrient retention?",
        "answer": (
            "Sandy soils drain quickly and generally retain less water "
            "and nutrients. Clay soils often retain more water and "
            "nutrients but may have drainage and compaction problems. "
            "Loam soils often provide a balance of drainage, aeration, "
            "and nutrient retention."
        ),
        "topic": "soil",
    },
    {
        "question": "How does soil pH affect nutrient availability?",
        "answer": (
            "Soil pH affects nutrient solubility and availability. "
            "Acidic soils can restrict phosphorus availability and "
            "increase the risk of aluminum toxicity. Alkaline and "
            "calcareous soils can reduce iron, zinc, and phosphorus "
            "availability."
        ),
        "topic": "soil",
    },
    {
        "question": "How can nitrogen deficiency be distinguished from iron deficiency?",
        "answer": (
            "Nitrogen deficiency commonly causes yellowing that begins "
            "in older leaves. Iron deficiency typically causes "
            "interveinal chlorosis in young leaves, with veins remaining "
            "green. Soil or plant-tissue testing can help confirm "
            "the diagnosis."
        ),
        "topic": "soil",
    },

    # ── DISEASES ───────────────────────────────────────────
    {
        "question": "What are the symptoms of early blight in tomato?",
        "answer": (
            "Early blight causes dark brown leaf spots with concentric "
            "rings, often on lower leaves, yellowing around lesions, "
            "and progressive defoliation. It is commonly associated "
            "with Alternaria solani."
        ),
        "topic": "diseases",
    },

    # ── YIELD ──────────────────────────────────────────────
    {
        "question": "What factors most affect maize yield?",
        "answer": (
            "Maize yield depends on water availability, especially "
            "during tasseling and grain filling, nitrogen supply, "
            "plant density, hybrid selection, soil fertility, and "
            "pest and disease pressure."
        ),
        "topic": "yield",
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