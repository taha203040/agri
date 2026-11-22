"""
Client-facing document upload — step 1 of the ingestion pipeline.

Status lifecycle (only "received" exists today; later steps add the rest):
    received -> queued -> processing -> indexed | failed
"""

import hashlib
import json
import logging
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated, Literal

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from pydantic import BaseModel

from src.config.settings import settings
from src.messaging.producer import publish_document

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ingest", tags=["ingestion"])

Topic = Literal["soil", "disease", "water", "crop_health", "yield"]

# Keep in sync with HANDLERS in src/ingestion/loader.py
ALLOWED_EXTENSIONS = {".txt", ".md", ".pdf", ".docx", ".html", ".htm"}

CHUNK_SIZE = 1024 * 1024  # 1 MB
DOC_ID_RE = re.compile(r"^[a-f0-9]{32}$")


class IngestResponse(BaseModel):
    doc_id: str
    filename: str
    topic: Topic
    size_bytes: int
    sha256: str
    status: str
    created_at: str
    duplicate: bool = False
    chunk_count: int | None = None
    error: str | None = None


def _dirs() -> tuple[Path, Path, Path]:
    root = Path(settings.upload_dir)
    files_dir, meta_dir, tmp_dir = root / "files", root / "meta", root / "tmp"
    for d in (files_dir, meta_dir, tmp_dir):
        d.mkdir(parents=True, exist_ok=True)
    return files_dir, meta_dir, tmp_dir


def _write_json_atomic(path: Path, data: dict) -> None:
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    os.replace(tmp, path)


def _looks_valid(ext: str, head: bytes) -> bool:
    """Cheap content check so a renamed binary isn't accepted as a document."""
    if ext == ".pdf":
        return head.startswith(b"%PDF-")
    if ext == ".docx":
        return head.startswith(b"PK\x03\x04")
    return b"\x00" not in head  # text formats must not contain NUL bytes


async def _queue(request: Request, record: dict, meta_path: Path) -> None:
    """Publish to Kafka and mark 'queued'. If Kafka is unavailable the document stays 'received'."""
    stored_as = record.get("stored_as") or (
        f"{record['doc_id']}{Path(record['filename']).suffix.lower()}"
    )
    message = {
        "schema_version": 1,
        "doc_id": record["doc_id"],
        "filename": record["filename"],
        "topic": record["topic"],
        "stored_as": f"files/{stored_as}",
        "sha256": record["sha256"],
        "size_bytes": record["size_bytes"],
        "attempt": 0,
        "submitted_at": record["created_at"],
    }
    producer = getattr(request.app.state, "kafka_producer", None)
    if await publish_document(producer, message):
        # The worker may already have advanced the status; only move received -> queued.
        current = json.loads(meta_path.read_text(encoding="utf-8"))
        if current["status"] == "received":
            current["status"] = "queued"
            _write_json_atomic(meta_path, current)
        record["status"] = current["status"]


@router.post("", response_model=IngestResponse)
async def upload_document(
    request: Request,
    file: Annotated[UploadFile, File()],
    topic: Annotated[Topic, Form()],
):
    original_name = Path(file.filename or "").name[:200]
    ext = Path(original_name).suffix.lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type '{ext or 'none'}'. "
                   f"Allowed: {sorted(ALLOWED_EXTENSIONS)}",
        )

    files_dir, meta_dir, tmp_dir = _dirs()
    max_bytes = settings.max_upload_mb * 1024 * 1024

    content_hash = hashlib.sha256()
    size = 0
    head = b""

    fd, tmp_name = tempfile.mkstemp(dir=tmp_dir)
    tmp_path = Path(tmp_name)

    try:
        with os.fdopen(fd, "wb") as out:
            while chunk := await file.read(CHUNK_SIZE):
                if not head:
                    head = chunk[:8192]
                size += len(chunk)
                if size > max_bytes:
                    raise HTTPException(
                        status_code=413,
                        detail=f"File too large (max {settings.max_upload_mb} MB).",
                    )
                content_hash.update(chunk)
                out.write(chunk)

        if size == 0:
            raise HTTPException(status_code=400, detail="Empty file.")
        if not _looks_valid(ext, head):
            raise HTTPException(
                status_code=400,
                detail="File content does not match its extension.",
            )

        sha256 = content_hash.hexdigest()
        # Stable ID: same content + same topic -> same doc_id. Uploading a file
        # twice is therefore idempotent, and later steps (Kafka message,
        # Chroma chunk IDs) can reuse this ID safely.
        doc_id = hashlib.sha256(f"{sha256}:{topic}".encode()).hexdigest()[:32]
        meta_path = meta_dir / f"{doc_id}.json"

        if meta_path.exists():
            existing = json.loads(meta_path.read_text(encoding="utf-8"))
            if existing["status"] == "received":  # stored earlier but never queued
                await _queue(request, existing, meta_path)
            return IngestResponse(**existing, duplicate=True)

        os.replace(tmp_path, files_dir / f"{doc_id}{ext}")

        record = {
            "doc_id": doc_id,
            "stored_as": f"{doc_id}{ext}",
            "filename": original_name,
            "topic": topic,
            "size_bytes": size,
            "sha256": sha256,
            "status": "received",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        _write_json_atomic(meta_path, record)
        await _queue(request, record, meta_path)
    finally:
        tmp_path.unlink(missing_ok=True)

    logger.info("Document received: id=%s topic=%s size=%d", doc_id, topic, size)
    return IngestResponse(**record, duplicate=False)


@router.get("/{doc_id}", response_model=IngestResponse)
async def get_document(doc_id: str):
    if not DOC_ID_RE.fullmatch(doc_id):
        raise HTTPException(status_code=400, detail="Invalid document id.")

    _, meta_dir, _ = _dirs()
    meta_path = meta_dir / f"{doc_id}.json"

    if not meta_path.exists():
        raise HTTPException(status_code=404, detail="Document not found.")

    return IngestResponse(**json.loads(meta_path.read_text(encoding="utf-8")))
