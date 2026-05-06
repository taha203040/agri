# # src/agent/agriculture_agent.py
# from langchain.agents import create_agent
# from src.retrieval.retriever import retriever_tool, diseases_tool
# from dotenv import load_dotenv
# import json

# load_dotenv()

# class AgricultureAgent:
#     """Agriculture Agent wrapper for handling farming-related queries"""
    
#     def __init__(self):
#         self.agent = create_agent(
#             model='deepseek-chat',
#             tools=[retriever_tool, diseases_tool],
#             system_prompt='You are a helpful assistant specialized in the agriculture field. Answer just the questions related to soil samples using the soil_retriever tool and diseases using the disease_retriever tool.'
#         )
    
#     def stream(self, question_input):
#         """Stream agent responses"""
#         for chunk in self.agent.stream(question_input):
#             yield chunk
    
#     def invoke(self, question_input):
#         """Invoke agent without streaming"""
#         return self.agent.invoke(question_input)
    
#     def run(self, question: str):
#         """Run agent and return AI messages"""
#         question_input = {'messages': [{'role': 'user', 'content': question}]}
#         answer = self.agent.invoke(question_input)
#         ai_messages = [msg.content for msg in answer['messages'] 
#                       if msg.__class__.__name__ == 'AIMessage']
        
#         for i, msg in enumerate(ai_messages, 1):
#             print(f"AI message {i}: {msg}")
        
#         return ai_messages

# # Create a singleton instance for reuse
# agriculture_agent = AgricultureAgent()
# src/agents/agriculture_agent.py
from langchain.agents import create_agent
from src.retrieval.retriever import retriever_tool, diseases_tool
from dotenv import load_dotenv
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class AgricultureAgent:
    """Agriculture Agent wrapper for handling farming-related queries"""
    
    def __init__(self):
        self.agent = create_agent(
            model='deepseek-chat',
            tools=[retriever_tool, diseases_tool],
            system_prompt='You are a helpful assistant specialized in the agriculture field. Answer just the questions related to soil samples using the soil_retriever tool and diseases using the disease_retriever tool.'
        )
    
    def stream(self, question_input):
        """Stream agent responses with proper chunk formatting"""
        try:
            # Check if the agent has a stream method
            if hasattr(self.agent, 'stream'):
                for chunk in self.agent.stream(question_input):
                    logger.info(f"Raw chunk from agent: {chunk}")
                    
                    # Handle different chunk formats
                    if isinstance(chunk, dict):
                        # If it's already a dict, yield as is
                        yield chunk
                    elif hasattr(chunk, 'dict'):
                        # If it's a Pydantic model
                        yield chunk.dict()
                    elif hasattr(chunk, 'content'):
                        # If it's a message object
                        yield {"type": "token", "content": chunk.content}
                    else:
                        # Unknown format, try to convert to string
                        yield {"type": "token", "content": str(chunk)}
            else:
                # If agent doesn't support streaming, simulate it
                logger.warning("Agent doesn't support streaming, simulating...")
                result = self.agent.invoke(question_input)
                
                # Extract content from result
                messages = result.get('messages', [])
                if messages:
                    # Find the AI message
                    for msg in messages:
                        if hasattr(msg, 'type') and msg.type == 'ai' or hasattr(msg, '__class__') and msg.__class__.__name__ == 'AIMessage':
                            content = msg.content if hasattr(msg, 'content') else str(msg)
                            
                            # Stream word by word
                            words = content.split()
                            for i, word in enumerate(words):
                                yield {
                                    "type": "token", 
                                    "content": word + (" " if i < len(words)-1 else "")
                                }
                            break
                
                yield {"type": "done"}
                
        except Exception as e:
            logger.error(f"Stream error: {e}")
            yield {"type": "error", "error": str(e)}
    
    def invoke(self, question_input):
        """Invoke agent without streaming"""
        return self.agent.invoke(question_input)
    
    def run(self, question: str):
        """Run agent and return AI messages"""
        question_input = {'messages': [{'role': 'user', 'content': question}]}
        answer = self.agent.invoke(question_input)
        ai_messages = [msg.content for msg in answer['messages'] 
                      if msg.__class__.__name__ == 'AIMessage']
        
        for i, msg in enumerate(ai_messages, 1):
            logger.info(f"AI message {i}: {msg}")
        
        return ai_messages

# Create a singleton instance for reuse
agriculture_agent = AgricultureAgent()











# from langchain.agents import   create_agent
# from src.retrieval.retriever import retriever_tool , diseases_tool
# from dotenv import load_dotenv
# load_dotenv()
# agent = create_agent(    
#     model='deepseek-chat',
#     tools=[retriever_tool , diseases_tool],
    
#     system_prompt='you are helpful assistant specialzed in agriculture field answer just the questions that related with soil sample using the soil_retriever tool and the diseases using disease_retriever'
# )
# # question = {'messages': [{'role': 'user', 'content': 'how soil sample help to grow planets and increase the amount of the farming ?'}]}
# question = {'messages': [{'role': 'user', 'content': 'what most diseases that tomato get it?'}]}
# answer = agent.invoke(question)
# # print('answr',answer['messages'].content)
# # print('answer',answer['messages'].content)
# ai_messages = [msg.content for msg in answer['messages'] if msg.__class__.__name__ == 'AIMessage']
# for i, msg in enumerate(ai_messages, 1):
#     print(f"AI message {i}: {msg}")

# # from ultralyticsplus import YOLO, render_result

# # import torch
# # from PIL import Image
# # from torchvision import transforms
# # import requests
# # from transformers import AutoModelForImageClassification

# # class AgricultureAgent:
# #     def __init__(self):
# #         self.model_name = "linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification"
# #         self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
# #         # Load model
# #         self.model = AutoModelForImageClassification.from_pretrained(self.model_name)
# #         self.model.to(self.device)
# #         self.model.eval()
        
# #         # Manual preprocessing (since auto processor fails)
# #         self.transform = transforms.Compose([
# #             transforms.Resize((224, 224)),
# #             transforms.ToTensor(),
# #             transforms.Normalize(mean=[0.485, 0.456, 0.406], 
# #                                std=[0.229, 0.224, 0.225])
# #         ])
    
# #     def predict(self, image_path):
# #         # Load and preprocess image
# #         image = Image.open(image_path).convert('RGB')
# #         input_tensor = self.transform(image).unsqueeze(0).to(self.device)
        
# #         # Predict
# #         with torch.no_grad():
# #             outputs = self.model(input_tensor)
# #             probabilities = torch.nn.functional.softmax(outputs.logits, dim=1)
# #             confidence, predicted_idx = torch.max(probabilities, 1)
        
# #         # Get label
# #         predicted_class = self.model.config.id2label[predicted_idx.item()]
# #         confidence_score = confidence.item()
        
# #         return {
# #             "disease": predicted_class,
# #             "confidence": confidence_score,
# #             "all_predictions": [
# #                 {
# #                     "label": self.model.config.id2label[i],
# #                     "score": probabilities[0][i].item()
# #                 }
# #                 for i in range(len(probabilities[0]))
# #             ]
# #         }

# # # Usage
# # if __name__ == "__main__":
# #     agent = AgricultureAgent()
# #     result = agent.predict("./image.png")
# #     print(f"Disease: {result['disease']}")
# #     print(f"Confidence: {result['confidence']:.2%}")