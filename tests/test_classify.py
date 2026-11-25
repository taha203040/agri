from types import SimpleNamespace

from src.agents.agriculture_graph import classify_intent


def _intent(q: str) -> str:
    return classify_intent({"messages": [SimpleNamespace(content=q)]})["intent"]


def test_carrot_water_question_is_water_only():
    assert _intent("Carrot ETc with ETo 6 mm/day and Kc 1.05") == "water"


def test_grain_is_not_rain():
    assert _intent("grain yield") == "yield"


def test_rotation_is_not_rot():
    assert _intent("rotation and soil pH") == "soil"


def test_real_disease_still_routes():
    assert "crop_health" in _intent("tomato early blight symptoms")
