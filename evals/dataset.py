from langsmith import Client

from evals.config import DATASET_NAME


QUESTIONS = [
    # ── WATER ──────────────────────────────────────────────
    {
        "question": "How much water does maize need per growing season?",
        "answer": (
            "Maize typically requires 500–800 mm of water per growing "
            "season, depending on climate, soil type, and variety. "
            "Peak demand occurs during tasseling and grain filling."
        ),
        "topic": "water",
    },

    # ── SOIL ───────────────────────────────────────────────
    {
        "question": "What are the signs of nitrogen deficiency in crops?",
        "answer": (
            "Nitrogen deficiency commonly causes pale green or yellow "
            "older leaves, stunted growth, and reduced tillering. "
            "Symptoms often appear first on older leaves."
        ),
        "topic": "soil",
    },

    # ── DISEASES ───────────────────────────────────────────
    {
        "question": "What are the symptoms of early blight in tomato?",
        "answer": (
            "Early blight causes dark brown leaf spots with concentric "
            "rings, often on lower leaves, yellowing around lesions, "
            "and progressive defoliation. It is caused by Alternaria solani."
        ),
        "topic": "diseases",
    },

    # ── YIELD ──────────────────────────────────────────────
    {
        "question": "What factors most affect maize yield?",
        "answer": (
            "Maize yield depends on water availability, especially during "
            "tasseling and grain filling, nitrogen supply, plant density, "
            "hybrid selection, and pest and disease pressure."
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