from src.ingestion.loader import load_documents
from src.ingestion.splitter import split_documents
from src.vectorstore.vector import (
    soil_vectorstore,
    disease_vectorstore,
    water_vectorstore,
    yield_vectorstore,
)


def ingest_soil():
    documents = load_documents("data/raw/soil")
    chunks = split_documents(documents)
    soil_vectorstore.add_documents(chunks)
    print(f"✅ soil      → {len(chunks)} chunks ingested")


def ingest_diseases():
    documents = load_documents("data/raw/diseases")
    chunks = split_documents(documents)
    disease_vectorstore.add_documents(chunks)
    print(f"✅ disease   → {len(chunks)} chunks ingested")


def ingest_water():
    documents = load_documents("data/raw/water")
    chunks = split_documents(documents)
    water_vectorstore.add_documents(chunks)
    print("✅chunks :", len(chunks))

def ingest_yield():
    documents = load_documents("data/raw/yield")
    chunks = split_documents(documents)
    yield_vectorstore.add_documents(chunks)
    print(f"✅ yield     → {len(chunks)} chunks ingested")


if __name__ == "__main__":
    # ingest_soil()
    ingest_diseases()
    ingest_water()
    ingest_yield()