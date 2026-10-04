from langchain_chroma import Chroma


soil_vectorstore = Chroma(
    collection_name="soil_collection",
    persist_directory="./chroma_soil_db",
)


disease_vectorstore = Chroma(
    collection_name="disease_collection",
    persist_directory="./chroma_disease_db",
)


water_vectorstore = Chroma(
    collection_name="water_collection",
    persist_directory="./chroma_water_db",
)


yield_vectorstore = Chroma(
    collection_name="yield_collection",
    persist_directory="./chroma_yield_db",
)