import re

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
MAX_SECTION = 1500  # an entry up to this size stays as ONE chunk

# Heading block:  =====\nTITLE\n=====   -> starts a new entry
_HEADING_START = re.compile(r"(?m)^(?=[=]{5,}[ \t]*\n[^\n=]+\n[=]{5,}[ \t]*$)")
_TITLE = re.compile(r"\A[=]{5,}[ \t]*\n([^\n=]+)\n[=]{5,}")

_fallback = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
)


def split_documents(documents):
    chunks: list[Document] = []

    for doc in documents:
        text = doc.page_content.replace("\r\n", "\n")
        sections = [s.strip() for s in _HEADING_START.split(text) if s.strip()]

        # No headings (plain prose, PDFs): old behavior
        if len(sections) <= 1:
            chunks.extend(_fallback.split_documents([doc]))
            continue

        for section in sections:
            meta = dict(doc.metadata)
            match = _TITLE.match(section)
            if match:
                meta["section"] = match.group(1).strip()

            piece = Document(page_content=section, metadata=meta)
            if len(section) <= MAX_SECTION:
                chunks.append(piece)
            else:
                chunks.extend(_fallback.split_documents([piece]))

    return chunks
