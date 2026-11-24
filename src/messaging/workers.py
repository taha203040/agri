"""
In-process Kafka workers.

    agri.docs.raw --[chunker]--> agri.docs.chunked --[indexer]--> Chroma + BM25
          failures after retries (either stage) --> agri.docs.dlq

Status lifecycle: queued -> chunking -> chunked -> embedding -> indexed | failed
Delivery is at-least-once: an offset is committed only after a message has been
handled, and every write is idempotent (stable doc_id and chunk ids).
"""
import threading
import asyncio
import contextlib
import json
import logging
from collections import defaultdict
from collections.abc import Awaitable, Callable
from datetime import datetime, timezone
from typing import Any

from aiokafka import AIOKafkaConsumer
from fastapi import FastAPI
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from langsmith import traceable

from src.config.settings import settings
from src.ingestion import store
from src.ingestion.loader import HANDLERS
from src.ingestion.splitter import split_documents
from src.messaging.producer import publish_message
from src.retrieval.assembler import (
    disease_hybrid,
    soil_hybrid,
    water_hybrid,
    yield_hybrid,
)
from src.vectorstore.vector import (
    disease_vectorstore,
    soil_vectorstore,
    water_vectorstore,
    yield_vectorstore,
)

logger = logging.getLogger(__name__)

MAX_ATTEMPTS = 3

# crop_health has no collection of its own; it shares the disease one (as in retriever.py).
VECTORSTORES = {
    "soil": soil_vectorstore,
    "disease": disease_vectorstore,
    "crop_health": disease_vectorstore,
    "water": water_vectorstore,
    "yield": yield_vectorstore,
}
# Each EnsembleRetriever was built as [bm25, vector], so retrievers[0] is the BM25 side.
HYBRIDS = {
    "soil": soil_hybrid,
    "disease": disease_hybrid,
    "crop_health": disease_hybrid,
    "water": water_hybrid,
    "yield": yield_hybrid,
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clean_metadata(md: dict) -> dict:
    """Chroma only accepts str/int/float/bool metadata values."""
    return {k: v for k, v in md.items() if isinstance(v, (str, int, float, bool))}


def _safe_status(doc_id: str | None, **fields) -> None:
    if not doc_id:
        return
    try:
        store.update_status(doc_id, **fields)
    except Exception as e:  # metadata file missing/corrupt must not kill the worker
        logger.warning("Could not update status for %s: %s", doc_id, e)


# ── BM25 (keyword side of the hybrid retrievers) ─────────────────────────────

def _merge_into_bm25(topic: str, by_doc: dict[str, list[Document]]) -> None:
    """Add/replace these documents' chunks in the topic's BM25 retriever."""
    hybrid = HYBRIDS[topic]
    old: BM25Retriever = hybrid.retrievers[0]
    kept = [d for d in old.docs if d.metadata.get("doc_id") not in by_doc]
    merged = kept + [c for chunks in by_doc.values() for c in chunks]
    rebuilt = BM25Retriever.from_documents(
        merged, k=old.k, preprocess_func=old.preprocess_func
    )
    # One atomic list-item swap, so concurrent queries never see a half-updated retriever.
    hybrid.retrievers[0] = rebuilt


def restore_bm25() -> None:
    """On startup, put already-indexed uploads back into BM25 (it is in-memory only)."""
    by_topic: dict[str, dict[str, list[Document]]] = defaultdict(dict)
    for record in store.indexed_records():
        try:
            by_topic[record["topic"]][record["doc_id"]] = store.read_chunks(record["doc_id"])
        except Exception as e:
            logger.warning("Skipping BM25 restore for %s: %s", record.get("doc_id"), e)
    for topic, by_doc in by_topic.items():
        _merge_into_bm25(topic, by_doc)
        logger.info("BM25 restored for '%s': %d uploaded document(s)", topic, len(by_doc))


# ── Stage 1: chunk ───────────────────────────────────────────────────────────

@traceable(name="chunk_document", run_type="chain")
def _chunk(msg: dict) -> int:
    path = store.upload_root() / msg["stored_as"]
    handler = HANDLERS.get(path.suffix.lower())
    if handler is None:
        raise ValueError(f"Unsupported file type '{path.suffix}'")

    documents = handler(path)
    if not documents:
        raise ValueError("No text could be extracted (empty, scanned or unreadable file)")

    chunks = split_documents(documents)
    for i, chunk in enumerate(chunks):
        chunk.metadata = _clean_metadata({
            **chunk.metadata,
            "doc_id": msg["doc_id"],
            "chunk": i,
            "topic": msg["topic"],
            "filename": msg["filename"],
        })
    store.write_chunks(msg["doc_id"], chunks)
    return len(chunks)


async def _stage_chunk(app: FastAPI, msg: dict) -> None:
    doc_id = msg["doc_id"]
    store.update_status(doc_id, status="chunking", error=None)

    count = await asyncio.to_thread(_chunk, msg)
    store.update_status(doc_id, status="chunked", chunk_count=count)

    next_msg = {**msg, "chunk_count": count, "attempt": 0}
    if not await publish_message(
        app.state.kafka_producer, settings.kafka_topic_chunked, doc_id, next_msg
    ):
        raise RuntimeError("Could not publish to the chunked topic")


# ── Stage 2: embed + store ───────────────────────────────────────────────────

CHROMA_LOCK = threading.Lock()

@traceable(name="index_document", run_type="chain")
def _index(msg: dict) -> int:
    doc_id, topic = msg["doc_id"], msg["topic"]
    chunks = store.read_chunks(doc_id)

    if not chunks:
        raise ValueError(f"No chunks for {doc_id}")

    ids = [f"{doc_id}:{c.metadata['chunk']}" for c in chunks]

    with CHROMA_LOCK:
        VECTORSTORES[topic].add_documents(chunks, ids=ids)

    _merge_into_bm25(topic, {doc_id: chunks})
    return len(chunks)

async def _stage_index(app: FastAPI, msg: dict) -> None:
    doc_id = msg["doc_id"]
    store.update_status(doc_id, status="embedding")

    count = await asyncio.to_thread(_index, msg)
    store.update_status(doc_id, status="indexed", chunk_count=count, indexed_at=_now())
    logger.info("Indexed document %s (%d chunks, topic=%s)", doc_id, count, msg["topic"])


# ── Retry / dead-letter handling ─────────────────────────────────────────────

async def _handle_failure(
    app: FastAPI, stage: str, in_topic: str, msg: dict, err: Exception
) -> None:
    doc_id = msg.get("doc_id")
    attempt = int(msg.get("attempt", 0))
    permanent = isinstance(err, ValueError)  # bad input: retrying cannot help
    producer = app.state.kafka_producer

    logger.error(
        "stage=%s doc_id=%s attempt=%d failed: %s", stage, doc_id, attempt, err,
        exc_info=not permanent,
    )

    if not permanent and attempt + 1 < MAX_ATTEMPTS:
        await asyncio.sleep(2 ** attempt)  # 1s, then 2s
        if await publish_message(producer, in_topic, doc_id or "unknown",
                                 {**msg, "attempt": attempt + 1}):
            return

    dlq = {**msg, "stage": stage, "error": str(err)[:500], "failed_at": _now()}
    await publish_message(producer, settings.kafka_topic_dlq, doc_id or "unknown", dlq)
    _safe_status(doc_id, status="failed", error=f"{stage}: {str(err)[:300]}")


# ── Consumer loop ────────────────────────────────────────────────────────────

def _loads(raw: bytes) -> dict:
    try:
        value = json.loads(raw.decode("utf-8"))
        return value if isinstance(value, dict) else {}
    except Exception:
        return {}


async def _consume(
    app: FastAPI,
    stage: str,
    in_topic: str,
    group: str,
    process: Callable[[FastAPI, dict], Awaitable[None]],
) -> None:
    while True:
        consumer = AIOKafkaConsumer(
            in_topic,
            bootstrap_servers=settings.kafka_bootstrap_servers,
            group_id=group,
            enable_auto_commit=False,
            auto_offset_reset="earliest",
            max_poll_interval_ms=900_000,  # large PDFs can take minutes
            value_deserializer=_loads,
        )
        try:
            await consumer.start()
            logger.info("Worker '%s' listening on %s", stage, in_topic)
            async for record in consumer:
                msg: dict[str, Any] = record.value
                try:
                    await process(app, msg)
                except asyncio.CancelledError:
                    raise
                except Exception as e:
                    await _handle_failure(app, stage, in_topic, msg, e)
                await consumer.commit()
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Worker '%s' crashed; restarting in 5s", stage)
            await asyncio.sleep(5)
        finally:
            with contextlib.suppress(Exception):
                await consumer.stop()


def start_workers(app: FastAPI) -> list[asyncio.Task]:
    if getattr(app.state, "kafka_producer", None) is None:
        logger.warning("Kafka not connected: ingestion workers not started.")
        return []
    return [
        asyncio.create_task(
            _consume(app, "chunker", settings.kafka_topic_raw, "agri-chunker", _stage_chunk),
            name="agri-chunker",
        ),
        asyncio.create_task(
            _consume(app, "indexer", settings.kafka_topic_chunked, "agri-indexer", _stage_index),
            name="agri-indexer",
        ),
    ]


async def stop_workers(tasks: list[asyncio.Task]) -> None:
    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)
