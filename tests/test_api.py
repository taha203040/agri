import pytest

from src.agents.service import stream_response


@pytest.mark.asyncio
async def test_stream_response():
    chunks = []

    async for chunk in stream_response(
        "What is crop rotation?"
    ):
        chunks.append(chunk)

    assert chunks
    assert all(isinstance(chunk, str) for chunk in chunks)

    response = "".join(chunks)

    assert response.strip()