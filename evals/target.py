import uuid


def extract_documents(state: dict) -> list[str]:
    """
    Flatten retrieved context from the graph state into a list of strings.
    Handles both consolidated (`context`) and per-domain (`soil_context`, etc.) fields.
    """
    docs: list[str] = []

    for key in (
        "context",
        "soil_context",
        "water_context",
        "crop_health_context",
        "yield_context",
    ):
        value = state.get(key, [])
        if not isinstance(value, list):
            continue

        for item in value:
            if hasattr(item, "page_content"):
                docs.append(item.page_content)
            elif isinstance(item, str):
                docs.append(item)

    # deduplicate, preserve order
    seen = set()
    unique = []
    for d in docs:
        if d not in seen:
            seen.add(d)
            unique.append(d)

    return unique


def make_target(agent):
    """
    Returns an async target function for LangSmith's evaluate().
    Each call uses a fresh thread_id so there is no memory bleed between eval examples.
    """

    async def target(inputs: dict) -> dict:
        try:
            config = {"configurable": {"thread_id": f"eval-{uuid.uuid4()}"}}
            result = await agent.ainvoke(
                {"messages": [{"role": "user", "content": inputs["question"]}]},
                config=config,
            )

            answer = result["messages"][-1].content
            documents = extract_documents(result)

            return {"answer": answer, "documents": documents}

        except Exception as e:
            return {"answer": f"ERROR: {e}", "documents": []}

    return target