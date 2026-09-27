from src.ingestion.loader import load_documents
from src.ingestion.splitter import split_documents
from src.vectorstore.vector import (
    soil_vectorstore,
    disease_vectorstore,
)


def ingest_soil():
    documents = load_documents("data/raw/agriculture_books")
    chunks = split_documents(documents)

    soil_vectorstore.add_documents(chunks)


def ingest_diseases():
    documents = load_documents("data/raw/diseases")
    chunks = split_documents(documents)

    disease_vectorstore.add_documents(chunks)


if __name__ == "__main__":
    ingest_soil()
    ingest_diseases()