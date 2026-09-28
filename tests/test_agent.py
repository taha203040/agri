from src.config.config import agent


def test_agent_responds():
    response = agent.invoke(
        {
            "messages": [
                ("user", "What is crop rotation?")
            ]
        }
    )

    assert response
    assert "messages" in response
    assert len(response["messages"]) > 0


def test_agent_produces_final_answer():
    response = agent.invoke(
        {
            "messages": [
                ("user", "What is crop rotation?")
            ]
        }
    )

    messages = response["messages"]

    final_message = messages[-1]

    assert final_message.content
    assert isinstance(final_message.content, str)