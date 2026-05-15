# tools for 
# search causes for each disease for 
# search about soil sample 

from langchain_core.tools import tool
import logging
logger = logging.getLogger(__name__)
@tool('cause_disease', description='Provide information about the causes of diseases of plants and discover solutions')
def srch_disease ()->str:
    logger.info(f">>> diseases_tool called")
    with open('data/raw/diseases/data.txt' ,'r',encoding='utf-8') as f :
        return f.read() 
    # toolss = create_retriever_tool(retriever=)

@tool('soil_sampling',description=("Provides information about soil samples. ""Answers farmers' questions about soil analysis, type, nutrient content, " "and improvement methods."))
def soil_search() -> str:
    logger.info(f">>> soil_retriever called ")
    with open("data/raw/agriculture_books/data.txt", "r", encoding="utf-8") as f:
        return f.read()
