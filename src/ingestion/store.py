"""File-based document metadata and chunk storage shared by the API and the workers."""

import json
import os
from collections.abc import Iterator
from datetime import datetime, timezone
from pathlib import Path

from langchain_core.documents import Document

from src.config.settings import settings


def upload_root() -> Path:
    return Path(settings.upload_dir)


def _meta_path(doc_id: str) -> Path:
    return upload_root() / "meta" / f"{doc_id}.json"


def _chunks_path(doc_id: str) -> Path:
    return upload_root() / "chunks" / f"{doc_id}.jsonl"


def update_status(doc_id: str, **fields) -> dict:
    """Merge `fields` (e.g. status="indexed", chunk_count=12) into the document's metadata."""
    path = _meta_path(doc_id)
    record = json.loads(path.read_text(encoding="utf-8"))
    record.update(fields)
    record["updated_at"] = datetime.now(timezone.utc).isoformat()
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(record, indent=2), encoding="utf-8")
    os.replace(tmp, path)
    return record


def indexed_records() -> Iterator[dict]:
    meta_dir = upload_root() / "meta"
    if not meta_dir.exists():
        return
    for path in meta_dir.glob("*.json"):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if record.get("status") == "indexed":
            yield record


def write_chunks(doc_id: str, chunks: list[Document]) -> None:
    path = _chunks_path(doc_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps({"page_content": c.page_content, "metadata": c.metadata}) + "\n")
    os.replace(tmp, path)


def read_chunks(doc_id: str) -> list[Document]:
    path = _chunks_path(doc_id)
    chunks: list[Document] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            row = json.loads(line)
            chunks.append(Document(page_content=row["page_content"], metadata=row["metadata"]))
    return chunks
