from pathlib import Path
from langchain_core.documents import Document


def load_documents(path: str) -> list[Document]:
    documents = []

    for file_path in Path(path).rglob("*.txt"):
        text = file_path.read_text(encoding="utf-8")

        documents.append(
            Document(
                page_content=text,
                metadata={
                    "source": str(file_path)
                }
            )
        )

    return documents