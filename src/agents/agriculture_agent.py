from langchain.agents import   create_agent
from src.retrieval.retriever import retriever_tool
from dotenv import load_dotenv
load_dotenv()
agent = create_agent(    
    model='deepseek-chat',
    tools=[retriever_tool],
    system_prompt='you are helpful assistant specialzed in agriculture field answer just the questions that related with soil sample using the soil_retriever tool'
)
question = {'messages': [{'role': 'user', 'content': 'how soil sample help to grow planets and increase the amount of the farming ?'}]}
answer = agent.invoke(question)
# print('answr',answer['messages'].content)
# print('answer',answer['messages'].content)
ai_messages = [msg.content for msg in answer['messages'] if msg.__class__.__name__ == 'AIMessage']
for i, msg in enumerate(ai_messages, 1):
    print(f"AI message {i}: {msg}")