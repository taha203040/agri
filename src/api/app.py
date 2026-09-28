import json
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.agents.service import invoke_response, stream_response


# ──────────────────────────────────────────────────────────────────────────────
# Logging
# ──────────────────────────────────────────────────────────────────────────────

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# Application
# ──────────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Agriculture RAG API",
    description="Agricultural question answering using RAG, Chroma, and LangGraph.",
    version="2.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ──────────────────────────────────────────────────────────────────────────────
# Schemas
# ──────────────────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    question: str
    thread_id: str = "default"


# ──────────────────────────────────────────────────────────────────────────────
# Health check
# ──────────────────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {
        "status": "healthy",
        "service": "Agriculture RAG API",
        "version": "2.0.0",
    }


# ──────────────────────────────────────────────────────────────────────────────
# Non-streaming chat
# ──────────────────────────────────────────────────────────────────────────────

@app.post("/chat")
async def chat(request: ChatRequest):
    """
    Process an agricultural question and return the complete response.
    Conversation memory is maintained using thread_id.
    """

    try:
        response = await invoke_response(
            request.question,
            request.thread_id,
        )

        return {
            "status": "success",
            "response": response,
        }

    except Exception as e:
        logger.error(
            "Chat request failed: %s",
            e,
            exc_info=True,
        )

        return {
            "status": "error",
            "detail": str(e),
        }


# ──────────────────────────────────────────────────────────────────────────────
# Streaming chat
# ──────────────────────────────────────────────────────────────────────────────

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Stream the agent response using Server-Sent Events (SSE).
    """

    async def generate():
        try:
            yield (
                f"data: {json.dumps({
                    'type': 'status',
                    'content': 'Thinking...'
                })}\n\n"
            )

            async for text in stream_response(
                request.question,
                request.thread_id,
            ):
                yield (
                    f"data: {json.dumps({
                        'type': 'token',
                        'content': text
                    })}\n\n"
                )

            yield (
                f"data: {json.dumps({
                    'type': 'done'
                })}\n\n"
            )

        except Exception as e:
            logger.error(
                "Streaming request failed: %s",
                e,
                exc_info=True,
            )

            yield (
                f"data: {json.dumps({
                    'type': 'error',
                    'error': str(e)
                })}\n\n"
            )

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

