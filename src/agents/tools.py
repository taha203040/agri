# tools for 
# search causes for each disease for 
# search about soil sample 

from langchain_core.tools import tool

@tool('cause_disease')
def srch_disease ()->str:
    """
    search raw disease information
    """
    with open('/data/raw/diseases' , 'r',encoding='utf-8') as f :
        return f.read()
    # toolss = create_retriever_tool(retriever=)

@tool('soil_sampling',description=("Provides information about soil samples. ""Answers farmers' questions about soil analysis, type, nutrient content, " "and improvement methods."))
def soil_search() -> str:
     with open("data/raw/agriculture_books/data.txt", "r", encoding="utf-8") as f:
        return f.read()
