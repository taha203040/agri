#implement retriverl funciton
from langchain_core.tools import create_retriever_tool
# from src.vctrstr..faiss_index.vctrstr import vectorstore
from src.vectorstore.faiss_index.vctrstr import vectorstore , vectorstr_d
retriever_tool = create_retriever_tool(
        name='soil_retriever'
        ,
        description="Retrieve detailed soil sample information for farmers"
        ,
        retriever=vectorstore.as_retriever(kwargs=5)
    )
diseases_tool = create_retriever_tool(
    name='disease_retriever',
    description='Disease detection for fruits or vegetables'
    ,retriever=vectorstr_d.as_retriever(kwargs=5)
    )
