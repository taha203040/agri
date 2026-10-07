from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-en-v1.5",
)


soil_vectorstore = Chroma(
    collection_name="soil_collection",
    persist_directory="./chroma_soil_db",
    embedding_function=embeddings,
)


disease_vectorstore = Chroma(
    collection_name="disease_collection",
    persist_directory="./chroma_disease_db",
    embedding_function=embeddings,
)


water_vectorstore = Chroma(
    collection_name="water_collection",
    persist_directory="./chroma_water_db",
    embedding_function=embeddings,
)


yield_vectorstore = Chroma(
    collection_name="yield_collection",
    persist_directory="./chroma_yield_db",
    embedding_function=embeddings,
)