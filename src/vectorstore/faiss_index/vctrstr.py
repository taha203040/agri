from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from src.agents.tools import soil_search , srch_disease
# define vector store function

def build_soil_vectorstore(documents):
    if not documents or not isinstance(documents[0], str):
        raise ValueError("Documents must be a non-empty list of strings")

    embedding = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    return FAISS.from_texts(texts=documents, embedding=embedding)
raw_text = soil_search.invoke({})
docs = [raw_text]
vectorstore = build_soil_vectorstore(docs)

def build_disease_vectorstore (docss) :
    if not docs or not isinstance(docss[0] , str) :
        raise ValueError("Documents must be a non-empty list of strings")
    embedding = HuggingFaceEmbeddings(
        model_name='sentence-transformers/all-MiniLM-L6-v2'
    )
    return FAISS.from_texts(texts=docss , embedding=embedding)

raw_txt_disease = srch_disease.invoke({})
doc_d = [raw_txt_disease]
vectorstr_d = build_disease_vectorstore(doc_d)