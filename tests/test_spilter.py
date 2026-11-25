from langchain_core.documents import Document

from src.ingestion.splitter import split_documents

SAMPLE = """==================================================
CARROT LEAF BLIGHT
==================================================
Host: Carrot.
Pathogen: Alternaria dauci (fungal).

==================================================
CARROT DAMPING-OFF
==================================================
Host: Carrot.
Pathogen: Pythium spp. (oomycete).
"""


def test_one_chunk_per_entry():
    chunks = split_documents([Document(page_content=SAMPLE, metadata={})])
    assert len(chunks) == 2
    assert chunks[0].metadata["section"] == "CARROT LEAF BLIGHT"
    assert "Pythium" not in chunks[0].page_content
