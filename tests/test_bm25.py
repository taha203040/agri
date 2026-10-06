from langchain_community.retrievers import BM25Retriever

from src.ingestion.loader import load_documents


def test_water_bm25():
    water_docs = load_documents("data/raw/water")

    retriever = BM25Retriever.from_documents(water_docs)
    retriever.k = 5

    query = "How much water does a crop need during the growing season?"

    results = retriever.invoke(query)

    print(f"\nDocuments loaded: {len(water_docs)}")
    print(f"Results returned: {len(results)}")

    for i, doc in enumerate(results, start=1):
        print(f"\n--- Result {i} ---")
        print(f"Characters: {len(doc.page_content)}")
        print(doc.page_content[:500])

    assert len(results) == 5