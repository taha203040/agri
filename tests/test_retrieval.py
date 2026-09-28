from src.retrieval.retriever import soil_tool, disease_tool


def test_soil_retrieval():
    result = soil_tool.invoke(
        "What soil conditions are suitable for growing tomatoes?"
    )

    assert result
    assert isinstance(result, str)
    assert len(result.strip()) > 0


def test_disease_retrieval():
    result = disease_tool.invoke(
        "What are common diseases affecting tomato plants?"
    )

    assert result
    assert isinstance(result, str)
    assert len(result.strip()) > 0