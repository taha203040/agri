from pathlib import Path

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
)
from langchain_core.documents import Document


def _load_txt(file_path: Path) -> list[Document]:
    try:
        text = file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = file_path.read_text(encoding="latin-1")

    if not text.strip():
        return []

    return [
        Document(
            page_content=text,
            metadata={"source": str(file_path), "type": "txt"},
        )
    ]


def _load_pdf(file_path: Path) -> list[Document]:
    try:
        docs = PyPDFLoader(str(file_path)).load()
    except Exception as e:
        print(f"⚠️  failed to load PDF {file_path}: {e}")
        return []

    for d in docs:
        d.metadata["source"] = str(file_path)
        d.metadata["type"] = "pdf"
    return docs


def _load_md(file_path: Path) -> list[Document]:
    try:
        text = file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = file_path.read_text(encoding="latin-1")

    if not text.strip():
        return []

    return [
        Document(
            page_content=text,
            metadata={"source": str(file_path), "type": "md"},
        )
    ]


def _load_docx(file_path: Path) -> list[Document]:
    try:
        from langchain_community.document_loaders import Docx2txtLoader
        docs = Docx2txtLoader(str(file_path)).load()
    except Exception as e:
        print(f"⚠️  failed to load DOCX {file_path}: {e}")
        return []

    for d in docs:
        d.metadata["source"] = str(file_path)
        d.metadata["type"] = "docx"
    return docs


def _load_html(file_path: Path) -> list[Document]:
    try:
        from langchain_community.document_loaders import UnstructuredHTMLLoader
        docs = UnstructuredHTMLLoader(str(file_path)).load()
    except Exception as e:
        print(f"⚠️  failed to load HTML {file_path}: {e}")
        return []

    for d in docs:
        d.metadata["source"] = str(file_path)
        d.metadata["type"] = "html"
    return docs


HANDLERS = {
    ".txt": _load_txt,
    ".pdf": _load_pdf,
    ".md": _load_md,
    ".docx": _load_docx,
    ".html": _load_html,
    ".htm": _load_html,
}


def load_documents(path: str) -> list[Document]:
    documents: list[Document] = []
    root = Path(path)

    for file_path in root.rglob("*"):
        if not file_path.is_file():
            continue

        ext = file_path.suffix.lower()
        handler = HANDLERS.get(ext)

        if handler is None:
            continue

        documents.extend(handler(file_path))

    return documents