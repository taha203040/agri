from langchain_chroma import Chroma
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction


embedding_function = DefaultEmbeddingFunction()


soil_vectorstore = Chroma(
    collection_name="soil_collection",
    embedding_function=embedding_function,
    persist_directory="./chroma_soil_db",
)


disease_vectorstore = Chroma(
    collection_name="disease_collection",
    embedding_function=embedding_function,
    persist_directory="./chroma_disease_db",
)