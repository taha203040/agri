import asyncio
import json
import logging
from contextlib import asynccontextmanager
from uuid import UUID

from src.monitoring.tracing import setup_tracing

setup_tracing()  # must run before the LangChain / LangGraph imports below

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langchain_deepseek import ChatDeepSeek
from pydantic import BaseModel

from src.agents.agriculture_agent import create_agriculture_agent
from src.agents.service import invoke_response, stream_response
from src.api.ingest import router as ingest_router
from src.config.settings import settings
from src.memory.conversation_memory import get_checkpointer_context
from src.messaging.producer import start_producer, stop_producer
from src.messaging.workers import restore_bm25, start_workers, stop_workers

# ──────────────────────────────────────────────────────────────────────────────
# Logging
# ──────────────────────────────────────────────────────────────────────────────

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# Lifespan: open checkpointer, build agent, close on shutdown
# ──────────────────────────────────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up: opening Postgres checkpointer...")

    async with get_checkpointer_context() as checkpointer:
        # Idempotent: creates checkpoint tables if missing.
        await checkpointer.setup()

        model = ChatDeepSeek(
            model=settings.model_name,
            api_key=settings.deepseek_api_key,
            extra_body={"thinking": {"type": "disabled"}},  # Key: disable thinking mode
        )

        app.state.agent = create_agriculture_agent(
            model=model,
            checkpointer=checkpointer,
        )

        logger.info("Agent ready with Postgres checkpointer.")
        app.state.kafka_producer = await start_producer()
        await asyncio.to_thread(restore_bm25)
        workers = start_workers(app)
        try:
            yield
        finally:
            await stop_workers(workers)
            await stop_producer(app.state.kafka_producer)

    logger.info("Shutdown: checkpointer connection closed.")


# ──────────────────────────────────────────────────────────────────────────────
# Application
# ──────────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Agriculture RAG API",
    description="Agricultural question answering using RAG, Pinecone, and LangGraph.",
    version="2.0.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(ingest_router)

# ──────────────────────────────────────────────────────────────────────────────
# Schemas
# ──────────────────────────────────────────────────────────────────────────────


class ChatRequest(BaseModel):
    question: str
    thread_id: UUID


def _sse(payload: dict) -> str:
    """Format one Server-Sent Event frame (wire format unchanged)."""
    return f"data: {json.dumps(payload)}\n\n"


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


@app.get("/health")
async def health(req: Request):
    return {
        "status": "ok",
        "agent": hasattr(req.app.state, "agent"),
        "kafka": req.app.state.kafka_producer is not None,
    }


# ──────────────────────────────────────────────────────────────────────────────
# Non-streaming chat
# ──────────────────────────────────────────────────────────────────────────────


@app.post("/chat")
async def chat(request: ChatRequest, req: Request):
    """
    Process an agricultural question and return the complete response.
    Conversation memory is maintained using thread_id.
    """
    try:
        response = await invoke_response(
            req.app.state.agent,
            request.question,
            str(request.thread_id),
        )
        return {
            "status": "success",
            "response": response,
        }

    except Exception as e:
        logger.error("Chat request failed: %s", e, exc_info=True)
        return {
            "status": "error",
            "detail": str(e),
        }


# ──────────────────────────────────────────────────────────────────────────────
# Streaming chat
# ──────────────────────────────────────────────────────────────────────────────


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest, req: Request):
    """
    Stream the agent response using Server-Sent Events (SSE).
    """

    async def generate():
        try:
            yield _sse({"type": "status", "content": "Thinking..."})

            async for text in stream_response(
                req.app.state.agent,
                request.question,
                str(request.thread_id),
            ):
                yield _sse({"type": "token", "content": text})

            yield _sse({"type": "done"})

        except Exception as e:
            logger.error("Streaming request failed: %s", e, exc_info=True)
            yield _sse({"type": "error", "error": str(e)})

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
